from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

WEEKDAYS = [
    (0, _("Lundi")),
    (1, _("Mardi")),
    (2, _("Mercredi")),
    (3, _("Jeudi")),
    (4, _("Vendredi")),
    (5, _("Samedi")),
    (6, _("Dimanche")),
]


class VerificationStatus(models.TextChoices):
    PENDING = "pending", _("En attente")
    APPROVED = "approved", _("Approuvé")
    REJECTED = "rejected", _("Rejeté")


class TherapistProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="therapist_profile",
    )
    slug = models.SlugField(_("slug"), unique=True, max_length=128, blank=True)
    full_name = models.CharField(_("nom complet"), max_length=128)
    headline = models.CharField(
        _("titre court"),
        max_length=160,
        blank=True,
        help_text=_("Une phrase qui résume votre approche."),
    )
    bio = models.TextField(_("présentation"), blank=True)
    specialties = models.CharField(
        _("spécialités"),
        max_length=255,
        blank=True,
        help_text=_("Séparées par des virgules"),
    )
    languages = models.CharField(
        _("langues parlées"),
        max_length=128,
        blank=True,
        default="Français",
        help_text=_("Séparées par des virgules"),
    )
    photo = models.ImageField(
        _("photo"), upload_to="therapists/", blank=True, null=True
    )
    payment_instructions = models.TextField(
        _("instructions de paiement"),
        blank=True,
        help_text=_(
            "CCP / RIB / Edahabia ou autres détails. Affiché à l'utilisateur après réservation."
        ),
    )
    session_price_dzd = models.PositiveIntegerField(
        _("prix de la séance (DZD)"), default=0
    )
    session_duration_minutes = models.PositiveSmallIntegerField(
        _("durée de la séance (minutes)"), default=60
    )
    verification_status = models.CharField(
        _("statut de vérification"),
        max_length=16,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )
    verification_notes = models.TextField(_("notes de vérification"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("profil thérapeute")
        verbose_name_plural = _("profils thérapeutes")
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.full_name or self.user.email

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.full_name) or slugify(self.user.email.split("@")[0])
            slug = base
            counter = 2
            while (
                TherapistProfile.objects.filter(slug=slug).exclude(pk=self.pk).exists()
            ):
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("therapists:detail", kwargs={"slug": self.slug})

    @property
    def is_approved(self) -> bool:
        return self.verification_status == VerificationStatus.APPROVED

    @property
    def specialties_list(self) -> list[str]:
        return [s.strip() for s in self.specialties.split(",") if s.strip()]

    @property
    def languages_list(self) -> list[str]:
        return [s.strip() for s in self.languages.split(",") if s.strip()]


class Availability(models.Model):
    """A recurring weekly time-window during which the therapist accepts bookings.

    Slots are derived from these windows by `services.get_available_slots`.
    """

    therapist = models.ForeignKey(
        TherapistProfile,
        on_delete=models.CASCADE,
        related_name="availability_slots",
    )
    weekday = models.PositiveSmallIntegerField(_("jour"), choices=WEEKDAYS)
    start_time = models.TimeField(_("début"))
    end_time = models.TimeField(_("fin"))

    class Meta:
        verbose_name = _("disponibilité")
        verbose_name_plural = _("disponibilités")
        ordering = ("weekday", "start_time")
        constraints = [
            models.UniqueConstraint(
                fields=("therapist", "weekday", "start_time"),
                name="unique_availability_slot",
            )
        ]

    def __str__(self) -> str:
        return f"{self.get_weekday_display()} {self.start_time:%H:%M}–{self.end_time:%H:%M}"

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError(_("L'heure de début doit précéder l'heure de fin."))


class AvailabilityException(models.Model):
    """A specific date on which the therapist is unavailable (vacation, etc.)."""

    therapist = models.ForeignKey(
        TherapistProfile,
        on_delete=models.CASCADE,
        related_name="availability_exceptions",
    )
    date = models.DateField(_("date"))
    reason = models.CharField(_("raison"), max_length=128, blank=True)

    class Meta:
        verbose_name = _("exception de disponibilité")
        verbose_name_plural = _("exceptions de disponibilité")
        ordering = ("date",)
        constraints = [
            models.UniqueConstraint(
                fields=("therapist", "date"),
                name="unique_availability_exception",
            )
        ]

    def __str__(self) -> str:
        return f"{self.therapist.full_name} blocked {self.date}"
