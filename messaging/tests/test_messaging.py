"""Messaging — model, services, views, isolation, email throttling."""

from datetime import timedelta
from unittest.mock import patch

import pytest
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils import timezone

from accounts.models import UserRole
from bookings.models import Booking, BookingState
from core.factories import UserFactory
from messaging import services
from messaging.models import Conversation, Message
from therapists.models import VerificationStatus
from therapists.tests.factories import TherapistProfileFactory


@pytest.fixture
def patient(db):
    user = UserFactory(email="patient@x.test")
    user.set_password("p-pw!")
    user.save()
    return user


@pytest.fixture
def therapist_profile(db):
    p = TherapistProfileFactory()
    p.user.set_password("t-pw!")
    p.user.save()
    return p


# ---------------- start_conversation ----------------


def test_patient_can_start_conversation_with_approved_therapist(
    patient, therapist_profile
):
    convo = services.get_or_create_conversation(
        user=patient, therapist=therapist_profile
    )
    assert convo.user_id == patient.id
    assert convo.therapist_id == therapist_profile.id


def test_starting_twice_returns_same_conversation(patient, therapist_profile):
    a = services.get_or_create_conversation(user=patient, therapist=therapist_profile)
    b = services.get_or_create_conversation(user=patient, therapist=therapist_profile)
    assert a.id == b.id


def test_cannot_message_pending_therapist(patient, therapist_profile):
    therapist_profile.verification_status = VerificationStatus.PENDING
    therapist_profile.save()
    with pytest.raises(PermissionDenied):
        services.get_or_create_conversation(user=patient, therapist=therapist_profile)


def test_therapist_account_cannot_initiate_as_patient(therapist_profile):
    other = TherapistProfileFactory()
    with pytest.raises(PermissionDenied):
        services.get_or_create_conversation(
            user=therapist_profile.user, therapist=other
        )


def test_therapist_can_initiate_only_with_existing_booking(therapist_profile, db):
    user_with_booking = UserFactory(email="patient1@x.test")
    user_no_booking = UserFactory(email="patient2@x.test")

    Booking.objects.create(
        user=user_with_booking,
        therapist=therapist_profile,
        slot_start=timezone.now() + timedelta(days=2),
        slot_end=timezone.now() + timedelta(days=2, hours=1),
        state=BookingState.CONFIRMED,
    )

    convo = services.get_or_create_conversation_for_therapist(
        therapist=therapist_profile, target_user=user_with_booking
    )
    assert convo.user_id == user_with_booking.id

    with pytest.raises(PermissionDenied):
        services.get_or_create_conversation_for_therapist(
            therapist=therapist_profile, target_user=user_no_booking
        )


# ---------------- post_message + auth ----------------


def test_post_message_persists_and_updates_last_message_at(patient, therapist_profile):
    convo = services.get_or_create_conversation(
        user=patient, therapist=therapist_profile
    )
    with patch("notifications.email.send", return_value=True):
        msg = services.post_message(
            conversation=convo, sender=patient, body="Bonjour, j'aimerais réserver."
        )
    assert msg.body.startswith("Bonjour")
    convo.refresh_from_db()
    assert convo.last_message_at is not None


def test_third_party_cannot_post_message(patient, therapist_profile, db):
    convo = services.get_or_create_conversation(
        user=patient, therapist=therapist_profile
    )
    intruder = UserFactory(email="intruder@x.test")
    with pytest.raises(PermissionDenied):
        services.post_message(
            conversation=convo, sender=intruder, body="hi from outside"
        )


def test_empty_message_rejected(patient, therapist_profile):
    convo = services.get_or_create_conversation(
        user=patient, therapist=therapist_profile
    )
    with pytest.raises(ValueError):
        services.post_message(conversation=convo, sender=patient, body="   ")


# ---------------- email throttling ----------------


def test_email_skipped_when_recipient_was_recently_online(patient, therapist_profile):
    convo = services.get_or_create_conversation(
        user=patient, therapist=therapist_profile
    )
    # Therapist has been online 2 minutes ago — within EMAIL_THROTTLE
    convo.last_seen_by_therapist_at = timezone.now() - timedelta(minutes=2)
    convo.save()

    with patch("notifications.email.send", return_value=True) as mock_send:
        services.post_message(conversation=convo, sender=patient, body="Hello")
    assert mock_send.call_count == 0


def test_email_sent_when_recipient_offline(patient, therapist_profile):
    convo = services.get_or_create_conversation(
        user=patient, therapist=therapist_profile
    )
    # Therapist's last_seen is None → counts as offline
    with patch("notifications.email.send", return_value=True) as mock_send:
        services.post_message(conversation=convo, sender=patient, body="Hello")
    assert mock_send.call_count == 1


# ---------------- views ----------------


def test_thread_view_requires_login(client, patient, therapist_profile):
    convo = services.get_or_create_conversation(
        user=patient, therapist=therapist_profile
    )
    response = client.get(
        reverse("messaging:thread", kwargs={"conversation_id": convo.id})
    )
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


def test_thread_view_blocks_third_party(client, patient, therapist_profile, db):
    convo = services.get_or_create_conversation(
        user=patient, therapist=therapist_profile
    )
    other = UserFactory(email="other@x.test")
    other.set_password("o-pw!")
    other.save()
    client.login(email=other.email, password="o-pw!")
    response = client.get(
        reverse("messaging:thread", kwargs={"conversation_id": convo.id})
    )
    assert response.status_code == 403


def test_send_message_via_http(client, patient, therapist_profile):
    convo = services.get_or_create_conversation(
        user=patient, therapist=therapist_profile
    )
    client.login(email=patient.email, password="p-pw!")

    with patch("notifications.email.send", return_value=True):
        response = client.post(
            reverse("messaging:send", kwargs={"conversation_id": convo.id}),
            {"body": "Bonjour, j'aimerais discuter d'une séance."},
        )
    assert response.status_code == 302
    assert Message.objects.filter(conversation=convo).count() == 1


def test_start_conversation_redirects_to_thread(client, patient, therapist_profile):
    client.login(email=patient.email, password="p-pw!")
    response = client.post(
        reverse("messaging:start", kwargs={"therapist_slug": therapist_profile.slug})
    )
    assert response.status_code == 302
    convo = Conversation.objects.get(user=patient, therapist=therapist_profile)
    assert response["Location"].endswith(f"/messages/{convo.id}/")


# ---------------- unread count ----------------


def test_unread_count_for_recipient(patient, therapist_profile):
    convo = services.get_or_create_conversation(
        user=patient, therapist=therapist_profile
    )
    with patch("notifications.email.send", return_value=True):
        services.post_message(conversation=convo, sender=patient, body="m1")
        services.post_message(conversation=convo, sender=patient, body="m2")
    # Therapist hasn't viewed → both are unread
    assert convo.unread_count_for(therapist_profile.user) == 2
    # Patient sees no unread (their own messages)
    assert convo.unread_count_for(patient) == 0


def test_mark_seen_clears_unread(patient, therapist_profile):
    convo = services.get_or_create_conversation(
        user=patient, therapist=therapist_profile
    )
    with patch("notifications.email.send", return_value=True):
        services.post_message(conversation=convo, sender=patient, body="m1")
    assert convo.unread_count_for(therapist_profile.user) == 1
    services.mark_seen(conversation=convo, viewer=therapist_profile.user)
    assert convo.unread_count_for(therapist_profile.user) == 0


def test_role_field_defaults_to_end_user(db):
    """Sanity: a freshly-created UserFactory user is end-user role."""
    user = UserFactory(email="x@y.test")
    assert user.role == UserRole.END_USER
