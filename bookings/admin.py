from django.contrib import admin

from bookings.models import Booking, BookingState


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_email",
        "therapist_name",
        "slot_start",
        "state",
        "created_at",
    )
    list_filter = ("state", "therapist")
    search_fields = ("user__email", "therapist__full_name", "therapist__user__email")
    date_hierarchy = "slot_start"
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "user_marked_paid_at",
        "therapist_confirmed_at",
        "daily_room_url",
    )
    actions = ("mark_completed", "mark_no_show", "mark_cancelled")
    fieldsets = (
        (None, {"fields": ("id", "user", "therapist", "state")}),
        ("Créneau", {"fields": ("slot_start", "slot_end")}),
        ("Notes & paiement", {"fields": ("user_notes", "receipt")}),
        (
            "Cycle de vie",
            {
                "fields": (
                    "user_marked_paid_at",
                    "therapist_confirmed_at",
                    "daily_room_url",
                    "cancellation_reason",
                )
            },
        ),
        ("Métadonnées", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(ordering="user__email", description="Patient·e")
    def user_email(self, obj):
        return obj.user.email

    @admin.display(ordering="therapist__full_name", description="Thérapeute")
    def therapist_name(self, obj):
        return obj.therapist.full_name

    @admin.action(description="Marquer comme terminée")
    def mark_completed(self, request, queryset):
        updated = queryset.update(state=BookingState.COMPLETED)
        self.message_user(request, f"{updated} séance(s) marquée(s) terminée(s).")

    @admin.action(description="Marquer comme absent·e")
    def mark_no_show(self, request, queryset):
        updated = queryset.update(state=BookingState.NO_SHOW)
        self.message_user(request, f"{updated} séance(s) marquée(s) absent·e.")

    @admin.action(description="Annuler les séances sélectionnées")
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(state=BookingState.CANCELLED)
        self.message_user(request, f"{updated} séance(s) annulée(s).")
