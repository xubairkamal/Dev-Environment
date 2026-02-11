from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.cache import cache_control
import json
import traceback

from .layers.bll import SecurityBLL, UserBLL, AuthBLL
from .layers.dal import DataAccessLayer


def is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


@never_cache
def login_view(request):
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
    auth_logout(request)
    request.session.flush()
    response = redirect("core_app:login")
    response.delete_cookie("sessionid")
    return response


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboard_view(request):
    if not request.session.get("user_id"):
        return redirect("core_app:login")

    is_ajax_req = is_ajax(request)
    base_template = "core_app/blank.html" if is_ajax_req else "core_app/base.html"
    return render(request, "core_app/dashboard.html", {"base_template": base_template})


@never_cache
def user_list_view(request):
    if not request.session.get("user_id"):
        if is_ajax(request):
            return JsonResponse(
                {"success": False, "message": "Session Expired"}, status=401
            )
        return redirect("core_app:login")

    service_id = request.session.get("current_service_id")
    is_ajax_req = is_ajax(request)
    base_template = "core_app/blank.html" if is_ajax_req else "core_app/base.html"

    try:
        users_data = UserBLL.get_user_list(service_id)
    except Exception as e:
        users_data = []

    return render(
        request,
        "core_app/user_list.html",
        {"users": users_data, "base_template": base_template},
    )


def get_lookup_ajax(request):
    lookup_type = request.GET.get("type")
    search_term = request.GET.get("q", "")
    results = DataAccessLayer.get_lookup_data(lookup_type, search_term)
    return JsonResponse({"results": results})


# --- CRUD Operations ---


def add_user_view(request):
    if not request.session.get("user_id"):
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=401)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            result = UserBLL.create_user(
                request.session.get("current_service_id"),
                data.get("username"),
                data.get("full_name"),
                data.get("password"),
                data.get("status_id"),
                request.session.get("user_id"),
            )
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)


def update_user_view(request):
    if not request.session.get("user_id"):
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=401)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            result = UserBLL.update_existing_user(
                request.session.get("current_service_id"),
                data.get("user_id"),
                data.get("username"),
                data.get("full_name"),
                data.get("password"),
                data.get("status_id"),
                data.get("version_hex"),
                request.session.get("user_id"),
            )
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)


def delete_user_view(request):
    if not request.session.get("user_id"):
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=401)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            result = UserBLL.delete_existing_user(
                request.session.get("current_service_id"),
                data.get("user_id"),
                data.get("version_hex"),
                request.session.get("user_id"),
            )
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)


# --- User Rights Views ---


def get_user_rights_matrix_ajax(request):
    if not request.session.get("user_id"):
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=401)

    user_id = request.GET.get("user_id")
    if not user_id:
        return JsonResponse(
            {"success": False, "message": "User ID missing"}, status=400
        )

    try:
        rights_data = UserBLL.get_user_rights_matrix(user_id)
        return render(
            request, "core_app/_rights_matrix_partial.html", {"rights": rights_data}
        )
    except Exception as e:
        print(f"Matrix Render Error: {traceback.format_exc()}")
        return JsonResponse(
            {"success": False, "message": "Failed to load matrix"}, status=500
        )


def save_user_rights_ajax(request):
    if not request.session.get("user_id"):
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=401)

    if request.method == "POST":
        try:
            raw_body = request.body.decode("utf-8")
            data = json.loads(raw_body)

            # --- Yahan hum log badal rahe hain taake confirm ho sake ---
            print("--- NEW LOG START ---")
            print(f"RAW DATA: {raw_body}")

            # Key check with fallbacks
            user_id = data.get("user_id") or data.get("userId")

            if not user_id:
                # Agar user_id missing hai, toh return karne se pehle poora data print karein
                print(f"FAILED: User ID missing in these keys: {list(data.keys())}")
                return JsonResponse(
                    {"success": False, "message": "User ID missing in payload"},
                    status=400,
                )

            result = UserBLL.save_all_user_rights(int(user_id), data.get("rights", []))
            return JsonResponse(result)

        except Exception as e:
            print(f"ERROR: {str(e)}")
            return JsonResponse({"success": False, "message": str(e)}, status=500)


@never_cache
def user_rights_view(request):
    if not request.session.get("user_id"):
        return redirect("core_app:login")

    is_ajax_req = is_ajax(request)
    base_template = "core_app/blank.html" if is_ajax_req else "core_app/base.html"
    return render(
        request, "core_app/user_rights.html", {"base_template": base_template}
    )
