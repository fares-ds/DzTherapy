"""Therapist-side views: public listing, public profile, signup, and dashboard."""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from bookings import services as booking_services
from bookings.models import ACTIVE_STATES, Booking, BookingState
from therapists.forms import (
    AvailabilityExceptionForm,
    AvailabilityForm,
    TherapistProfileForm,
    TherapistSignupForm,
)
from therapists.models import (
    Availability,
    AvailabilityException,
    Gender,
    TherapistProfile,
    VerificationStatus,
)
from therapists.services import get_available_slots

# Public ----------------------------------------------------------------


def therapist_list(request: HttpRequest) -> HttpResponse:
    qs = TherapistProfile.objects.filter(
        verification_status=VerificationStatus.APPROVED
    ).select_related("user")

    # Free-text search across name + headline + bio + specialties.
    # icontains is fine at MVP volume; switch to Postgres FTS later if needed.
    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(full_name__icontains=q)
            | Q(headline__icontains=q)
            | Q(bio__icontains=q)
            | Q(specialties__icontains=q)
        )

    gender = (request.GET.get("gender") or "").strip()
    if gender in {Gender.FEMALE, Gender.MALE, Gender.NON_BINARY}:
        qs = qs.filter(gender=gender)

    language = (request.GET.get("language") or "").strip()
    if language:
        qs = qs.filter(languages__icontains=language)

    max_price_raw = (request.GET.get("max_price") or "").strip()
    max_price = int(max_price_raw) if max_price_raw.isdigit() else None
    if max_price is not None:
        qs = qs.filter(session_price_dzd__lte=max_price)

    context = {
        "therapists": qs,
        "filters": {
            "q": q,
            "gender": gender,
            "language": language,
            "max_price": max_price_raw,
        },
        "gender_choices": Gender.choices,
    }
    # HTMX-driven filter form swaps just the result grid.
    if request.headers.get("HX-Request") == "true":
        return render(request, "therapists/_list_results_partial.html", context)
    return render(request, "therapists/list.html", context)


def therapist_detail(request: HttpRequest, slug: str) -> HttpResponse:
    therapist = get_object_or_404(
        TherapistProfile,
        slug=slug,
        verification_status=VerificationStatus.APPROVED,
    )
    slots = get_available_slots(therapist)
    return render(
        request,
        "therapists/detail.html",
        {"therapist": therapist, "slots": slots},
    )


# Signup ----------------------------------------------------------------


@ratelimit(key="ip", rate="5/h", method="POST", block=True)
def therapist_signup(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("therapists:profile_editor")
    if request.method == "POST":
        form = TherapistSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(
                request,
                _(
                    "Bienvenue. Votre profil est en cours de vérification ; "
                    "vous serez visible publiquement dès qu'il sera approuvé."
                ),
            )
            return redirect("therapists:profile_editor")
    else:
        form = TherapistSignupForm()
    return render(request, "therapists/signup.html", {"form": form})


# Dashboard guards ------------------------------------------------------


def _therapist_required(view):
    """Decorator: ensures a logged-in therapist with a profile."""

    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_therapist:
            return HttpResponseForbidden(_("Cet espace est réservé aux thérapeutes."))
        try:
            request.therapist_profile = request.user.therapist_profile
        except TherapistProfile.DoesNotExist:
            return redirect("therapists:signup")
        return view(request, *args, **kwargs)

    return wrapper


# Profile editor (D3) ---------------------------------------------------


@_therapist_required
def profile_editor(request: HttpRequest) -> HttpResponse:
    profile = request.therapist_profile
    if request.method == "POST":
        form = TherapistProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _("Profil mis à jour."))
            return redirect("therapists:profile_editor")
    else:
        form = TherapistProfileForm(instance=profile)
    return render(
        request,
        "therapists/profile_editor.html",
        {"form": form, "profile": profile},
    )


# Availability (D4) -----------------------------------------------------


