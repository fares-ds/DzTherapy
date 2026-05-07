from django.urls import path

from messaging import views

app_name = "messaging"

urlpatterns = [
    path("", views.conversation_list, name="list"),
    path("nouvelle/<slug:therapist_slug>/", views.start_conversation, name="start"),
    path("<uuid:conversation_id>/", views.thread, name="thread"),
    path(
        "<uuid:conversation_id>/messages/",
        views.thread_messages_partial,
        name="thread_messages",
    ),
    path(
        "<uuid:conversation_id>/envoyer/",
        views.send_message,
        name="send",
    ),
]
