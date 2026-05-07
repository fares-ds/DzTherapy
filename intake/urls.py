from django.urls import path

from intake import views

app_name = "intake"

urlpatterns = [
    path("", views.start, name="start"),
    path("urgence/", views.crisis_notice, name="crisis"),
    path("<uuid:session_id>/", views.thread, name="thread"),
    path("<uuid:session_id>/reponse/", views.reply_view, name="reply"),
]
