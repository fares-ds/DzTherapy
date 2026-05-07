"""Channels-layer integration: posting a message broadcasts to the group."""

from unittest.mock import patch

import pytest
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from core.factories import UserFactory
from messaging import services
from messaging.consumers import ThreadConsumer
from therapists.tests.factories import TherapistProfileFactory


@pytest.fixture
def patient(db):
    user = UserFactory(email="patient@x.test")
    user.set_password("p-pw!")
    user.save()
    return user


@pytest.fixture
def therapist_profile(db):
    p = TherapistProfileFactory()
    p.user.set_password("t-pw!")
    p.user.save()
    return p


def test_post_message_broadcasts_to_channel_layer(patient, therapist_profile):
    convo = services.get_or_create_conversation(
        user=patient, therapist=therapist_profile
    )
    layer = get_channel_layer()
    assert layer is not None

    async def _subscribe_and_capture():
        # Subscribe a fake channel to the conversation's group.
        channel_name = await layer.new_channel()
        await layer.group_add(f"chat-{convo.id}", channel_name)
        return channel_name

    channel_name = async_to_sync(_subscribe_and_capture)()

    with patch("notifications.email.send", return_value=True):
        services.post_message(conversation=convo, sender=patient, body="Bonjour")

    async def _drain():
        return await layer.receive(channel_name)

    event = async_to_sync(_drain)()
    assert event["type"] == "chat.new"
    assert "message_id" in event


def test_consumer_class_has_proper_handlers():
    # Sanity that the WS consumer doesn't blow up at import + has the
    # expected event handler.
    assert hasattr(ThreadConsumer, "chat_new")
    assert hasattr(ThreadConsumer, "_user_in_conversation")
