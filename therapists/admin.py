from django.contrib import admin

from therapists.models import (
    Availability,
    AvailabilityException,
    TherapistProfile,
    VerificationStatus,
)


class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 0


class AvailabilityExceptionInline(admin.TabularInline):
    model = AvailabilityException
    extra = 0


@admin.register(TherapistProfile)
class TherapistProfileAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "user_email",
        "verification_status",
        "session_price_dzd",
        "created_at",
    )
    list_filter = ("verification_status",)
    search_fields = ("full_name", "user__email", "specialties", "languages")
    readonly_fields = ("created_at", "updated_at", "slug")
    actions = ("approve_selected", "reject_selected")
    inlines = (AvailabilityInline, AvailabilityExceptionInline)
    fieldsets = (
        (None, {"fields": ("user", "full_name", "headline", "bio", "photo")}),
        (
            "Pratique",
            {
                "fields": (
                    "specialties",
                    "languages",
                    "session_price_dzd",
                    "session_duration_minutes",
                )
            },
        ),
        ("Paiement", {"fields": ("payment_instructions",)}),
        ("Vérification", {"fields": ("verification_status", "verification_notes")}),
        ("Métadonnées", {"fields": ("slug", "created_at", "updated_at")}),
    )

    @admin.display(ordering="user__email", description="Email")
    def user_email(self, obj):
        return obj.user.email

    @admin.action(description="Approuver les profils sélectionnés")
    def approve_selected(self, request, queryset):
        updated = queryset.update(verification_status=VerificationStatus.APPROVED)
        self.message_user(request, f"{updated} profil(s) approuvé(s).")

    @admin.action(description="Rejeter les profils sélectionnés")
    def reject_selected(self, request, queryset):
        updated = queryset.update(verification_status=VerificationStatus.REJECTED)
        self.message_user(request, f"{updated} profil(s) rejeté(s).")
