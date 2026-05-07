"""Inject the authenticated user's total unread message count into every template.

Cheap (one COUNT query); skipped for anonymous users.
"""

from django.db.models import Q

from messaging.models import Conversation


def unread_messages(request) -> dict:
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {"unread_messages_total": 0}

    convos = Conversation.objects.filter(
        Q(user=user) | Q(therapist__user=user)
    ).select_related("therapist")
    total = 0
    for c in convos:
        total += c.unread_count_for(user)
    return {"unread_messages_total": total}
