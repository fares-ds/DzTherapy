from django import forms
from django.utils.translation import gettext_lazy as _


class MessageForm(forms.Form):
    body = forms.CharField(
        label="",
        max_length=4000,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": _("Écrivez votre message…"),
                "class": "w-full rounded-md border border-slate-300 px-3 py-2 text-sm",
            }
        ),
    )
