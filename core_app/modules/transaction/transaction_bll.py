from core_app.modules.transaction.transaction_dal import TransactionDAL


class TransactionBLL:
    """
    Transaction operations (CRUD) management logic.
    In charge of validating financial data before passing it to TransactionDAL.
    Using exact SP field names for consistency.
    """

    @staticmethod
    def get_lookup_data(lookup_type, search_term=""):
        """
        Generic method to fetch lookup data for transactions (Accounts, Categories, etc.)
        """
        try:
            return TransactionDAL.get_lookup_data(lookup_type, search_term)
        except Exception as e:
            print(f"--- BLL ERROR (Transaction Lookup): {str(e)} ---")
            return []

    @staticmethod
    def get_cash_book_list(service_id, from_date, to_date, search_term=""):
        """
        Fetches the cash book ledger with date filtering and search term.
        """
        try:
            return TransactionDAL.get_cash_book_data(
                service_id, from_date, to_date, search_term
            )
        except Exception as e:
            print(f"--- BLL ERROR (Cash Book List): {str(e)} ---")
            return []

    @staticmethod
    def create_cash_entry(**kwargs):
        """
        Logic for creating a new cash transaction based on spTransAdd.
        Validates using exact SP field names.
        """
        # 1. Basic Validation for required SP fields
        # Note: 'user_code' and 'am_code' are handled at the View level from session
        required_fields = [
            "dttrdate",
            "inaccode",
            "mntramnt",
            "indpcode",
            "incccode",
            "invtcode",
        ]
        for field in required_fields:
            if not kwargs.get(field):
                return {
                    "status": "error",
                    "message": f"Field '{field}' is required for transaction!",
                }

        try:
            # 2. Amount Validation & Cleaning (mntramnt)
            try:
                amount = float(kwargs.get("mntramnt", 0))
                if amount <= 0:
                    return {
                        "status": "error",
                        "message": "Amount (mntramnt) must be greater than zero!",
                    }
                kwargs["mntramnt"] = amount  # Ensure it's a float
            except (ValueError, TypeError):
                return {
                    "status": "error",
                    "message": "Invalid amount format for mntramnt.",
                }

            # 3. Call DAL
            result = TransactionDAL.insert_cash_entry(**kwargs)

            # 4. Handle SP Specific Responses
            if not result:
                return {
                    "status": "error",
                    "message": "No response from database layer.",
                }

            status_code = result.get("status")
            if status_code == 101:
                result["message"] = "Transaction saved successfully."
            elif status_code == 2002:
                result["message"] = "Transaction Failed: Insufficient funds."

            return result

        except Exception as e:
            print(f"--- BLL ERROR (Create Cash Entry): {str(e)} ---")
            return {"status": "error", "message": f"BLL Create Error: {str(e)}"}

    @staticmethod
    def update_existing_transaction(**kwargs):
        """
        Updates an existing transaction based on spTransEdit.
        Handles validations for all SP parameters including concurrency (intrvrsn).
        """
        try:
            # 1. Basic Validation using SP names
            intrcode = kwargs.get("intrcode")
            mntramnt = kwargs.get("mntramnt")
            intrvrsn = kwargs.get("intrvrsn")

            if not intrcode:
                return {
                    "status": "error",
                    "message": "Transaction ID (intrcode) is required.",
                }

            if intrvrsn is None:
                return {
                    "status": "error",
                    "message": "Transaction Version (intrvrsn) is required for update.",
                }

            # 2. Amount Validation (mntramnt)
            try:
                amt = float(mntramnt)
                if amt <= 0:
                    return {
                        "status": "error",
                        "message": "Amount (mntramnt) must be greater than zero.",
                    }
                kwargs["mntramnt"] = amt
            except (ValueError, TypeError):
                return {"status": "error", "message": "Invalid amount format."}

            # 3. Call DAL for Update
            result = TransactionDAL.update_transaction(**kwargs)

            # 4. Handle SP Return Values for Update
            if not result:
                return {
                    "status": "error",
                    "message": "No response from database during update.",
                }

            status_code = result.get("status")

            if status_code == 101:
                result["message"] = "Record modified successfully."
            elif status_code == 2001:
                result["message"] = "Error: The record could not be modified."
            elif status_code == 2003:
                result["message"] = (
                    "Conflict: Another user has modified this record. Please refresh."
                )
            elif status_code == 2004:
                result["message"] = "Security Error: User log failure."
            elif status_code == 2002:
                result["message"] = "❌ Insufficient Funds for this update."

            return result

        except Exception as e:
            print(f"--- BLL ERROR (Update Transaction): {str(e)} ---")
            return {"status": "error", "message": f"BLL Update Error: {str(e)}"}

    @staticmethod
    def delete_existing_transaction(service_id, trans_id, version_hex, requested_by):
        """
        Soft delete or permanent delete logic for transactions.
        """
        try:
            if not trans_id:
                return {
                    "status": "error",
                    "message": "Transaction ID is required for deletion.",
                }

            return TransactionDAL.delete_transaction(
                service_id, trans_id, version_hex, requested_by
            )
        except Exception as e:
            print(f"--- BLL ERROR (Delete Transaction): {str(e)} ---")
            return {"status": "error", "message": f"BLL Delete Error: {str(e)}"}
