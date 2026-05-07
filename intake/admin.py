from django.contrib import admin

from intake.models import IntakeSession


@admin.register(IntakeSession)
class IntakeSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user_email", "completed", "created_at")
    list_filter = ("completed",)
    readonly_fields = (
        "id",
        "user",
        "messages",
        "recommended_therapist_slugs",
        "created_at",
        "updated_at",
    )

    @admin.display(description="Visiteur·euse")
    def user_email(self, obj):
        return obj.user.email if obj.user_id else "(anonyme)"
