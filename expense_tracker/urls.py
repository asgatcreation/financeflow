from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.http import FileResponse
import os


def service_worker(request):
    path = os.path.join(settings.BASE_DIR, "static", "sw.js")
    return FileResponse(open(path, "rb"), content_type="application/javascript")


def pwa_manifest(request):
    path = os.path.join(settings.BASE_DIR, "static", "manifest.json")
    return FileResponse(open(path, "rb"), content_type="application/manifest+json")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("accounts/", include("accounts.urls")),
    path("", include("finance.urls")),

    # PWA — served at root so scope covers the whole app
    path("sw.js", service_worker, name="sw"),
    path("manifest.json", pwa_manifest, name="manifest"),
]