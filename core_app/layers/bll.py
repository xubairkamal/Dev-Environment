from .dal import DataAccessLayer
from .constants import DBErrorCodes


class AuthBLL:
    """
    User authentication aur login logic.
    """

    @staticmethod
    def login(username, password, service_id):
        if not username or not password or not service_id:
            return {
                "success": False,
                "message": "Username, Password, and Service are required.",
            }

        try:
            result = DataAccessLayer.execute_sp(
                "sp_AuthenticateUser", [username, password, service_id]
            )

            if result and len(result) > 0:
                row = result[0]
                user_data = {
                    "UserID": row.get("userid"),
                    "FullName": row.get("fullname"),
                    "ServiceID": row.get("serviceid"),
                    "ServiceName": row.get("servicename"),
                }
                return {"success": True, "user": user_data}
            else:
                return {
                    "success": False,
                    "message": "Invalid credentials or service mapping.",
                }
        except Exception as e:
            print(f"--- BLL ERROR (Login): {str(e)} ---")
            return {"success": False, "message": f"System Error: {str(e)}"}


class SecurityBLL:
    """
    Authorization aur Sidebar menu logic.
    Supports: Module -> Parent Menu -> Sub Menu
    """

    @staticmethod
    def fetch_authorized_sidebar(user_id):
        try:
            raw_menus = DataAccessLayer.get_sidebar_menus(user_id)
            if not raw_menus:
                return {}

            hierarchy = {}

            for row in raw_menus:
                mod_val = row.get("moduleid")
                mod_id = str(mod_val) if mod_val is not None else "0"

                m_id = str(row.get("menuid", ""))
                p_id = row.get("parentmenuid")

                if not m_id:
                    continue

                if mod_id not in hierarchy:
                    hierarchy[mod_id] = {
                        "name": row.get("modulename") or "Main",
                        "menus": {},
                    }

                hierarchy[mod_id]["menus"][m_id] = {
                    "id": m_id,
                    "name": row.get("menuname", "Unknown"),
                    "url": row.get("menuurl", "#"),
                    "icon": row.get("menuicon") or "bi-circle",
                    "parent_id": str(p_id) if p_id else None,
                    "has_children": False,
                }

            for mod_id in hierarchy:
                menus_dict = hierarchy[mod_id]["menus"]
                for m_id, m_data in menus_dict.items():
                    parent_id = m_data["parent_id"]
                    if parent_id and parent_id in menus_dict:
                        menus_dict[parent_id]["has_children"] = True

            return hierarchy
        except Exception as e:
            print(f"--- BLL ERROR (Sidebar): {str(e)} ---")
            return {}


class UserBLL:
    """
    User operations (CRUD) aur Access Rights management.
    """

    @staticmethod
    def get_user_list(service_id):
        try:
            return DataAccessLayer.get_users_list_by_service(service_id)
        except Exception as e:
            print(f"--- BLL ERROR (List): {str(e)} ---")
            return []

    @staticmethod
    def create_user(service_id, username, full_name, password, status_id, created_by):
        if not username or not full_name or not password:
            return {"status": "error", "message": "All fields are required!"}
        try:
            return DataAccessLayer.insert_user(
                service_id, username, full_name, password, status_id, created_by
            )
        except Exception as e:
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
            return DataAccessLayer.update_user(
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
            return {"status": "error", "message": f"BLL Update Error: {str(e)}"}

    @staticmethod
    def delete_existing_user(service_id, user_id, version_hex, requested_by):
        try:
            return DataAccessLayer.delete_user(
                service_id, user_id, version_hex, requested_by
            )
        except Exception as e:
            return {"status": "error", "message": f"BLL Delete Error: {str(e)}"}

    @staticmethod
    def get_user_rights_matrix(user_id):
        """
        Matrix fetch karta hai DAL ke through.
        """
        try:
            return DataAccessLayer.get_user_rights_matrix(user_id)
        except Exception as e:
            print(f"--- BLL ERROR (Get Rights): {str(e)} ---")
            return []

    @staticmethod
    def save_all_user_rights(user_id, rights_list):
        """
        Bulk save logic for user rights.
        """
        try:
            if not user_id or not isinstance(rights_list, list):
                return {"success": False, "message": "Invalid data format."}

            for right in rights_list:
                # Keys sync with JS: rightid, menuid, canview, cancreate, canedit, candelete
                DataAccessLayer.save_single_user_right(
                    right_id=int(right.get("rightid") or 0),
                    user_id=int(user_id),
                    menu_id=int(right.get("menuid")),
                    can_view=1 if right.get("canview") else 0,
                    can_create=1 if right.get("cancreate") else 0,
                    can_edit=1 if right.get("canedit") else 0,
                    can_delete=1 if right.get("candelete") else 0,
                )

            return {"success": True, "message": "User rights updated successfully!"}

        except Exception as e:
            print(f"--- BLL ERROR (Save Rights): {str(e)} ---")
            return {"success": False, "message": f"BLL Save Error: {str(e)}"}
