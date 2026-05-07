"""In-app messaging views — list, thread, send, start.

Real-time delivery is via HTMX 5s polling; Redis/WebSockets per PRD §14
becomes a later upgrade if message volume warrants it.
"""

from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from messaging import services
from messaging.forms import MessageForm
from messaging.models import Conversation
from therapists.models import TherapistProfile, VerificationStatus


def _conversations_for(user):
    return (
        Conversation.objects.filter(Q(user=user) | Q(therapist__user=user))
        .select_related("user", "therapist", "therapist__user")
        .order_by("-last_message_at", "-created_at")
    )


@login_required
def conversation_list(request: HttpRequest) -> HttpResponse:
    convos = list(_conversations_for(request.user))
    for c in convos:
        c.unread_count = c.unread_count_for(request.user)
        c.viewer_is_therapist = c.therapist.user_id == request.user.id
    return render(
        request,
        "messaging/list.html",
        {"conversations": convos},
    )


@login_required
def thread(request: HttpRequest, conversation_id) -> HttpResponse:
    convo = get_object_or_404(
        Conversation.objects.select_related("user", "therapist", "therapist__user"),
        id=conversation_id,
    )
    if not convo.includes(request.user):
        raise PermissionDenied
    services.mark_seen(conversation=convo, viewer=request.user)
    messages = convo.messages.select_related("sender").all()
    return render(
        request,
        "messaging/thread.html",
        {"conversation": convo, "messages": messages, "form": MessageForm()},
    )


@login_required
def thread_messages_partial(request: HttpRequest, conversation_id) -> HttpResponse:
    """HTMX poll endpoint — returns just the message list. Cheaper than full page."""
    convo = get_object_or_404(Conversation, id=conversation_id)
    if not convo.includes(request.user):
        raise PermissionDenied
    services.mark_seen(conversation=convo, viewer=request.user)
    messages = convo.messages.select_related("sender").all()
    return render(
        request,
        "messaging/_messages_partial.html",
        {"conversation": convo, "messages": messages},
    )


@login_required
@require_POST
@ratelimit(key="user", rate="60/h", method="POST", block=True)
def send_message(request: HttpRequest, conversation_id) -> HttpResponse:
    convo = get_object_or_404(Conversation, id=conversation_id)
    if not convo.includes(request.user):
        raise PermissionDenied
    form = MessageForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest(_("Message vide ou trop long."))
    services.post_message(
        conversation=convo, sender=request.user, body=form.cleaned_data["body"]
    )
    if request.headers.get("HX-Request"):
        messages = convo.messages.select_related("sender").all()
        return render(
            request,
            "messaging/_messages_partial.html",
            {"conversation": convo, "messages": messages},
        )
    return redirect("messaging:thread", conversation_id=convo.id)


@login_required
@require_POST
@ratelimit(key="user", rate="20/h", method="POST", block=True)
def start_conversation(request: HttpRequest, therapist_slug: str) -> HttpResponse:
    """Patient-side: open (or reuse) a conversation with an approved therapist."""
    therapist = get_object_or_404(
        TherapistProfile,
        slug=therapist_slug,
        verification_status=VerificationStatus.APPROVED,
    )
    try:
        convo = services.get_or_create_conversation(
            user=request.user, therapist=therapist
        )
    except PermissionDenied as exc:
        return HttpResponseBadRequest(str(exc))
    return redirect("messaging:thread", conversation_id=convo.id)
