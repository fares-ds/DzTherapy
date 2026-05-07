import pytest
from django.urls import reverse

from accounts.models import User, UserRole
from therapists.models import TherapistProfile, VerificationStatus


@pytest.mark.django_db
def test_therapist_signup_creates_pending_profile(client):
    response = client.post(
        reverse("therapists:signup"),
        {
            "email": "newtherapist@example.test",
            "password1": "supersecret-x9!",
            "password2": "supersecret-x9!",
            "full_name": "Dr Amine Hadjadj",
            "headline": "Anxiété et burnout",
            "bio": "Spécialisé dans l'accompagnement des jeunes professionnel·le·s.",
            "specialties": "Anxiété, Burnout",
            "languages": "Français, Arabe",
            "payment_instructions": "CCP : 0000 1234",
            "session_price_dzd": 3000,
            "session_duration_minutes": 60,
        },
        follow=True,
    )
    assert response.status_code == 200

    user = User.objects.get(email="newtherapist@example.test")
    assert user.role == UserRole.THERAPIST

    profile = TherapistProfile.objects.get(user=user)
    assert profile.full_name == "Dr Amine Hadjadj"
    assert profile.verification_status == VerificationStatus.PENDING
    assert profile.slug  # auto-generated
