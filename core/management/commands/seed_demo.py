"""Populate the local DB with demo data so the home page isn't empty.

Creates 3 approved therapists with weekly availability, and one demo patient.
Idempotent — re-running updates existing demo records rather than duplicating.

Run:
    python manage.py seed_demo
"""

from datetime import time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.models import UserRole
from therapists.models import Availability, TherapistProfile, VerificationStatus

User = get_user_model()

DEMO_THERAPISTS = [
    {
        "email": "demo.amel@dz.test",
        "full_name": "Dr Amel Benali",
        "headline": "Anxiété, burnout, transitions de vie",
        "bio": (
            "Psychologue clinicienne. J'accompagne les jeunes adultes dans la "
            "gestion du stress, l'anxiété chronique et les périodes de transition "
            "(post-études, premier emploi, parentalité)."
        ),
        "specialties": "Anxiété, Burnout, Transitions de vie",
        "languages": "Français, Arabe",
        "gender": "female",
        "payment_instructions": (
            "CCP : 0000 1234 5678\nÀ régler avant le rendez-vous puis cliquer "
            "« J'ai effectué le paiement »."
        ),
        "session_price_dzd": 2500,
        "availability": [(0, time(9), time(12)), (2, time(14), time(18))],
    },
    {
        "email": "demo.karim@dz.test",
        "full_name": "Karim Saidi",
        "headline": "Couple, communication, conflits",
        "bio": (
            "Thérapeute de couple. Approche systémique. Séances individuelles "
            "ou en couple."
        ),
        "specialties": "Couple, Communication, Conflits familiaux",
        "languages": "Français, Arabe, Tamazight",
        "gender": "male",
        "payment_instructions": "Edahabia : 6300 0000 0000 0000",
        "session_price_dzd": 3000,
        "availability": [(1, time(10), time(13)), (3, time(15), time(19))],
    },
    {
        "email": "demo.sarah@dz.test",
        "full_name": "Dr Sarah Lounis",
        "headline": "TCC, troubles du sommeil, dépression",
        "bio": (
            "Psychologue spécialisée en thérapies cognitivo-comportementales. "
            "Travail principal sur la dépression, les troubles du sommeil et "
            "les phobies."
        ),
        "specialties": "TCC, Dépression, Sommeil",
        "languages": "Français",
        "gender": "female",
        "payment_instructions": "RIB BNA : à demander en première séance",
        "session_price_dzd": 3500,
        "availability": [(4, time(9), time(13))],
    },
]


class Command(BaseCommand):
    help = "Populate the local DB with demo therapists + a demo patient."

    def handle(self, *args, **options):
        for spec in DEMO_THERAPISTS:
            user, _ = User.objects.update_or_create(
                email=spec["email"],
                defaults={
                    "username": spec["email"],
                    "role": UserRole.THERAPIST,
                    "is_active": True,
                },
            )
            user.set_password("demo-password-1!")
            user.save()
            profile, _ = TherapistProfile.objects.update_or_create(
                user=user,
                defaults={
                    "full_name": spec["full_name"],
                    "headline": spec["headline"],
                    "bio": spec["bio"],
                    "specialties": spec["specialties"],
                    "languages": spec["languages"],
                    "gender": spec.get("gender", "other"),
                    "payment_instructions": spec["payment_instructions"],
                    "session_price_dzd": spec["session_price_dzd"],
                    "verification_status": VerificationStatus.APPROVED,
                },
            )
            profile.availability_slots.all().delete()
            for weekday, start_t, end_t in spec["availability"]:
                Availability.objects.create(
                    therapist=profile,
                    weekday=weekday,
                    start_time=start_t,
                    end_time=end_t,
                )

        # Demo patient
        patient, _ = User.objects.update_or_create(
            email="demo.patient@dz.test",
            defaults={
                "username": "demo.patient@dz.test",
                "role": UserRole.END_USER,
                "is_active": True,
            },
        )
        patient.set_password("demo-password-1!")
        patient.save()

        self.stdout.write(
            self.style.SUCCESS(
                "Seeded:\n"
                f"  - {len(DEMO_THERAPISTS)} therapists (password: demo-password-1!)\n"
                "  - 1 patient: demo.patient@dz.test (password: demo-password-1!)\n"
            )
        )
