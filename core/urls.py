from django.urls import path

from core import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("htmx-demo/", views.htmx_demo, name="htmx_demo"),
    path("conditions/", views.terms, name="terms"),
    path("confidentialite/", views.privacy, name="privacy"),
    path("manifest.webmanifest", views.manifest, name="manifest"),
    path("sw.js", views.sw, name="sw"),
]
