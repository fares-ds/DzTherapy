from django.urls import path

from bookings import views

app_name = "bookings"

urlpatterns = [
    path("", views.my_bookings, name="my_bookings"),
    path("nouvelle/<slug:therapist_slug>/", views.create_booking, name="create"),
    path(
        "<uuid:booking_id>/paiement/",
        views.payment_instructions,
        name="payment_instructions",
    ),
    path("<uuid:booking_id>/marquer-paye/", views.mark_paid, name="mark_paid"),
    path("<uuid:booking_id>/annuler/", views.cancel_booking, name="cancel"),
    path("<uuid:booking_id>/seance/", views.session_room, name="session_room"),
    path("<uuid:booking_id>/avis/", views.leave_review, name="leave_review"),
]
