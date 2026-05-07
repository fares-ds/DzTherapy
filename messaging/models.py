import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Conversation(models.Model):
    """A 1:1 conversation between a patient and a therapist.

    Auto-created on first message in either direction. Unique per (user, therapist).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    therapist = models.ForeignKey(
        "therapists.TherapistProfile",
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    last_message_at = models.DateTimeField(null=True, blank=True, db_index=True)
    # `last_seen_*_at` is set when the respective party opens the thread.
    # Used to throttle email notifications: if the recipient was online recently,
    # we don't email — they'll see the message in-app.
    last_seen_by_user_at = models.DateTimeField(null=True, blank=True)
    last_seen_by_therapist_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-last_message_at", "-created_at")
        verbose_name = _("conversation")
        verbose_name_plural = _("conversations")
        constraints = [
            models.UniqueConstraint(
                fields=("user", "therapist"),
                name="unique_user_therapist_conversation",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user.email} ↔ {self.therapist.full_name}"

    def get_absolute_url(self) -> str:
        return reverse("messaging:thread", kwargs={"conversation_id": self.id})

    def participants(self) -> tuple:
        return (self.user, self.therapist.user)

    def includes(self, user) -> bool:
        return user.id in (self.user_id, self.therapist.user_id)

    def other_party(self, viewer):
        """Return the *other* User object relative to the viewer."""
        if viewer.id == self.user_id:
            return self.therapist.user
        return self.user

    def unread_count_for(self, viewer) -> int:
        if not self.includes(viewer):
            return 0
        last_seen = (
            self.last_seen_by_user_at
            if viewer.id == self.user_id
            else self.last_seen_by_therapist_at
        )
        qs = self.messages.exclude(sender=viewer)
        if last_seen:
            qs = qs.filter(created_at__gt=last_seen)
        return qs.count()


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    body = models.TextField(_("contenu"), blank=True)
    voice_note = models.FileField(
        _("note vocale"),
        upload_to="voice_notes/%Y/%m/",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    notified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("created_at",)
        verbose_name = _("message")
        verbose_name_plural = _("messages")

    def __str__(self) -> str:
        preview = (self.body[:60] + "…") if len(self.body) > 60 else self.body
        return f"{self.sender.email}: {preview or '[voice]'}"

    @property
    def has_voice(self) -> bool:
        return bool(self.voice_note)
