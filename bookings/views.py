"""User-facing booking flow: pick slot → pay instructions → confirm → join session."""

from __future__ import annotations

from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from bookings import services as booking_services
from bookings.forms import BookingNotesForm, MarkPaidForm
from bookings.models import ACTIVE_STATES, Booking, BookingState
from notifications import email as notify
from therapists.models import TherapistProfile, VerificationStatus


def _get_approved_therapist(slug: str) -> TherapistProfile:
    return get_object_or_404(
        TherapistProfile,
        slug=slug,
        verification_status=VerificationStatus.APPROVED,
    )


def _parse_iso_slot(raw: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(raw)
    except (TypeError, ValueError):
        return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


@login_required
def create_booking(request: HttpRequest, therapist_slug: str) -> HttpResponse:
    therapist = _get_approved_therapist(therapist_slug)
    if request.user.is_therapist:
        return HttpResponseBadRequest(
            _("Les comptes thérapeutes ne peuvent pas réserver de séance.")
        )

    raw_slot = request.POST.get("slot") or request.GET.get("slot")
    slot_start = _parse_iso_slot(raw_slot or "")
    if slot_start is None or slot_start <= timezone.now():
        messages.error(
            request, _("Créneau invalide ou expiré. Choisissez-en un autre.")
        )
        return redirect("therapists:detail", slug=therapist.slug)

    slot_end = slot_start + timedelta(minutes=therapist.session_duration_minutes)

    # Slot collision check
    if Booking.objects.filter(
        therapist=therapist,
        slot_start=slot_start,
        state__in=ACTIVE_STATES,
    ).exists():
        messages.error(
            request, _("Ce créneau vient d'être réservé. Choisissez-en un autre.")
        )
        return redirect("therapists:detail", slug=therapist.slug)

    if request.method == "POST" and "user_notes" in request.POST:
        form = BookingNotesForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.therapist = therapist
            booking.slot_start = slot_start
            booking.slot_end = slot_end
            booking.save()
            notify.send_booking_submitted(booking)
            return redirect("bookings:payment_instructions", booking_id=booking.id)
    else:
        form = BookingNotesForm()

    return render(
        request,
        "bookings/create.html",
        {
            "therapist": therapist,
            "slot_start": slot_start,
            "slot_end": slot_end,
            "form": form,
        },
    )


def _booking_for_user(request: HttpRequest, booking_id) -> Booking:
    return get_object_or_404(Booking, id=booking_id, user=request.user)


@login_required
def payment_instructions(request: HttpRequest, booking_id) -> HttpResponse:
    booking = _booking_for_user(request, booking_id)
    return render(
        request,
        "bookings/payment_instructions.html",
        {"booking": booking, "states": BookingState},
    )


@login_required
def mark_paid(request: HttpRequest, booking_id) -> HttpResponse:
    booking = _booking_for_user(request, booking_id)
    if booking.state != BookingState.PENDING_PAYMENT:
        return redirect("bookings:payment_instructions", booking_id=booking.id)

    if request.method == "POST":
        form = MarkPaidForm(request.POST, request.FILES, instance=booking)
        if form.is_valid():
            form.save()  # persists receipt upload
            booking.refresh_from_db()
            booking_services.mark_user_paid(booking)
            messages.success(
                request,
                _(
                    "Merci. Votre thérapeute confirmera la réception du paiement, "
                    "puis vous recevrez le lien vidéo par e-mail."
                ),
            )
            return redirect("bookings:payment_instructions", booking_id=booking.id)
    else:
        form = MarkPaidForm(instance=booking)

    return render(
        request,
        "bookings/mark_paid.html",
        {"booking": booking, "form": form},
    )


@login_required
def session_room(request: HttpRequest, booking_id) -> HttpResponse:
    # Both the patient and the therapist can access their own session.
    booking = get_object_or_404(Booking, id=booking_id)
    if (
        booking.user_id != request.user.id
        and booking.therapist.user_id != request.user.id
    ):
        return HttpResponseBadRequest(_("Accès refusé."))
    return render(request, "bookings/session_room.html", {"booking": booking})
