from django.urls import path

from bookings import views

app_name = "bookings"

urlpatterns = [
    path("nouvelle/<slug:therapist_slug>/", views.create_booking, name="create"),
    path(
        "<uuid:booking_id>/paiement/",
        views.payment_instructions,
        name="payment_instructions",
    ),
    path("<uuid:booking_id>/marquer-paye/", views.mark_paid, name="mark_paid"),
    path("<uuid:booking_id>/seance/", views.session_room, name="session_room"),
]
