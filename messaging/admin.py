from django.contrib import admin

from messaging.models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("sender", "body", "created_at", "notified_at")
    can_delete = False


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("user_email", "therapist_name", "last_message_at", "created_at")
    list_filter = ("therapist__verification_status",)
    search_fields = ("user__email", "therapist__full_name", "therapist__user__email")
    readonly_fields = (
        "id",
        "created_at",
        "last_message_at",
        "last_seen_by_user_at",
        "last_seen_by_therapist_at",
    )
    inlines = (MessageInline,)

    @admin.display(ordering="user__email", description="Patient·e")
    def user_email(self, obj):
        return obj.user.email

    @admin.display(ordering="therapist__full_name", description="Thérapeute")
    def therapist_name(self, obj):
        return obj.therapist.full_name


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "sender", "preview", "created_at", "notified_at")
    search_fields = ("body", "sender__email")
    readonly_fields = ("created_at", "notified_at")

    @admin.display(description="Aperçu")
    def preview(self, obj):
        return (obj.body[:80] + "…") if len(obj.body) > 80 else obj.body
