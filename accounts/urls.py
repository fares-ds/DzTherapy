from django.urls import path

from accounts import views

app_name = "accounts"

urlpatterns = [
    path("", views.account_settings, name="settings"),
]
