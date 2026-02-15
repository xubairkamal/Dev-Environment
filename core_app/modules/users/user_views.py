from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.cache import cache_control
import json
import traceback

# Naye Modular Imports
from core_app.modules.users.user_bll import UserBLL
from core_app.layers.base_dal import BaseDAL


def is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


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
        "core_app/users/user_list.html",
        {"users": users_data, "base_template": base_template},
    )


def get_lookup_ajax(request):
    lookup_type = request.GET.get("type")
    search_term = request.GET.get("q", "")
    # BaseDAL ya UserDAL se lookup data lena
    results = UserBLL.get_lookup_data(lookup_type, search_term)
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
            request,
            "core_app/users/_rights_matrix_partial.html",
            {"rights": rights_data},
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": "Failed to load matrix"}, status=500
        )


def save_user_rights_ajax(request):
    if not request.session.get("user_id"):
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=401)

    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            user_id = data.get("user_id") or data.get("userId")

            if not user_id:
                return JsonResponse(
                    {"success": False, "message": "User ID missing"}, status=400
                )

            result = UserBLL.save_all_user_rights(int(user_id), data.get("rights", []))
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)


@never_cache
def user_rights_view(request):
    if not request.session.get("user_id"):
        return redirect("core_app:login")

    is_ajax_req = is_ajax(request)
    base_template = "core_app/blank.html" if is_ajax_req else "core_app/base.html"
    return render(
        request, "core_app/users/user_rights.html", {"base_template": base_template}
    )
