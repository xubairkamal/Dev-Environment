# layers/utils.py


class DBResponseHandler:
    # Business Logic Errors (Mapped with Sys_ErrorDefinitions)
    ERRORS = {
        0: {"msg": "Success", "level": "Info"},
        50001: {
            "msg": "Concurrency Violation: Kisi aur user ne ye record update kar diya hai. Refresh karein.",
            "level": "Business",
        },
        50002: {
            "msg": "Record Not Found: Ye record database mein mojud nahi hai.",
            "level": "Business",
        },
        50003: {
            "msg": "Duplicate Entry: Ye data pehle se system mein mojud hai.",
            "level": "Business",
        },
        50004: {
            "msg": "Access Denied: Aapko is Service ka ikhtiyar nahi hai.",
            "level": "Business",
        },
        # SQL System Errors (Standard SQL Server Codes)
        2627: {
            "msg": "Primary Key Violation: Duplicate ID enter karne ki koshish ki gai.",
            "level": "System",
        },
        547: {
            "msg": "Foreign Key Conflict: Is record ka talluq dusre table se hai, delete nahi ho sakta.",
            "level": "System",
        },
        8114: {
            "msg": "Data Type Error: SQL ko bheja gaya data format ghalat hai.",
            "level": "System",
        },
    }

    # Business Logic Errors (Mapped with SQL SP Response Codes)
    ERRORS = {
        0: {"msg": "Record successfully update/deleted.", "level": "Info"},
        50001: {
            "msg": "Concurrency Violation: Ye record kisi aur ne update ya delete kar diya hai.",
            "level": "Business",
        },
        50002: {
            "msg": "Record Not Found: Ye user ab system mein maujood nahi hai.",
            "level": "Business",
        },
        50004: {
            "msg": "Access Denied: Aapko is operation ki ijazat nahi hai.",
            "level": "Business",
        },
        # System Errors
        547: {
            "msg": "Database Conflict: Is record ka data kisi aur table mein istimal ho raha hai.",
            "level": "System",
        },
    }

    @staticmethod
    def parse(code, procedure_name=""):
        error_info = DBResponseHandler.ERRORS.get(
            code, {"msg": f"SQL Execution Error ({code})", "level": "Critical"}
        )

        print(
            f"--- [{error_info['level']}] Error in {procedure_name} | Code: {code} ---"
        )

        return {
            "status": "success" if code == 0 else "error",
            "message": error_info["msg"],
            "code": code,
            "level": error_info["level"],
        }
