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

    # Pehla din of current month
    default_start = today.replace(day=1).strftime("%Y-%m-%d")
    # Akhri din of current month
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
    """
    AJAX view to create a new cash transaction.
    Mapping frontend data exactly to SP/BLL parameter names.
    """
    if not request.session.get("user_id"):
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=401)

    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Exact Mapping to BLL 'required_fields' and SP parameters
            params = {
                "inuscode": request.session.get("user_id"),  # @pINUSCODE
                "invtcode": data.get("invtcode"),  # @pINVTCODE
                "dttrdate": data.get("dttrdate"),  # @pDTTRDATE
                "inaccode": data.get("inaccode"),  # @pINACCODE
                "indpcode": data.get("indpcode"),  # @pINDPCODE
                "incccode": data.get("incccode"),  # @pINCCCODE
                "vctrtitl": data.get("vctrtitl", "ANONYMOUS"),  # @pVCTRTITL
                "vctrdesc": data.get("vctrdesc"),  # @pVCTRDESC
                "mntramnt": data.get("mntramnt"),  # @pMNTRAMNT
                "vctrinvc": data.get("vctrinvc", ""),  # @pVCTRINVC
                "inamcode": request.session.get("current_service_id"),  # @pINAMCODE
                "inyscode": data.get("inyscode"),  # @pINYSCODE
                "vctrchqd": data.get("vctrchqd", ""),  # @pVCTRCHQD
                "vctrmnth": data.get("vctrmnth", ""),  # @pVCTRMNTH
            }

            # BLL method call
            result = TransactionBLL.create_cash_entry(**params)
            return JsonResponse(result)

        except Exception as e:
            print(f"--- VIEW ERROR (Add Cash): {traceback.format_exc()} ---")
            return JsonResponse({"success": False, "message": str(e)}, status=500)


def update_transaction_view(request):
    """
    AJAX view to update an existing transaction.
    Mapping frontend data exactly to SP/BLL parameter names.
    """
    if not request.session.get("user_id"):
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=401)

    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Exact Mapping to SP parameters
            params = {
                "inuscode": request.session.get("user_id"),  # @pINUSCODE
                "intrcode": data.get("intrcode"),  # @pINTRCODE
                "invtcode": data.get("invtcode"),  # @pINVTCODE
                "vctrnmbr": data.get("vctrnmbr"),  # @pVCTRNMBR
                "bitrvnmb": data.get("bitrvnmb"),  # @pBITRVNMB
                "dttrdate": data.get("dttrdate"),  # @pDTTRDATE
                "inaccode": data.get("inaccode"),  # @pINACCODE
                "indpcode": data.get("indpcode"),  # @pINDPCODE
                "incccode": data.get("incccode"),  # @pINCCCODE
                "vctrtitl": data.get("vctrtitl"),  # @pVCTRTITL
                "vctrdesc": data.get("vctrdesc"),  # @pVCTRDESC
                "mntramnt": data.get("mntramnt"),  # @pMNTRAMNT
                "vctrinvc": data.get("vctrinvc", ""),  # @pVCTRINVC
                "vctrmnth": data.get("vctrmnth", ""),  # @pVCTRMNTH
                "inamcode": request.session.get("current_service_id"),  # @pINAMCODE
                "inyscode": data.get("inyscode"),  # @pINYSCODE
                "intrvrsn": data.get("intrvrsn"),  # @pINTRVRSN
                "vctrchqd": data.get("vctrchqd", ""),  # @pVCTRCHQD
            }

            # BLL method call with exact keys
            result = TransactionBLL.update_existing_transaction(**params)
            return JsonResponse(result)

        except Exception as e:
            print(f"--- VIEW ERROR (Update Transaction): {traceback.format_exc()} ---")
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
