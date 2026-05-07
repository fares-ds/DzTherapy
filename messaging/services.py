"""Authorization + lifecycle helpers for messaging."""

from __future__ import annotations

from datetime import timedelta

from django.core.exceptions import PermissionDenied
from django.utils import timezone

from accounts.models import UserRole
from bookings.models import Booking
from messaging.models import Conversation, Message
from notifications import email as notify
from therapists.models import TherapistProfile, VerificationStatus

# If the recipient was online inside this window, skip the email — they'll
# see the message in-app on next render. Avoids notification spam during
# active back-and-forth.
EMAIL_THROTTLE = timedelta(minutes=30)


def get_or_create_conversation(*, user, therapist: TherapistProfile) -> Conversation:
    """Patient-side starter. Errors if the user isn't allowed to start one."""
    if user.role != UserRole.END_USER:
        raise PermissionDenied(
            "Only end users can initiate conversations from the patient side."
        )
    if therapist.verification_status != VerificationStatus.APPROVED:
        raise PermissionDenied("Cannot message an unapproved therapist.")
    convo, _ = Conversation.objects.get_or_create(user=user, therapist=therapist)
    return convo


def therapist_can_initiate(*, therapist: TherapistProfile, target_user) -> bool:
    """A therapist may DM only patients who have an existing booking with them."""
    return Booking.objects.filter(therapist=therapist, user=target_user).exists()


def get_or_create_conversation_for_therapist(
    *, therapist: TherapistProfile, target_user
) -> Conversation:
    if not therapist_can_initiate(therapist=therapist, target_user=target_user):
        raise PermissionDenied("No existing booking with this user.")
    convo, _ = Conversation.objects.get_or_create(user=target_user, therapist=therapist)
    return convo


def post_message(*, conversation: Conversation, sender, body: str) -> Message:
    """Persist a message and notify the recipient if they've been away."""
    if not conversation.includes(sender):
        raise PermissionDenied("Sender is not a participant in this conversation.")
    body = body.strip()
    if not body:
        raise ValueError("Empty messages are not allowed.")
    message = Message.objects.create(
        conversation=conversation, sender=sender, body=body
    )
    now = timezone.now()
    conversation.last_message_at = now
    conversation.save(update_fields=["last_message_at"])

    _maybe_notify(message)
    return message


def mark_seen(*, conversation: Conversation, viewer) -> None:
    """Stamp the viewer's last_seen so future emails throttle correctly."""
    now = timezone.now()
    if viewer.id == conversation.user_id:
        conversation.last_seen_by_user_at = now
        conversation.save(update_fields=["last_seen_by_user_at"])
    elif viewer.id == conversation.therapist.user_id:
        conversation.last_seen_by_therapist_at = now
        conversation.save(update_fields=["last_seen_by_therapist_at"])


def _maybe_notify(message: Message) -> None:
    """Send email to recipient unless they were online inside EMAIL_THROTTLE."""
    convo = message.conversation
    recipient = convo.other_party(message.sender)
    last_seen = (
        convo.last_seen_by_user_at
        if recipient.id == convo.user_id
        else convo.last_seen_by_therapist_at
    )
    now = timezone.now()
    if last_seen and (now - last_seen) < EMAIL_THROTTLE:
        return
    notify.send_new_message(message)
    message.notified_at = now
    message.save(update_fields=["notified_at"])
