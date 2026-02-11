from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache


@never_cache
def root_redirect(request):
    user_id = request.session.get("user_id")
    print(f"DEBUG: Current User ID in Session: {user_id}")  # Console mein check karein

    if not user_id:
        return redirect("core_app:login")
    return redirect("core_app:dashboard")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("setup/", include("core_app.urls", namespace="core_app")),
    path("", root_redirect, name="root_redirect"),
]
