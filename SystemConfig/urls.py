from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache


@never_cache
def root_redirect(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("core_app:login")
    return redirect("core_app:dashboard")


urlpatterns = [
    path("admin/", admin.site.urls),
    # Core app ki saari routing yahan se handle hogi
    path("", include("core_app.urls")),
    path("", root_redirect, name="root_redirect"),
]
