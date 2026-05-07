import factory

from accounts.models import User, UserRole
from therapists.models import (
    Availability,
    AvailabilityException,
    TherapistProfile,
    VerificationStatus,
)


class TherapistUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"therapist{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.test")
    role = UserRole.THERAPIST


class TherapistProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TherapistProfile

    user = factory.SubFactory(TherapistUserFactory)
    full_name = factory.Sequence(lambda n: f"Dr Test {n}")
    bio = "Spécialiste en anxiété et burnout."
    specialties = "Anxiété, Burnout"
    languages = "Français, Arabe"
    payment_instructions = "CCP : 0000 1234 5678"
    session_price_dzd = 2500
    session_duration_minutes = 60
    verification_status = VerificationStatus.APPROVED


class AvailabilityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Availability


class AvailabilityExceptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AvailabilityException
