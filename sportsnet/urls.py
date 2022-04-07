from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("team/", include("team.urls")),
    path("events", include("events.urls")),
    # Always keep last!
    path("", include("core.urls")),
]
