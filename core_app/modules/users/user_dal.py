from core_app.layers.base_dal import BaseDAL


class UserDAL(BaseDAL):
    """
    User-specific Data Access Layer.
    Inherits execute_sp and execute_sp_single_row from BaseDAL.
    """

    @staticmethod
    def get_users_list_by_service(service_id):
        """Fetches all users for a specific service."""
        return BaseDAL.execute_sp("sp_Users_GetList", [service_id])

    @staticmethod
    def insert_user(service_id, username, full_name, password, status_id, created_by):
        """Inserts a new user and returns success/error status."""
        params = (service_id, username, full_name, password, status_id, created_by)
        result = BaseDAL.execute_sp_single_row("sp_Users_Insert", params)

        if result and str(result.get("status", "")).lower() == "success":
            return {
                "status": "success",
                "message": "User created!",
                "new_id": result.get("newid"),
            }
        return {"status": "error", "message": "Insert failed or user already exists."}

    @staticmethod
    def update_user(
        service_id,
        user_id,
        username,
        full_name,
        password,
        status_id,
        version_bin,
        changed_by,
    ):
        """Updates user details with concurrency check (version_bin)."""
        params = (
            service_id,
            user_id,
            username,
            full_name,
            password,
            status_id,
            version_bin,
            changed_by,
        )
        result = BaseDAL.execute_sp_single_row("sp_Users_Update", params)

        if result and str(result.get("status", "")).lower() == "success":
            return {"status": "success", "message": "User updated!"}
        return {
            "status": "error",
            "message": "Update failed (Concurrency or DB error).",
        }

    @staticmethod
    def delete_user(service_id, user_id, version_bin, requested_by):
        """Soft deletes or removes a user."""
        params = (service_id, user_id, version_bin, requested_by)
        result = BaseDAL.execute_sp_single_row("sp_Users_Delete", params)

        if result and str(result.get("status", "")).lower() == "success":
            return {"status": "success", "message": "User deleted!"}
        return {"status": "error", "message": "Delete failed."}

    @staticmethod
    def get_user_rights_matrix(user_id):
        """Fetches the complete menu-rights grid for a user."""
        return BaseDAL.execute_sp("sp_Get_User_Rights_Matrix", [user_id])

    @staticmethod
    def save_single_user_right(
        right_id, user_id, menu_id, can_view, can_create, can_edit, can_delete
    ):
        """Inserts or updates a single permission row."""
        try:
            params = (
                right_id,
                user_id,
                menu_id,
                can_view,
                can_create,
                can_edit,
                can_delete,
            )
            BaseDAL.execute_sp("sp_Save_User_Right", params)
            return True
        except Exception as e:
            print(f"DAL Save Right Error: {str(e)}")
            return False

    @staticmethod
    def get_lookup_data(lookup_type, search_term=None):
        """Common lookup for user-related dropdowns (Roles, Groups etc)."""
        raw_data = BaseDAL.execute_sp("sp_Common_GetLookup", [lookup_type, search_term])
        return [
            {"id": str(row.get("id", "")), "text": str(row.get("text", "No Name"))}
            for row in raw_data
        ]
