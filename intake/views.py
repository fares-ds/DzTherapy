"""AI intake assistant views.

Anonymous + authenticated visitors can use the assistant. We persist the
session in the DB; for anonymous users the session id lives in the URL +
Django session cookie so they can refresh without losing context.
"""

from __future__ import annotations

import re

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from intake import services
from intake.models import IntakeSession


def _recommendation_block(text: str) -> str:
    """Strip the `<recommend>...</recommend>` block from a message body."""
    return re.sub(r"<recommend>.*?</recommend>", "", text, flags=re.DOTALL).strip()


def _ensure_session(request: HttpRequest) -> IntakeSession:
    sid = request.session.get("intake_session_id")
    if sid:
        try:
            return IntakeSession.objects.get(id=sid)
        except IntakeSession.DoesNotExist:
            pass
    session = IntakeSession.objects.create(
        user=request.user if request.user.is_authenticated else None
    )
    request.session["intake_session_id"] = str(session.id)
    return session


def start(request: HttpRequest) -> HttpResponse:
    session = _ensure_session(request)
    if not session.messages:
        # Seed with the greeting so the page has something to show.
        first = services.reply([])
        session.append("assistant", first)
        session.save(update_fields=["messages", "updated_at"])
    return redirect("intake:thread", session_id=session.id)


def _displayable(messages: list[dict]) -> list[dict]:
    """Strip `<recommend>...</recommend>` from assistant messages for display."""
    out = []
    for m in messages or []:
        content = m.get("content", "") or ""
        if m.get("role") == "assistant":
            content = _recommendation_block(content)
        out.append({"role": m.get("role"), "content": content})
    return out


def thread(request: HttpRequest, session_id) -> HttpResponse:
    session = get_object_or_404(IntakeSession, id=session_id)
    if session.user_id and (
        not request.user.is_authenticated or session.user_id != request.user.id
    ):
        return redirect("intake:start")
    recommended = services.filter_recommended_therapists(
        session.recommended_therapist_slugs or []
    )
    return render(
        request,
        "intake/thread.html",
        {
            "session": session,
            "messages": _displayable(session.messages),
            "recommended": recommended,
            "ai_enabled": services.is_enabled(),
        },
    )


@require_POST
@ratelimit(key="ip", rate="20/h", method="POST", block=True)
def reply_view(request: HttpRequest, session_id) -> HttpResponse:
    session = get_object_or_404(IntakeSession, id=session_id)
    body = (request.POST.get("body") or "").strip()
    if not body:
        return redirect("intake:thread", session_id=session.id)

    session.append("user", body)
    session.save(update_fields=["messages", "updated_at"])

    raw_reply = services.reply(session.messages)
    slugs = services.extract_recommended_slugs(raw_reply)
    if slugs:
        valid = [t.slug for t in services.filter_recommended_therapists(slugs)]
        if valid:
            session.recommended_therapist_slugs = valid
            session.completed = True

    session.append("assistant", raw_reply)
    session.save(
        update_fields=[
            "messages",
            "recommended_therapist_slugs",
            "completed",
            "updated_at",
        ]
    )

    if request.headers.get("HX-Request"):
        recommended = services.filter_recommended_therapists(
            session.recommended_therapist_slugs or []
        )
        return render(
            request,
            "intake/_thread_swap.html",
            {
                "session": session,
                "messages": _displayable(session.messages),
                "recommended": recommended,
            },
        )
    return redirect("intake:thread", session_id=session.id)


def crisis_notice(request: HttpRequest) -> HttpResponse:
    """Standalone crisis-line page; linked from the assistant footer."""
    return render(
        request,
        "intake/crisis.html",
        {
            "crisis_lines": [
                ("SOS Algérie", "0560 001 555"),
                ("SAMU", "115"),
                (_("Numéro d'urgence général"), "14"),
            ]
        },
    )
