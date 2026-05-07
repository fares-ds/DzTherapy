from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from bookings.models import Booking


class BookingNotesForm(forms.ModelForm):
    accept_disclaimer = forms.BooleanField(
        label=_(
            "Je comprends que DzTherapy est un outil de mise en relation "
            "et n'est pas un établissement de santé. En cas d'urgence, je "
            "contacterai les services d'urgence locaux."
        ),
        required=True,
    )

    class Meta:
        model = Booking
        fields = ("user_notes",)
        widgets = {
            "user_notes": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": _("Que souhaitez-vous aborder ? (facultatif)"),
                }
            ),
        }
        labels = {"user_notes": _("Notes pour le ou la thérapeute (optionnel)")}


# Receipt upload restrictions — keep tight; oversize / executable uploads
# are a real attack surface even on a low-volume MVP.
MAX_RECEIPT_BYTES = 5 * 1024 * 1024
ALLOWED_RECEIPT_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "application/pdf",
}


class MarkPaidForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ("receipt",)
        labels = {"receipt": _("Justificatif de paiement (optionnel)")}

    def clean_receipt(self):
        receipt = self.cleaned_data.get("receipt")
        if not receipt:
            return receipt
        if receipt.size > MAX_RECEIPT_BYTES:
            raise ValidationError(
                _("Le fichier dépasse %(max)d Mo.")
                % {"max": MAX_RECEIPT_BYTES // (1024 * 1024)}
            )
        # `content_type` may be None for some clients — be defensive.
        ctype = getattr(receipt, "content_type", "") or ""
        if ctype not in ALLOWED_RECEIPT_CONTENT_TYPES:
            raise ValidationError(
                _("Format non supporté. Utilisez JPG, PNG, GIF, WEBP ou PDF.")
            )
        return receipt
