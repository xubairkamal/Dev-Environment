from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from .transaction_bll import TransactionBLL
from datetime import datetime


def is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


@never_cache
def cash_book_view(request):
    if not request.session.get("user_id"):
        return redirect("core_app:login")

    service_id = request.session.get("current_service_id")
    from_date = request.GET.get("from_date", datetime.now().strftime("%Y-%m-01"))
    to_date = request.GET.get("to_date", datetime.now().strftime("%Y-%m-%d"))
    search_str = request.GET.get("search", "")  # SP search parameter support karti hai

    # BLL call with new parameters
    transactions = TransactionBLL.get_transactions(
        service_id, from_date, to_date, search_str
    )

    context = {
        "transactions": transactions,
        "from_date": from_date,
        "to_date": to_date,
        "base_template": (
            "core_app/blank.html" if is_ajax(request) else "core_app/base.html"
        ),
    }
    return render(request, "core_app/transaction/cash_book.html", context)
