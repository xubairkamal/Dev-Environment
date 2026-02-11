import pyodbc
from django.conf import settings


class BaseDAL:
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
            conn = BaseDAL.get_connection()
            conn.autocommit = True
            cursor = conn.cursor()
            placeholders = ", ".join(["?"] * len(params)) if params else ""
            sql = f"{{CALL {sp_name} ({placeholders})}}"

            cursor.execute(sql, params or ())

            results = []
            while True:
                if cursor.description:
                    columns = [column[0].lower() for column in cursor.description]
                    rows = cursor.fetchall()
                    for row in rows:
                        row_dict = dict(zip(columns, row))
                        # VersionID handling for concurrency
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
    def execute_non_query(sp_name, params=None):
        """Used for INSERT, UPDATE, DELETE - Returns {status, message}"""
        conn = None
        try:
            conn = BaseDAL.get_connection()
            conn.autocommit = True
            cursor = conn.cursor()
            placeholders = ", ".join(["?"] * len(params)) if params else ""
            sql = f"{{CALL {sp_name} ({placeholders})}}"

            cursor.execute(sql, params or ())

            # SP se success/error message fetch karna (agar SP return kare)
            row = None
            if cursor.description:
                row = cursor.fetchone()

            if row:
                columns = [column[0].lower() for column in cursor.description]
                return dict(zip(columns, row))

            return {"status": "success", "message": "Operation completed."}
        except Exception as e:
            print(f"DAL Non-Query Error ({sp_name}): {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            if conn:
                conn.close()

    @staticmethod
    def execute_sp_single_row(sp_name, params=None):
        """Returns a single dictionary with LOWERCASE keys."""
        results = BaseDAL.execute_sp(sp_name, params)
        return results[0] if results else None
