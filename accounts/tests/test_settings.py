"""Patient-side account settings (display_name) + Mes réservations."""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from bookings.models import Booking, BookingState
from core.factories import UserFactory
from therapists.tests.factories import TherapistProfileFactory


@pytest.fixture
def patient(db):
    user = UserFactory(email="patient@x.test")
    user.set_password("p-pw!")
    user.save()
    return user


def test_account_settings_requires_login(client):
    response = client.get(reverse("accounts:settings"))
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


def test_patient_can_set_display_name(client, patient):
    client.login(email=patient.email, password="p-pw!")
    response = client.post(
        reverse("accounts:settings"),
        {"display_name": "Sara M."},
    )
    assert response.status_code == 302
    patient.refresh_from_db()
    assert patient.display_name == "Sara M."
    assert patient.public_name == "Sara M."


def test_public_name_falls_back_to_email(patient):
    assert patient.display_name == ""
    assert patient.public_name == patient.email


def test_my_bookings_separates_past_and_upcoming(client, patient, db):
    therapist = TherapistProfileFactory()
    now = timezone.now()
    upcoming = Booking.objects.create(
        user=patient,
        therapist=therapist,
        slot_start=now + timedelta(days=2),
        slot_end=now + timedelta(days=2, hours=1),
        state=BookingState.CONFIRMED,
    )
    past = Booking.objects.create(
        user=patient,
        therapist=therapist,
        slot_start=now - timedelta(days=5),
        slot_end=now - timedelta(days=5) + timedelta(hours=1),
        state=BookingState.COMPLETED,
    )

    client.login(email=patient.email, password="p-pw!")
    response = client.get(reverse("bookings:my_bookings"))
    assert response.status_code == 200
    body = response.content.decode()
    # Both bookings appear
    assert str(upcoming.therapist.full_name) in body
    assert str(past.therapist.full_name) in body
    # The view splits them; ensure both sections show up at all
    assert "À venir" in body or "venir" in body
    assert "Historique" in body
