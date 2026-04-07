from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from datetime import date
from core_app.modules.transaction.consolidated_bll import ConsolidatedBLL


def is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


@never_cache
def consolidated_cash_book(request):
    # Pattern Match: Session Check (As per Cash Book)
    if not request.session.get("user_id"):
        return redirect("core_app:login")

    service_id = request.session.get("current_service_id")

    # Template Selection (As per Cash Book)
    is_ajax_req = is_ajax(request)
    base_template = "core_app/blank.html" if is_ajax_req else "core_app/base.html"

    # Date Handling
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    if not from_date:
        from_date = date.today().replace(day=1).strftime("%Y-%m-%d")
    if not to_date:
        to_date = date.today().strftime("%Y-%m-%d")

    # BLL Call
    report_data = ConsolidatedBLL.get_consolidated_context(
        service_id, from_date, to_date
    )

    context = {
        "base_template": base_template,
        "from_date": from_date,
        "to_date": to_date,
        **report_data,
    }

    # Important: Folder structure as per your project
    return render(request, "core_app/transaction/consolidated_cash_book.html", context)
