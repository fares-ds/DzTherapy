"""Search + filter behavior on the public therapist directory."""

import pytest
from django.urls import reverse

from therapists.models import Gender, VerificationStatus
from therapists.tests.factories import TherapistProfileFactory


@pytest.fixture
def directory(db):
    """Three approved therapists with distinct gender/language/price."""
    a = TherapistProfileFactory(
        full_name="Dr Amel Benali",
        bio="Spécialiste en anxiété chronique.",
        specialties="Anxiété, Burnout",
        languages="Français, Arabe",
        gender=Gender.FEMALE,
        session_price_dzd=2500,
        verification_status=VerificationStatus.APPROVED,
    )
    b = TherapistProfileFactory(
        full_name="Karim Saidi",
        bio="Thérapie de couple et conflits.",
        specialties="Couple, Communication",
        languages="Français, Arabe, Tamazight",
        gender=Gender.MALE,
        session_price_dzd=3000,
        verification_status=VerificationStatus.APPROVED,
    )
    c = TherapistProfileFactory(
        full_name="Dr Sarah Lounis",
        bio="TCC et troubles du sommeil.",
        specialties="TCC, Dépression, Sommeil",
        languages="Français",
        gender=Gender.FEMALE,
        session_price_dzd=4000,
        verification_status=VerificationStatus.APPROVED,
    )
    return a, b, c


def test_list_returns_all_when_no_filter(client, directory):
    response = client.get(reverse("therapists:list"))
    assert response.status_code == 200
    body = response.content.decode()
    assert "Dr Amel Benali" in body
    assert "Karim Saidi" in body
    assert "Dr Sarah Lounis" in body


def test_search_matches_specialty(client, directory):
    response = client.get(reverse("therapists:list"), {"q": "couple"})
    body = response.content.decode()
    assert "Karim Saidi" in body
    assert "Dr Amel Benali" not in body


def test_filter_by_gender_female(client, directory):
    response = client.get(reverse("therapists:list"), {"gender": "female"})
    body = response.content.decode()
    assert "Dr Amel Benali" in body
    assert "Dr Sarah Lounis" in body
    assert "Karim Saidi" not in body


def test_filter_by_max_price(client, directory):
    response = client.get(reverse("therapists:list"), {"max_price": "3000"})
    body = response.content.decode()
    assert "Dr Amel Benali" in body  # 2500
    assert "Karim Saidi" in body  # 3000
    assert "Dr Sarah Lounis" not in body  # 4000


def test_filter_by_language(client, directory):
    response = client.get(reverse("therapists:list"), {"language": "Tamazight"})
    body = response.content.decode()
    assert "Karim Saidi" in body
    assert "Dr Amel Benali" not in body


def test_combined_filters(client, directory):
    response = client.get(
        reverse("therapists:list"),
        {"gender": "female", "max_price": "3000", "language": "Arabe"},
    )
    body = response.content.decode()
    assert "Dr Amel Benali" in body  # female + Arabe + 2500
    assert "Dr Sarah Lounis" not in body  # no Arabe
    assert "Karim Saidi" not in body  # not female


def test_htmx_request_returns_only_results_partial(client, directory):
    response = client.get(
        reverse("therapists:list"),
        {"q": "anxiété"},
        HTTP_HX_REQUEST="true",
    )
    body = response.content.decode()
    # Partial doesn't include the page header / search form
    assert "<html" not in body
    assert "Dr Amel Benali" in body