@_therapist_required
def availability_editor(request: HttpRequest) -> HttpResponse:
    profile = request.therapist_profile
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add_slot":
            form = AvailabilityForm(request.POST)
            if form.is_valid():
                slot = form.save(commit=False)
                slot.therapist = profile
                slot.save()
                messages.success(request, _("Disponibilité ajoutée."))
            return redirect("therapists:availability_editor")
        if action == "add_exception":
            form = AvailabilityExceptionForm(request.POST)
            if form.is_valid():
                exception = form.save(commit=False)
                exception.therapist = profile
                exception.save()
                messages.success(request, _("Date bloquée."))
            return redirect("therapists:availability_editor")

    return render(
        request,
        "therapists/availability_editor.html",
        {
            "profile": profile,
            "slots": profile.availability_slots.all(),
            "exceptions": profile.availability_exceptions.all(),
            "slot_form": AvailabilityForm(),
            "exception_form": AvailabilityExceptionForm(),
        },
    )


@_therapist_required
@require_POST
def availability_delete(request: HttpRequest, availability_id: int) -> HttpResponse:
    Availability.objects.filter(
        id=availability_id, therapist=request.therapist_profile
    ).delete()
    return redirect("therapists:availability_editor")


@_therapist_required
@require_POST
def exception_delete(request: HttpRequest, exception_id: int) -> HttpResponse:
    AvailabilityException.objects.filter(
        id=exception_id, therapist=request.therapist_profile
    ).delete()
    return redirect("therapists:availability_editor")


# Booking inbox (D5) ----------------------------------------------------


@_therapist_required
def booking_inbox(request: HttpRequest) -> HttpResponse:
    bookings = (
        Booking.objects.filter(therapist=request.therapist_profile)
        .select_related("user")
        .order_by("-created_at")
    )
    return render(
        request,
        "therapists/booking_inbox.html",
        {"bookings": bookings, "states": BookingState},
    )


@_therapist_required
@require_POST
def confirm_payment(request: HttpRequest, booking_id) -> HttpResponse:
    booking = get_object_or_404(
        Booking, id=booking_id, therapist=request.therapist_profile
    )
    booking_services.confirm_payment(booking)
    messages.success(request, _("Paiement confirmé. Le lien vidéo a été envoyé."))
    if request.headers.get("HX-Request"):
        booking.refresh_from_db()
        return render(
            request,
            "therapists/_inbox_row_partial.html",
            {"booking": booking, "states": BookingState},
        )
    return redirect("therapists:booking_inbox")


@_therapist_required
@require_POST
def decline_booking(request: HttpRequest, booking_id) -> HttpResponse:
    booking = get_object_or_404(
        Booking, id=booking_id, therapist=request.therapist_profile
    )
    reason = request.POST.get("reason", "").strip()
    transitioned = booking_services.therapist_decline(booking, reason=reason)
    if transitioned:
        messages.success(
            request, _("Demande refusée. Le ou la patient·e a été notifié·e.")
        )
    if request.headers.get("HX-Request"):
        booking.refresh_from_db()
        return render(
            request,
            "therapists/_inbox_row_partial.html",
            {"booking": booking, "states": BookingState},
        )
    return redirect("therapists:booking_inbox")


# Patient list (D6) -----------------------------------------------------


@_therapist_required
def patient_list(request: HttpRequest) -> HttpResponse:
    profile = request.therapist_profile
    bookings = (
        Booking.objects.filter(
            therapist=profile,
            state__in=ACTIVE_STATES,
        )
        .select_related("user")
        .order_by("user__email", "-slot_start")
    )
    # Aggregate by user
    patients: dict = {}
    for b in bookings:
        bucket = patients.setdefault(
            b.user_id,
            {"user": b.user, "session_count": 0, "last_session": None},
        )
        bucket["session_count"] += 1
        if bucket["last_session"] is None or b.slot_start > bucket["last_session"]:
            bucket["last_session"] = b.slot_start
    return render(
        request,
        "therapists/patient_list.html",
        {"patients": patients.values()},
    )
