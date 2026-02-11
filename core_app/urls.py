from django.urls import path
from . import views  # Common views like login, dashboard
from core_app.modules.users import user_views  # User module specific views

app_name = "core_app"

urlpatterns = [
    # --- Authentication (Common) ---
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # --- Dashboard (Common) ---
    path("dashboard/", views.dashboard_view, name="dashboard"),
    # --- Users Management (CRUD) - Points to user_views.py ---
    path("users/user_list/", user_views.user_list_view, name="user_list"),
    path("users/add/", user_views.add_user_view, name="add_user"),
    path("users/update/", user_views.update_user_view, name="update_user"),
    path("users/delete/", user_views.delete_user_view, name="delete_user"),
    # --- User Rights Management (Matrix) - Points to user_views.py ---
    # 1. Main Page
    path("users/user-rights/", user_views.user_rights_view, name="user_rights"),
    # 2. AJAX: Fetch Matrix HTML
    path(
        "users/get-user-rights/",
        user_views.get_user_rights_matrix_ajax,
        name="get_user_rights",
    ),
    # 3. AJAX: Save Rights JSON Data
    path(
        "users/save-user-rights/",
        user_views.save_user_rights_ajax,
        name="save_user_rights",
    ),
    # --- Lookups & Utilities ---
    path("common/lookup/", user_views.get_lookup_ajax, name="get_lookup_ajax"),
]
