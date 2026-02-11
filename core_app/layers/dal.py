import pyodbc
from django.conf import settings


class DataAccessLayer:
    @staticmethod
    def get_connection():
        try:
            # 1. Check if DB_CONFIG exists in settings.py
            if hasattr(settings, "DB_CONFIG"):
                db_cfg = settings.DB_CONFIG
                driver = db_cfg.get("driver", "SQL Server")
                server = db_cfg.get("server")
                database = db_cfg.get("database")
            else:
                # 2. Fallback to default Django DATABASES setting
                db_cfg = settings.DATABASES["default"]
                driver = db_cfg.get("OPTIONS", {}).get("driver", "SQL Server")
                server = db_cfg.get("HOST")
                database = db_cfg.get("NAME")

            if not server or not database:
                raise ValueError("Database settings not found in settings.py!")

            conn_str = (
                f"DRIVER={{{driver}}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"Trusted_Connection=yes;"
                f"Connection Timeout=5;"
            )
            return pyodbc.connect(conn_str)
        except Exception as e:
            print(f"CRITICAL Connection Error: {str(e)}")
            raise e

    @staticmethod
    def execute_sp(sp_name, params=None):
        """Returns a list of dictionaries with LOWERCASE keys."""
        conn = None
        try:
            conn = DataAccessLayer.get_connection()
            conn.autocommit = True
            cursor = conn.cursor()
            placeholders = ", ".join(["?"] * len(params)) if params else ""
            sql = f"{{CALL {sp_name} ({placeholders})}}"
            cursor.execute(sql, params or ())

            results = []
            while True:
                if cursor.description:
                    columns = [column[0].lower() for column in cursor.description]
                    for row in cursor.fetchall():
                        row_dict = dict(zip(columns, row))
                        if "versionid" in row_dict and row_dict["versionid"]:
                            row_dict["version_hex"] = row_dict["versionid"].hex()
                        results.append(row_dict)
                    if results:
                        break

                if not cursor.nextset():
                    break
            return results
        except Exception as e:
            print(f"DAL SP Error ({sp_name}): {str(e)}")
            return []
        finally:
            if conn:
                conn.close()

    @staticmethod
    def execute_sp_single_row(sp_name, params=None):
        """Returns a single dictionary with LOWERCASE keys."""
        conn = None
        try:
            conn = DataAccessLayer.get_connection()
            conn.autocommit = True
            cursor = conn.cursor()
            placeholders = ", ".join(["?"] * len(params)) if params else ""
            sql = f"{{CALL {sp_name} ({placeholders})}}"
            cursor.execute(sql, params or ())

            row = None
            while True:
                if cursor.description:
                    row = cursor.fetchone()
                    if row:
                        break
                if not cursor.nextset():
                    break

            if row:
                columns = [column[0].lower() for column in cursor.description]
                row_dict = dict(zip(columns, row))
                if "versionid" in row_dict and row_dict["versionid"]:
                    row_dict["version_hex"] = row_dict["versionid"].hex()
                return row_dict
            return None
        except Exception as e:
            print(f"DAL Single Row Error ({sp_name}): {str(e)}")
            return None
        finally:
            if conn:
                conn.close()

    # --- Auth & Sidebar ---
    @staticmethod
    def get_sidebar_menus(user_id):
        return DataAccessLayer.execute_sp("sp_GetSidebarMenus", [user_id])

    @staticmethod
    def get_lookup_data(lookup_type, search_term=None):
        raw_data = DataAccessLayer.execute_sp(
            "sp_Common_GetLookup", [lookup_type, search_term]
        )
        return [
            {"id": str(row.get("id", "")), "text": str(row.get("text", "No Name"))}
            for row in raw_data
        ]

    # --- User CRUD ---
    @staticmethod
    def get_users_list_by_service(service_id):
        return DataAccessLayer.execute_sp("sp_Users_GetList", [service_id])

    @staticmethod
    def insert_user(service_id, username, full_name, password, status_id, created_by):
        params = (service_id, username, full_name, password, status_id, created_by)
        result = DataAccessLayer.execute_sp_single_row("sp_Users_Insert", params)
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
        result = DataAccessLayer.execute_sp_single_row("sp_Users_Update", params)
        if result and str(result.get("status", "")).lower() == "success":
            return {"status": "success", "message": "User updated!"}
        return {
            "status": "error",
            "message": "Update failed (Concurrency or DB error).",
        }

    @staticmethod
    def delete_user(service_id, user_id, version_bin, requested_by):
        params = (service_id, user_id, version_bin, requested_by)
        result = DataAccessLayer.execute_sp_single_row("sp_Users_Delete", params)
        if result and str(result.get("status", "")).lower() == "success":
            return {"status": "success", "message": "User deleted!"}
        return {"status": "error", "message": "Delete failed."}

    # --- User Rights Matrix ---
    @staticmethod
    def get_user_rights_matrix(user_id):
        """Fetches the complete menu-rights grid."""
        return DataAccessLayer.execute_sp("sp_Get_User_Rights_Matrix", [user_id])

    @staticmethod
    def save_single_user_right(
        right_id, user_id, menu_id, can_view, can_create, can_edit, can_delete
    ):
        """Inserts or updates a single row via SP."""
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
            # Chunke yahan return value zaroori nahi, isliye execute_sp kafi hai
            DataAccessLayer.execute_sp("sp_Save_User_Right", params)
            return True
        except Exception as e:
            print(f"DAL Save Right Error: {str(e)}")
            return False
