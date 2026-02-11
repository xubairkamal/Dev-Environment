from .base_dal import BaseDAL


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
            # Type casting to ensure SQL matching (Explicitly int for ServiceID)
            clean_username = str(username).strip()
            clean_password = str(password).strip()
            clean_service_id = int(service_id)

            # BaseDAL se direct execute_sp use karein
            result = BaseDAL.execute_sp(
                "sp_AuthenticateUser",
                [clean_username, clean_password, clean_service_id],
            )

            # Debugging terminal par check karein
            print(
                f"DEBUG: Params Sent -> ['{clean_username}', '{clean_password}', {clean_service_id}]"
            )
            print(f"DEBUG: SQL Result -> {result}")

            if result and len(result) > 0:
                row = result[0]

                # BaseDAL converts all keys to lowercase automatically
                user_data = {
                    "UserID": row.get("userid"),
                    "FullName": row.get("fullname"),
                    "ServiceID": row.get("serviceid"),
                    "ServiceName": row.get("servicename"),
                }

                if user_data["UserID"]:
                    return {"success": True, "user": user_data}
                else:
                    return {
                        "success": False,
                        "message": "System Error: Mapping failed (userid not found).",
                    }
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
    """

    @staticmethod
    def fetch_authorized_sidebar(user_id):
        try:
            # Sidebar ke liye SP call
            raw_menus = BaseDAL.execute_sp("sp_GetSidebarMenus", [user_id])

            if not raw_menus:
                return {}

            hierarchy = {}

            for row in raw_menus:
                # Lowercase key handling as per updated BaseDAL
                mod_val = row.get("moduleid")
                mod_id = str(mod_val) if mod_val is not None else "0"

                m_id_val = row.get("menuid")
                m_id = str(m_id_val) if m_id_val else ""
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
                    "name": row.get("menuname") or "Unknown",
                    "url": row.get("menuurl") or "#",
                    "icon": row.get("menuicon") or "bi-circle",
                    "parent_id": str(p_id) if p_id else None,
                    "has_children": False,
                    "features": [],
                }

            # Parent/Child relationship set karna
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
