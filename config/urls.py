from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from core.admin_views import founder_dashboard

urlpatterns = [
    # Founder dashboard must come before admin/ to avoid being shadowed.
    path("admin/dztherapy/dashboard/", founder_dashboard, name="founder_dashboard"),
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("accounts/", include("allauth.urls")),
    path("mon-compte/", include("accounts.urls")),
    path("therapeutes/", include("therapists.urls")),
    path("reservations/", include("bookings.urls")),
    path("messages/", include("messaging.urls")),
    path("orientation/", include("intake.urls")),
    path("", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
