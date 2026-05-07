"""Founder dashboard — staff-only stats view.

Renders a single page with the metrics the founder watches weekly:
- bookings/week (last 4 weeks)
- active therapists this week
- completion rate
"""

from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from bookings.models import Booking, BookingState
from therapists.models import TherapistProfile, VerificationStatus


@staff_member_required
def founder_dashboard(request: HttpRequest) -> HttpResponse:
    now = timezone.now()
    week_starts = [now - timedelta(weeks=i) for i in range(4)]
    weekly_bookings = []
    for start in week_starts:
        end = start
        begin = end - timedelta(days=7)
        count = Booking.objects.filter(
            created_at__gte=begin, created_at__lt=end
        ).count()
        weekly_bookings.append({"week_ending": end.date(), "count": count})

    week_ago = now - timedelta(days=7)
    active_therapists = (
        TherapistProfile.objects.filter(
            verification_status=VerificationStatus.APPROVED,
            bookings__created_at__gte=week_ago,
        )
        .distinct()
        .count()
    )
    pending_verifications = TherapistProfile.objects.filter(
        verification_status=VerificationStatus.PENDING
    ).count()
    approved_therapists = TherapistProfile.objects.filter(
        verification_status=VerificationStatus.APPROVED
    ).count()

    completed = Booking.objects.filter(state=BookingState.COMPLETED).count()
    no_show = Booking.objects.filter(state=BookingState.NO_SHOW).count()
    finished = completed + no_show
    completion_rate = (completed / finished * 100) if finished else None

    state_counts = dict(Booking.objects.values_list("state").annotate(n=Count("id")))
    by_state_rows = [
        (label, state_counts.get(value, 0)) for value, label in BookingState.choices
    ]

    return render(
        request,
        "admin/dztherapy_dashboard.html",
        {
            "weekly_bookings": list(reversed(weekly_bookings)),
            "active_therapists": active_therapists,
            "approved_therapists": approved_therapists,
            "pending_verifications": pending_verifications,
            "completion_rate": completion_rate,
            "by_state_rows": by_state_rows,
        },
    )
