from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Voice-note constraints. Browsers typically record webm/opus; iOS Safari
# uses mp4/m4a; we accept the common audio mimes only.
MAX_VOICE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_VOICE_CONTENT_TYPES = {
    "audio/webm",
    "audio/ogg",
    "audio/mp4",
    "audio/m4a",
    "audio/x-m4a",
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/x-wav",
}


class MessageForm(forms.Form):
    body = forms.CharField(
        label="",
        max_length=4000,
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": _(
                    "Écrivez votre message ou enregistrez une note vocale…"
                ),
                "class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm",
            }
        ),
    )
    voice_note = forms.FileField(
        label="",
        required=False,
        widget=forms.FileInput(attrs={"accept": "audio/*"}),
    )

    def clean(self):
        cleaned = super().clean()
        body = (cleaned.get("body") or "").strip()
        voice = cleaned.get("voice_note")
        if not body and not voice:
            raise ValidationError(_("Écrivez un message ou ajoutez une note vocale."))
        return cleaned

    def clean_voice_note(self):
        voice = self.cleaned_data.get("voice_note")
        if not voice:
            return voice
        if voice.size > MAX_VOICE_BYTES:
            raise ValidationError(
                _("Note vocale trop lourde (max %(max)d Mo).")
                % {"max": MAX_VOICE_BYTES // (1024 * 1024)}
            )
        ctype = getattr(voice, "content_type", "") or ""
        if ctype not in ALLOWED_VOICE_CONTENT_TYPES:
            raise ValidationError(_("Format audio non supporté."))
        return voice
