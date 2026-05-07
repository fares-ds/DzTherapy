"""Cross-user isolation: a therapist must not see or act on another therapist's bookings."""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from bookings.models import Booking, BookingState
from core.factories import UserFactory
from therapists.tests.factories import TherapistProfileFactory


@pytest.fixture
def therapist_a(db):
    p = TherapistProfileFactory(full_name="Dr A")
    p.user.set_password("a-pw!")
    p.user.save()
    return p


@pytest.fixture
def therapist_b(db):
    p = TherapistProfileFactory(full_name="Dr B")
    p.user.set_password("b-pw!")
    p.user.save()
    return p


@pytest.fixture
def patient(db):
    u = UserFactory(email="patient@x.test")
    u.set_password("p-pw!")
    u.save()
    return u


@pytest.fixture
def booking_for_a(db, therapist_a, patient):
    slot = timezone.now() + timedelta(days=2)
    return Booking.objects.create(
        user=patient,
        therapist=therapist_a,
        slot_start=slot,
        slot_end=slot + timedelta(hours=1),
        state=BookingState.AWAITING_CONFIRMATION,
    )


def test_therapist_b_cannot_confirm_a_s_booking(client, booking_for_a, therapist_b):
    client.login(email=therapist_b.user.email, password="b-pw!")
    response = client.post(
        reverse("therapists:confirm_payment", kwargs={"booking_id": booking_for_a.id}),
    )
    assert response.status_code == 404
    booking_for_a.refresh_from_db()
    assert booking_for_a.state == BookingState.AWAITING_CONFIRMATION


def test_therapist_b_cannot_decline_a_s_booking(client, booking_for_a, therapist_b):
    client.login(email=therapist_b.user.email, password="b-pw!")
    response = client.post(
        reverse("therapists:decline_booking", kwargs={"booking_id": booking_for_a.id}),
    )
    assert response.status_code == 404
    booking_for_a.refresh_from_db()
    assert booking_for_a.state == BookingState.AWAITING_CONFIRMATION


def test_therapist_b_inbox_does_not_show_a_s_booking(
    client, booking_for_a, therapist_b
):
    client.login(email=therapist_b.user.email, password="b-pw!")
    response = client.get(reverse("therapists:booking_inbox"))
    assert response.status_code == 200
    # patient@x.test is the user on therapist_a's booking — must not surface here
    assert b"patient@x.test" not in response.content


def test_unauthenticated_user_redirected_from_dashboard(client):
    response = client.get(reverse("therapists:profile_editor"))
    # login_required redirects to LOGIN_URL
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


def test_end_user_role_forbidden_from_therapist_dashboard(client, db):
    user = UserFactory(email="enduser@x.test")
    user.set_password("u-pw!")
    user.save()
    client.login(email=user.email, password="u-pw!")
    response = client.get(reverse("therapists:profile_editor"))
    assert response.status_code == 403


def test_session_room_blocks_third_party(client, booking_for_a, db):
    other = UserFactory(email="thirdparty@x.test")
    other.set_password("o-pw!")
    other.save()
    client.login(email=other.email, password="o-pw!")
    response = client.get(
        reverse("bookings:session_room", kwargs={"booking_id": booking_for_a.id})
    )
    assert response.status_code == 400
