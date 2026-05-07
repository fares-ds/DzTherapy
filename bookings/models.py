import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class BookingState(models.TextChoices):
    PENDING_PAYMENT = "pending_payment", _("En attente de paiement")
    AWAITING_CONFIRMATION = "awaiting_confirmation", _("Paiement à confirmer")
    CONFIRMED = "confirmed", _("Confirmé")
    COMPLETED = "completed", _("Terminé")
    NO_SHOW = "no_show", _("Absent")
    CANCELLED = "cancelled", _("Annulé")


# States that occupy a slot (block other bookings on the same time)
ACTIVE_STATES = (
    BookingState.PENDING_PAYMENT,
    BookingState.AWAITING_CONFIRMATION,
    BookingState.CONFIRMED,
    BookingState.COMPLETED,
)


class Booking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    therapist = models.ForeignKey(
        "therapists.TherapistProfile",
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    slot_start = models.DateTimeField(_("début"))
    slot_end = models.DateTimeField(_("fin"))
    state = models.CharField(
        _("état"),
        max_length=24,
        choices=BookingState.choices,
        default=BookingState.PENDING_PAYMENT,
    )
    user_notes = models.TextField(_("notes utilisateur"), blank=True)
    user_marked_paid_at = models.DateTimeField(null=True, blank=True)
    therapist_confirmed_at = models.DateTimeField(null=True, blank=True)
    receipt = models.FileField(
        _("justificatif"),
        upload_to="receipts/%Y/%m/",
        blank=True,
        null=True,
    )
    daily_room_url = models.URLField(_("lien vidéo"), blank=True)
    cancellation_reason = models.CharField(
        _("raison d'annulation"), max_length=255, blank=True
    )
    cancelled_by = models.CharField(
        _("annulé·e par"),
        max_length=16,
        blank=True,
        choices=(("user", "user"), ("therapist", "therapist"), ("system", "system")),
    )
    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-slot_start",)
        verbose_name = _("réservation")
        verbose_name_plural = _("réservations")
        constraints = [
            # DB-level lock that prevents two active bookings on the same slot.
            # Postgres partial unique index — `state` is in ACTIVE_STATES.
            models.UniqueConstraint(
                fields=("therapist", "slot_start"),
                condition=Q(
                    state__in=(
                        "pending_payment",
                        "awaiting_confirmation",
                        "confirmed",
                        "completed",
                    )
                ),
                name="unique_active_booking_slot",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user.email} → {self.therapist.full_name} @ {self.slot_start:%Y-%m-%d %H:%M}"

    def get_absolute_url(self) -> str:
        return reverse("bookings:payment_instructions", kwargs={"booking_id": self.id})

    @property
    def is_active(self) -> bool:
        return self.state in ACTIVE_STATES

    @property
    def can_join_session(self) -> bool:
        return self.state == BookingState.CONFIRMED and bool(self.daily_room_url)
