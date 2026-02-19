from core_app.modules.transaction.transaction_dal import TransactionDAL


class TransactionBLL:
    """
    Transaction operations (CRUD) management logic.
    In charge of validating financial data before passing it to TransactionDAL.
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
        """
        # 1. Basic Validation for required fields
        required_fields = ["date", "ac_code", "amount", "dp_code", "cc_code", "vt_code"]
        for field in required_fields:
            if not kwargs.get(field):
                return {
                    "status": "error",
                    "message": f"Field '{field}' is required for transaction!",
                }

        try:
            # 2. Amount Validation & Cleaning
            try:
                amount = float(kwargs.get("amount", 0))
                if amount <= 0:
                    return {
                        "status": "error",
                        "message": "Amount must be greater than zero!",
                    }
                kwargs["amount"] = amount  # Ensure it's a float
            except (ValueError, TypeError):
                return {"status": "error", "message": "Invalid amount format."}

            # 3. Date Validation (Ensure it's not empty or malformed)
            if not kwargs.get("date"):
                return {"status": "error", "message": "Transaction date is missing."}

            # 4. Call DAL with all parameters
            # Note: DAL handles the exact sequence for spTransAdd
            result = TransactionDAL.insert_cash_entry(**kwargs)

            # 5. Handle SP Specific Business Logic Responses
            if not result:
                return {
                    "status": "error",
                    "message": "No response from database layer.",
                }

            status_code = result.get("status")

            if status_code == 101:
                result["message"] = "Transaction saved successfully."
            elif status_code == 2002:
                result["message"] = (
                    "Transaction Failed: Insufficient funds in the selected Cost Center."
                )
            elif status_code == 2001:
                result["message"] = (
                    "Database Error: The record could not be added to the ledger."
                )
            elif status_code == 2004:
                result["message"] = (
                    "Security Error: User log failure or unauthorized access."
                )

            return result

        except Exception as e:
            print(f"--- BLL ERROR (Create Cash Entry): {str(e)} ---")
            return {"status": "error", "message": f"BLL Create Error: {str(e)}"}

    @staticmethod
    def update_existing_transaction(
        service_id,
        trans_id,
        date,
        account_id,
        description,
        amount,
        version_hex,
        changed_by,
    ):
        """
        Updates an existing transaction with concurrency check.
        """
        try:
            # Basic validation
            if not trans_id or float(amount) <= 0:
                return {
                    "status": "error",
                    "message": "Invalid Transaction ID or Amount.",
                }

            return TransactionDAL.update_transaction(
                service_id,
                trans_id,
                date,
                account_id,
                description,
                amount,
                version_hex,
                changed_by,
            )
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
