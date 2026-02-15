from django.urls import path
from . import views
from core_app.modules.users import user_views
from core_app.modules.transaction import transaction_views

app_name = "core_app"

urlpatterns = [
    # --- Authentication & Dashboard ---
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    # --- Users Management ---
    path("setup/users/user_list/", user_views.user_list_view, name="user_list"),
    path("setup/users/add/", user_views.add_user_view, name="add_user"),
    path("setup/users/update/", user_views.update_user_view, name="update_user"),
    path("setup/users/delete/", user_views.delete_user_view, name="delete_user"),
    # User Rights Paths - Names matched with user_list.html
    path("setup/users/rights/", user_views.user_rights_view, name="user_rights"),
    path(
        "setup/users/rights/get-matrix/",
        user_views.get_user_rights_matrix_ajax,
        name="get_user_rights_matrix_ajax",  # Yahan _ajax add kiya hai
    ),
    path(
        "setup/users/rights/save/",
        user_views.save_user_rights_ajax,
        name="save_user_rights",
    ),
    # --- Transaction ---
    path(
        "transaction/cash-book/",
        transaction_views.cash_book_view,
        name="cash_book_list",
    ),
    # --- Lookups & Utilities ---
    path("common/lookup/", user_views.get_lookup_ajax, name="get_lookup_ajax"),
]
