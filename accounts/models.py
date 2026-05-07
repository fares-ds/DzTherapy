from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    END_USER = "end_user", _("Utilisateur")
    THERAPIST = "therapist", _("Thérapeute")


class User(AbstractUser):
    email = models.EmailField(_("adresse e-mail"), unique=True)
    role = models.CharField(
        _("rôle"),
        max_length=16,
        choices=UserRole.choices,
        default=UserRole.END_USER,
    )
    display_name = models.CharField(
        _("nom affiché"),
        max_length=64,
        blank=True,
        help_text=_(
            "Optionnel. Si renseigné, ce nom apparaîtra à la place de votre "
            "adresse e-mail dans les boîtes de réception des thérapeutes."
        ),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = _("utilisateur")
        verbose_name_plural = _("utilisateurs")

    def __str__(self) -> str:
        return self.email

    @property
    def is_therapist(self) -> bool:
        return self.role == UserRole.THERAPIST

    @property
    def is_end_user(self) -> bool:
        return self.role == UserRole.END_USER

    @property
    def public_name(self) -> str:
        """Display-name when set, falls back to email. Used in inbox & lists."""
        return self.display_name or self.email
