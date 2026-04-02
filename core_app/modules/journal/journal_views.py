from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
import json
import traceback
from datetime import date
import calendar

# Modular Imports
from core_app.modules.journal.journal_bll import JournalBLL


def is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


@never_cache
def journal_book_view(request):
    """
    Main General Journal View: Handles date range filtering and initial page load.
    """
    if not request.session.get("user_id"):
        if is_ajax(request):
            return JsonResponse(
                {"success": False, "message": "Session Expired"}, status=401
            )
        return redirect("core_app:login")

    is_ajax_req = is_ajax(request)
    base_template = "core_app/blank.html" if is_ajax_req else "core_app/base.html"

    # Default Date Range: Current Month
    today = date.today()
    default_start = today.replace(day=1).strftime("%Y-%m-%d")
    last_day_val = calendar.monthrange(today.year, today.month)[1]
    default_end = today.replace(day=last_day_val).strftime("%Y-%m-%d")

    context = {
        "base_template": base_template,
        "first_day": default_start,
        "last_day": default_end,
    }

    return render(request, "core_app/journal/general_journal.html", context)


def journal_list_ajax(request):
    """
    AJAX view to fetch journal data for DataTables OR a single entry for editing.
    """
    if not request.session.get("user_id"):
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=401)

    try:
        service_id = request.session.get("current_service_id")

        # 1. Check if specific ID is requested (For Edit Modal)
        journal_id = request.GET.get("id")
        if journal_id:
            # BLL se single record fetch karen
            data = JournalBLL.get_journal_list(service_id, id=journal_id)
            if data:
                return JsonResponse({"success": True, "data": data[0]})
            return JsonResponse({"success": False, "message": "Record not found"})

        # 2. Otherwise, handle DataTables List request
        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")
        search_term = request.GET.get("search[value]", "")

        data = JournalBLL.get_journal_list(
            service_id, from_date=from_date, to_date=to_date, search_term=search_term
        )

        return JsonResponse(
            {
                "draw": int(request.GET.get("draw", 1)),
                "recordsTotal": len(data),
                "recordsFiltered": len(data),
                "data": data,
            }
        )
    except Exception as e:
        print(f"--- VIEW ERROR (Journal List): {traceback.format_exc()} ---")
        return JsonResponse({"success": False, "message": str(e)}, status=500)


def add_journal_view(request):
    """
    AJAX view to create a new Journal Entry using spGjrnlAdd.
    """
    if not request.session.get("user_id"):
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=401)

    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Mapping frontend fields to SP parameters
            params = {
                "inuscode": request.session.get("user_id"),
                "inamcode": request.session.get("current_service_id"),
                "dtgjdate": data.get("dtgjdate"),
                "indrcode": data.get("indrcode"),
                "incrcode": data.get("incrcode"),
                "indpcode": data.get("indpcode"),
                "vcgjtitl": data.get("vcgjtitl", ""),
                "vcgjdesc": data.get("vcgjdesc", ""),
                "mngjamnt": data.get("mngjamnt"),
                "vcgjmnth": data.get("vcgjmnth", ""),
                "invncode": data.get("invncode", 0),
                "inetcode": data.get("inetcode", 1),
                "vcgjrtyp": data.get("vcgjrtyp", "GJ"),
                "ingjrefr": data.get("ingjrefr", 0),
                "inyscode": data.get("inyscode", 10),
                "ingjvrsn": 0,  # New entry version is always 0
            }

            result = JournalBLL.create_journal_entry(**params)
            return JsonResponse(result)

        except Exception as e:
            print(f"--- VIEW ERROR (Save Journal): {traceback.format_exc()} ---")
            return JsonResponse({"success": False, "message": str(e)}, status=500)


def delete_journal_view(request):
    """AJAX view to delete/cancel a journal entry."""
    if not request.session.get("user_id"):
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=401)

    if request.method == "POST":
        try:
            import json

            data = json.loads(request.body)

            # JournalBLL call (Yahan check karlein ke BLL mein ye method mojood ho)
            # result = JournalBLL.delete_existing_journal(
            #     request.session.get("current_service_id"),
            #     data.get("trans_id"),
            #     data.get("version_hex"),
            #     request.session.get("user_id")
            # )

            # Temporary success message jab tak BLL integrate nahi hoti:
            return JsonResponse({"success": True, "message": "Deleted successfully"})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)


def update_journal_view(request):
    """
    AJAX view to update existing Journal Entry using spGjrnlEdit.
    """
    if not request.session.get("user_id"):
        return JsonResponse({"success": False, "message": "Unauthorized"}, status=401)

    if request.method == "POST":
        try:
            data = json.loads(request.body)

            params = {
                "inuscode": request.session.get("user_id"),
                "inamcode": request.session.get("current_service_id"),
                "vcgjnmbr": data.get("vcgjnmbr"),
                "bigjvnm": data.get("bigjvnm"),
                "dtgjdate": data.get("dtgjdate"),
                "indrcode": data.get("indrcode"),
                "incrcode": data.get("incrcode"),
                "indpcode": data.get("indpcode"),
                "vcgjtitl": data.get("vcgjtitl", ""),
                "vcgjdesc": data.get("vcgjdesc", ""),
                "mngjamnt": data.get("mngjamnt"),
                "vcgjmnth": data.get("vcgjmnth", ""),
                "inyscode": data.get("inyscode"),
                "ingjvrsn": data.get("ingjvrsn"),  # Version check for concurrency
            }

            result = JournalBLL.update_existing_journal(**params)
            return JsonResponse(result)

        except Exception as e:
            print(f"--- VIEW ERROR (Update Journal): {traceback.format_exc()} ---")
            return JsonResponse({"success": False, "message": str(e)}, status=500)


from django.http import JsonResponse
from core_app.modules.journal.journal_bll import JournalBLL  # Ensure BLL is imported


def get_journal_lookup_ajax(request):
    """
    Journal entries ke liye dynamic lookup (Accounts, etc.) fetch karta hai.
    """
    if not request.session.get("user_id"):
        return JsonResponse([], safe=False)

    lookup_type = request.GET.get("type")
    search_term = request.GET.get("term", "")

    try:
        # JournalBLL se data fetch karen (agar method bana hua hai)
        # data = JournalBLL.get_lookup_data(lookup_type, search_term)

        # Temporary empty list taake server crash na ho
        data = []

        return JsonResponse(data, safe=False)
    except Exception as e:
        print(f"--- VIEW ERROR (Journal Lookup): {str(e)} ---")
        return JsonResponse([], safe=False)
