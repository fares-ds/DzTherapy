from django.shortcuts import render


def home(request):
    return render(request, "core/home.html")


def htmx_demo(request):
    return render(request, "core/_demo_partial.html")


def manifest(request):
    return render(
        request, "manifest.webmanifest", content_type="application/manifest+json"
    )


def sw(request):
    return render(request, "sw.js", content_type="application/javascript")
