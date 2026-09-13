from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),          # allauth handles login/register/social
    path("accounts/", include("accounts.urls")),          # your custom logout view
    path("", include("finance.urls")),
]