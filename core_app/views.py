from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.views.decorators.cache import never_cache
from django.views.decorators.cache import cache_control

# Sirf Auth aur Security ki BLL import hogi yahan
from .layers.sidebar_bll import AuthBLL, SecurityBLL


def is_ajax(request):
    """Common Utility (Isay layers/utils.py mein bhi rakha ja sakta hai)"""
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


@never_cache
def login_view(request):
    """Handle User Login and Sidebar Session Initialization"""
    if request.session.get("user_id"):
        return redirect("core_app:dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        service_id = request.POST.get("service_id")

        result = AuthBLL.login(username, password, service_id)

        if result["success"]:
            user = result["user"]
            request.session["user_id"] = user["UserID"]
            request.session["full_name"] = user["FullName"]
            request.session["current_service_id"] = user["ServiceID"]
            request.session["service_name"] = user["ServiceName"]

            # Sidebar menu hierarchy ko session mein save karna
            try:
                hierarchy = SecurityBLL.fetch_authorized_sidebar(user["UserID"])
                request.session["sidebar_data"] = hierarchy if hierarchy else {}
                request.session.modified = True
            except Exception as e:
                print(f"Sidebar Critical Error: {e}")
                request.session["sidebar_data"] = {}

            return redirect("core_app:dashboard")
        else:
            messages.error(request, result["message"])

    return render(request, "core_app/login.html")


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout_view(request):
    """Clear Session and Redirect to Login"""
    auth_logout(request)
    request.session.flush()
    response = redirect("core_app:login")
    response.delete_cookie("sessionid")
    return response


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboard_view(request):
    """Main Landing Page after Login"""
    if not request.session.get("user_id"):
        return redirect("core_app:login")

    is_ajax_req = is_ajax(request)
    # SPA behavior ke liye base template switch
    base_template = "core_app/blank.html" if is_ajax_req else "core_app/base.html"
    return render(request, "core_app/dashboard.html", {"base_template": base_template})
