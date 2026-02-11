from core_app.modules.users.user_dal import UserDAL


class UserBLL:
    """
    User operations (CRUD) aur Access Rights management logic.
    In charge of validating data before passing it to UserDAL.
    """

    @staticmethod
    def get_lookup_data(lookup_type, search_term=""):
        """
        Generic method to fetch lookup data (like Services, Status, etc.)
        This was missing and causing the AttributeError.
        """
        try:
            return UserDAL.get_lookup_data(lookup_type, search_term)
        except Exception as e:
            print(f"--- BLL ERROR (Lookup): {str(e)} ---")
            return []

    @staticmethod
    def get_user_list(service_id):
        try:
            return UserDAL.get_users_list_by_service(service_id)
        except Exception as e:
            print(f"--- BLL ERROR (User List): {str(e)} ---")
            return []

    @staticmethod
    def create_user(service_id, username, full_name, password, status_id, created_by):
        # Basic Validation
        if not username or not full_name or not password:
            return {"status": "error", "message": "All fields are required!"}

        try:
            return UserDAL.insert_user(
                service_id, username, full_name, password, status_id, created_by
            )
        except Exception as e:
            print(f"--- BLL ERROR (Create User): {str(e)} ---")
            return {"status": "error", "message": f"BLL Create Error: {str(e)}"}

    @staticmethod
    def update_existing_user(
        service_id,
        user_id,
        username,
        full_name,
        password,
        status_id,
        version_hex,
        changed_by,
    ):
        try:
            return UserDAL.update_user(
                service_id,
                user_id,
                username,
                full_name,
                password,
                status_id,
                version_hex,
                changed_by,
            )
        except Exception as e:
            print(f"--- BLL ERROR (Update User): {str(e)} ---")
            return {"status": "error", "message": f"BLL Update Error: {str(e)}"}

    @staticmethod
    def delete_existing_user(service_id, user_id, version_hex, requested_by):
        try:
            return UserDAL.delete_user(service_id, user_id, version_hex, requested_by)
        except Exception as e:
            print(f"--- BLL ERROR (Delete User): {str(e)} ---")
            return {"status": "error", "message": f"BLL Delete Error: {str(e)}"}

    @staticmethod
    def get_user_rights_matrix(user_id):
        """Fetches the complete menu-rights grid for a user."""
        try:
            return UserDAL.get_user_rights_matrix(user_id)
        except Exception as e:
            print(f"--- BLL ERROR (Get Rights Matrix): {str(e)} ---")
            return []

    @staticmethod
    def save_all_user_rights(user_id, rights_list):
        """
        Bulk save logic for user rights.
        Iterates through the list and calls DAL for each row.
        """
        try:
            if not user_id or not isinstance(rights_list, list):
                return {"success": False, "message": "Invalid data format."}

            for right in rights_list:
                # Syncing keys with frontend/JS: rightid, menuid, canview, etc.
                success = UserDAL.save_single_user_right(
                    right_id=int(right.get("rightid") or 0),
                    user_id=int(user_id),
                    menu_id=int(right.get("menuid")),
                    can_view=1 if right.get("canview") else 0,
                    can_create=1 if right.get("cancreate") else 0,
                    can_edit=1 if right.get("canedit") else 0,
                    can_delete=1 if right.get("candelete") else 0,
                )
                if not success:
                    raise Exception(
                        f"Failed to save right for MenuID: {right.get('menuid')}"
                    )

            return {"success": True, "message": "User rights updated successfully!"}

        except Exception as e:
            print(f"--- BLL ERROR (Save All Rights): {str(e)} ---")
            return {"success": False, "message": f"BLL Save Error: {str(e)}"}
