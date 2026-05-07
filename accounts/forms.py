from django import forms
from django.utils.translation import gettext_lazy as _

from accounts.models import User


class AccountSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("display_name",)
        labels = {"display_name": _("Nom affiché (optionnel)")}
