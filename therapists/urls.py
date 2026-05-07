from django.urls import path

from therapists import views

app_name = "therapists"

urlpatterns = [
    # Public
    path("", views.therapist_list, name="list"),
    path("inscription/", views.therapist_signup, name="signup"),
    # Therapist dashboard (auth required + role=therapist)
    path("dashboard/profil/", views.profile_editor, name="profile_editor"),
    path(
        "dashboard/disponibilites/",
        views.availability_editor,
        name="availability_editor",
    ),
    path(
        "dashboard/disponibilites/<int:availability_id>/supprimer/",
        views.availability_delete,
        name="availability_delete",
    ),
    path(
        "dashboard/exceptions/<int:exception_id>/supprimer/",
        views.exception_delete,
        name="exception_delete",
    ),
    path("dashboard/messages/", views.booking_inbox, name="booking_inbox"),
    path(
        "dashboard/messages/<uuid:booking_id>/confirmer-paiement/",
        views.confirm_payment,
        name="confirm_payment",
    ),
    path("dashboard/patients/", views.patient_list, name="patient_list"),
    # Public profile (must come after fixed routes to avoid slug collision)
    path("<slug:slug>/", views.therapist_detail, name="detail"),
]
