from core_app.modules.journal.journal_dal import JournalDAL


class JournalBLL:
    """
    Journal operations (CRUD) management logic.
    DAL ke sath data exchange aur business rules validation yahan handle hoti hai.
    """

    @staticmethod
    def get_journal_list(service_id, from_date, to_date, search_term=""):
        """
        Fetches the general journal entries with date filtering.
        """
        try:
            return JournalDAL.get_journal_book_data(
                service_id, from_date, to_date, search_term
            )
        except Exception as e:
            print(f"--- BLL ERROR (Journal List): {str(e)} ---")
            return []

    @staticmethod
    def create_journal_entry(**kwargs):
        """
        Logic for creating a new journal entry based on spGjrnlAdd.
        """
        try:
            # Basic Validation
            if not kwargs.get("indrcode") or not kwargs.get("incrcode"):
                return {
                    "success": False,
                    "message": "Both Debit and Credit accounts are required.",
                }

            if float(kwargs.get("mngjamnt", 0)) <= 0:
                return {
                    "success": False,
                    "message": "Amount must be greater than zero.",
                }

            # DAL Call
            result = JournalDAL.insert_journal_entry(**kwargs)
            return result

        except Exception as e:
            print(f"--- BLL ERROR (Create Journal): {str(e)} ---")
            return {"success": False, "message": f"BLL Error: {str(e)}"}

    @staticmethod
    def update_existing_journal(**kwargs):
        """
        Logic for updating journal entry using spGjrnlEdit.
        Handles status mapping based on SP return values.
        """
        try:
            # Data cleaning or business checks before update
            if not kwargs.get("vcgjnmbr"):
                return {
                    "success": False,
                    "message": "Voucher Number is missing for update.",
                }

            # DAL Call
            result = JournalDAL.update_journal_entry(**kwargs)

            # Additional mapping if needed based on status code
            status_code = result.get("status")

            if status_code == 101:
                result["message"] = "Journal entry modified successfully."
            elif status_code == 2003:
                result["message"] = (
                    "Conflict: Another user has modified this record. Please refresh."
                )
            elif status_code == 2004:
                result["message"] = "Security Error: User log failure."

            return result

        except Exception as e:
            print(f"--- BLL ERROR (Update Journal): {str(e)} ---")
            return {"success": False, "message": f"BLL Update Error: {str(e)}"}

    @staticmethod
    def get_journal_detail(journal_id):
        """
        Fetch single journal record for editing.
        (Note: Ensure your DAL has a matching method if needed)
        """
        try:
            # Agar individual detail ki SP hai to yahan call hogi
            # Filhal list se hi data filter kiya ja sakta hai client-side par
            pass
        except Exception as e:
            print(f"--- BLL ERROR (Journal Detail): {str(e)} ---")
            return None
