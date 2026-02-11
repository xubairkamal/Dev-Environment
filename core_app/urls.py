from django.urls import path
from . import views

app_name = "core_app"

urlpatterns = [
    # --- Authentication ---
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # --- Dashboard ---
    path("dashboard/", views.dashboard_view, name="dashboard"),
    # --- Users Management (CRUD) ---
    path("users/user_list/", views.user_list_view, name="user_list"),
    path("users/add/", views.add_user_view, name="add_user"),
    path("users/update/", views.update_user_view, name="update_user"),
    path("users/delete/", views.delete_user_view, name="delete_user"),
    # --- User Rights Management (Matrix) ---
    # 1. Main Page (List of users to select for rights)
    path("users/user-rights/", views.user_rights_view, name="user_rights"),
    # 2. AJAX: Fetch Matrix HTML for Modal
    path(
        "users/get-user-rights/",
        views.get_user_rights_matrix_ajax,
        name="get_user_rights",
    ),
    # 3. AJAX: Save Rights JSON Data
    path(
        "users/save-user-rights/", views.save_user_rights_ajax, name="save_user_rights"
    ),
    # --- Lookups & Utilities ---
    path("common/lookup/", views.get_lookup_ajax, name="get_lookup_ajax"),
]
