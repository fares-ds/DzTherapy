"""Transactional email — Resend HTTP API in prod, console backend in dev.

Failures are always logged but never raised; an email outage must not block
a booking transition. Operators inspect Sentry / logs for failures.
"""

from __future__ import annotations

import logging

import requests
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

log = logging.getLogger(__name__)


def send(to: str, subject: str, template: str, context: dict) -> bool:
    """Render a template pair (`{template}.txt` + `{template}.html`) and send."""
    try:
        body_text = render_to_string(f"emails/{template}.txt", context)
        body_html = render_to_string(f"emails/{template}.html", context)
    except Exception:
        log.exception("Email template render failed (template=%s)", template)
        return False

    if settings.RESEND_API_KEY:
        return _send_via_resend(to, subject, body_text, body_html)
    return _send_via_django(to, subject, body_text, body_html)


def _send_via_resend(to: str, subject: str, text: str, html: str) -> bool:
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": settings.DEFAULT_FROM_EMAIL,
                "to": [to],
                "subject": subject,
                "html": html,
                "text": text,
            },
            timeout=10,
        )
        response.raise_for_status()
        return True
    except Exception:
        log.exception("Resend send failed (to=%s subject=%s)", to, subject)
        return False


def _send_via_django(to: str, subject: str, text: str, html: str) -> bool:
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to],
        )
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=False)
        return True
    except Exception:
        log.exception("Django email send failed (to=%s subject=%s)", to, subject)
        return False


# Booking lifecycle helpers — keep call-sites readable.


def send_booking_submitted(booking) -> None:
    send(
        to=booking.therapist.user.email,
        subject="Nouvelle demande de séance",
        template="booking_submitted",
        context={"booking": booking},
    )


def send_payment_marked(booking) -> None:
    send(
        to=booking.therapist.user.email,
        subject="Paiement signalé par votre patient·e",
        template="payment_marked",
        context={"booking": booking},
    )


def send_booking_confirmed(booking) -> None:
    ctx = {"booking": booking}
    # User
    send(
        to=booking.user.email,
        subject="Votre séance est confirmée",
        template="booking_confirmed",
        context=ctx,
    )
    # Therapist
    send(
        to=booking.therapist.user.email,
        subject="Séance confirmée",
        template="booking_confirmed",
        context=ctx,
    )


def send_booking_declined(booking) -> None:
    """Therapist declined — notify the user."""
    send(
        to=booking.user.email,
        subject="Votre demande de séance n'a pas pu être confirmée",
        template="booking_declined",
        context={"booking": booking},
    )


def send_booking_cancelled_by_user(booking) -> None:
    """User cancelled — notify the therapist."""
    send(
        to=booking.therapist.user.email,
        subject="Séance annulée par le ou la patient·e",
        template="booking_cancelled_by_user",
        context={"booking": booking},
    )


def send_session_reminder(booking) -> None:
    """T-24h reminder to both parties."""
    ctx = {"booking": booking}
    send(
        to=booking.user.email,
        subject="Rappel : votre séance demain",
        template="session_reminder",
        context=ctx,
    )
    send(
        to=booking.therapist.user.email,
        subject="Rappel : séance demain",
        template="session_reminder",
        context=ctx,
    )
