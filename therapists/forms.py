from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from accounts.models import User, UserRole
from therapists.models import (
    Availability,
    AvailabilityException,
    Gender,
    TherapistProfile,
)


class TherapistSignupForm(forms.Form):
    """One-page therapist onboarding: account creds + profile in a single form."""

    email = forms.EmailField(label=_("Adresse e-mail"))
    password1 = forms.CharField(label=_("Mot de passe"), widget=forms.PasswordInput)
    password2 = forms.CharField(
        label=_("Confirmer le mot de passe"), widget=forms.PasswordInput
    )
    full_name = forms.CharField(label=_("Nom complet"), max_length=128)
    headline = forms.CharField(label=_("Titre court"), max_length=160, required=False)
    bio = forms.CharField(
        label=_("Présentation"),
        widget=forms.Textarea(attrs={"rows": 4}),
        required=False,
    )
    specialties = forms.CharField(
        label=_("Spécialités (séparées par des virgules)"),
        max_length=255,
        required=False,
    )
    languages = forms.CharField(
        label=_("Langues parlées (séparées par des virgules)"),
        max_length=128,
        initial="Français",
    )
    gender = forms.ChoiceField(
        label=_("Genre"),
        choices=Gender.choices,
        initial=Gender.OTHER,
    )
    payment_instructions = forms.CharField(
        label=_("Instructions de paiement (CCP / RIB / Edahabia)"),
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False,
    )
    session_price_dzd = forms.IntegerField(
        label=_("Prix de la séance (DZD)"), min_value=0, initial=2500
    )
    session_duration_minutes = forms.IntegerField(
        label=_("Durée de la séance (minutes)"), min_value=15, initial=60
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(_("Un compte existe déjà avec cette adresse."))
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError(_("Les deux mots de passe ne correspondent pas."))
        if p1:
            validate_password(p1)
        return cleaned

    def save(self) -> User:
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data["email"],
            email=data["email"],
            password=data["password1"],
            role=UserRole.THERAPIST,
        )
        TherapistProfile.objects.create(
            user=user,
            full_name=data["full_name"],
            headline=data.get("headline", ""),
            bio=data.get("bio", ""),
            specialties=data.get("specialties", ""),
            languages=data.get("languages", "Français"),
            gender=data.get("gender", Gender.OTHER),
            payment_instructions=data.get("payment_instructions", ""),
            session_price_dzd=data["session_price_dzd"],
            session_duration_minutes=data["session_duration_minutes"],
        )
        return user


class TherapistProfileForm(forms.ModelForm):
    class Meta:
        model = TherapistProfile
        fields = (
            "full_name",
            "headline",
            "bio",
            "specialties",
            "languages",
            "gender",
            "photo",
            "payment_instructions",
            "session_price_dzd",
            "session_duration_minutes",
        )
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 5}),
            "payment_instructions": forms.Textarea(attrs={"rows": 4}),
        }


class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ("weekday", "start_time", "end_time")
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }


class AvailabilityExceptionForm(forms.ModelForm):
    class Meta:
        model = AvailabilityException
        fields = ("date", "reason")
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}
