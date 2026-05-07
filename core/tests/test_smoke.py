import pytest
from django.urls import reverse

from core.factories import UserFactory


def test_home_renders(client):
    response = client.get(reverse("core:home"))
    assert response.status_code == 200
    assert b"DzTherapy" in response.content


@pytest.mark.django_db
def test_user_factory_creates_user():
    user = UserFactory()
    assert user.pk is not None
    assert "@example.test" in user.email


def test_manifest_served(client):
    response = client.get(reverse("core:manifest"))
    assert response.status_code == 200
    assert response["Content-Type"] == "application/manifest+json"
