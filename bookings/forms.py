from django import forms
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


class MarkPaidForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ("receipt",)
        labels = {"receipt": _("Justificatif de paiement (optionnel)")}
