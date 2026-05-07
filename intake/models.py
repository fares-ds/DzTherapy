import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class IntakeSession(models.Model):
    """A guided AI conversation that helps a visitor describe their situation.

    Stores the message history (JSON) so we can re-render the chat across
    page loads. Anonymous visitors get a session-keyed pseudo-session;
    logged-in users get one tied to their account.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="intake_sessions",
    )
    # Free-form message log: [{"role": "user"|"assistant", "content": "..."}]
    messages = models.JSONField(default=list, blank=True)
    completed = models.BooleanField(default=False)
    recommended_therapist_slugs = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("session d'orientation")
        verbose_name_plural = _("sessions d'orientation")
        ordering = ("-created_at",)

    def __str__(self) -> str:
        identifier = self.user.email if self.user_id else f"anon:{self.id}"
        return f"Intake · {identifier}"

    def append(self, role: str, content: str) -> None:
        self.messages = (self.messages or []) + [{"role": role, "content": content}]
