from datetime import date, time, timedelta

import pytest
from django.utils import timezone

from therapists.models import VerificationStatus
from therapists.services import get_available_slots
from therapists.tests.factories import (
    AvailabilityExceptionFactory,
    AvailabilityFactory,
    TherapistProfileFactory,
)


def _next_weekday(target_weekday: int) -> date:
    today = timezone.localdate()
    delta = (target_weekday - today.weekday()) % 7
    if delta == 0:
        delta = 7  # always future
    return today + timedelta(days=delta)


@pytest.mark.django_db
def test_pending_therapist_yields_no_slots():
    therapist = TherapistProfileFactory(verification_status=VerificationStatus.PENDING)
    AvailabilityFactory(
        therapist=therapist, weekday=0, start_time=time(9), end_time=time(11)
    )
    assert get_available_slots(therapist) == []


@pytest.mark.django_db
def test_get_available_slots_emits_session_length_chunks():
    therapist = TherapistProfileFactory(session_duration_minutes=60)
    target_weekday = _next_weekday(0).weekday()  # Monday
    AvailabilityFactory(
        therapist=therapist,
        weekday=target_weekday,
        start_time=time(9),
        end_time=time(12),
    )
    slots = get_available_slots(therapist, days=14)
    assert (
        len(slots) >= 3
    )  # 3 hour-long chunks per Monday × at least 1 Monday in 14 days
    for start, end in slots:
        assert (end - start).total_seconds() == 60 * 60


@pytest.mark.django_db
def test_blocked_dates_excluded():
    therapist = TherapistProfileFactory()
    target = _next_weekday(0)  # next Monday
    AvailabilityFactory(
        therapist=therapist,
        weekday=target.weekday(),
        start_time=time(9),
        end_time=time(11),
    )
    AvailabilityExceptionFactory(therapist=therapist, date=target)
    slots = get_available_slots(therapist, days=8)
    assert all(start.date() != target for start, _end in slots)
