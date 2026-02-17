from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
import json
import traceback
from datetime import datetime, date
import calendar

# Naye Modular Imports
from core_app.modules.transaction.transaction_bll import TransactionBLL


def is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


@never_cache
def cash_book_view(request):
    """
    Main Cash Book View: Handles dynamic date ranges and AJAX reloads.
    """
    if not request.session.get("user_id"):
        if is_ajax(request):
            return JsonResponse(
                {"success": False, "message": "Session Expired"}, status=401
            )
        return redirect("core_app:login")

    service_id = request.session.get("current_service_id")
    is_ajax_req = is_ajax(request)
    base_template = "core_app/blank.html" if is_ajax_req else "core_app/base.html"

    # --- Dynamic Date Handling ---
    today = date.today()

    # Pehla din of current month: 2026-02-01
    default_start = today.replace(day=1).strftime("%Y-%m-%d")
    # Akhri din of current month: 2026-02-28
    last_day = calendar.monthrange(today.year, today.month)[1]
    default_end = today.replace(day=last_day).strftime("%Y-%m-%d")

    # Agar GET request mein dates hain to wo use karein, warna default
    from_date = request.GET.get("from_date", default_start)
    to_date = request.GET.get("to_date", default_end)
    search_term = request.GET.get("q", "")

    try:
        # BLL call matching sp_Trans_GetList parameters
        transactions_data = TransactionBLL.get_cash_book_list(
            service_id, from_date, to_date, search_term
        )
    except Exception:
        print(f"--- VIEW ERROR (Cash Book): {traceback.format_exc()} ---")
        transactions_data = []

    return render(
        request,
        "core_app/transaction/cash_book.html",
        {
            "transactions": transactions_data,
            "base_template": base_template,
            "from_date": from_date,
            "to_date": to_date,
            "search_term": search_term,
        },
    )


def get_transaction_lookup_ajax(request):
    """Generic lookup for transaction accounts, categories, etc."""
    lookup_type = request.GET.get("type")
    search_term = request.GET.get("q", "")
    results = TransactionBLL.get_lookup_data(lookup_type, search_term)
    return JsonResponse({"results": results})


# --- CRUD Operations ---


def add_cash_entry_view(request):
    """AJAX view to create a new cash transaction."""
    if not request.session.get("user_id"):
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=401)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            result = TransactionBLL.create_cash_entry(
                request.session.get("current_service_id"),
                data.get("date"),
                data.get("account_id"),
                data.get("description"),
                data.get("amount"),
                request.session.get("user_id"),
            )
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)


def update_transaction_view(request):
    """AJAX view to update an existing transaction."""
    if not request.session.get("user_id"):
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=401)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            result = TransactionBLL.update_existing_transaction(
                request.session.get("current_service_id"),
                data.get("trans_id"),
                data.get("date"),
                data.get("account_id"),
                data.get("description"),
                data.get("amount"),
                data.get("version_hex"),
                request.session.get("user_id"),
            )
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)


def delete_transaction_view(request):
    """AJAX view to delete/cancel a transaction."""
    if not request.session.get("user_id"):
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=401)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            result = TransactionBLL.delete_existing_transaction(
                request.session.get("current_service_id"),
                data.get("trans_id"),
                data.get("version_hex"),
                request.session.get("user_id"),
            )
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)
