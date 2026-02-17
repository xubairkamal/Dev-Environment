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
            # search_term add kiya gaya hai taake View se aane wala 4th argument handle ho sake
            return TransactionDAL.get_cash_book_data(
                service_id, from_date, to_date, search_term
            )
        except Exception as e:
            print(f"--- BLL ERROR (Cash Book List): {str(e)} ---")
            return []

    @staticmethod
    def create_cash_entry(
        service_id, date, account_id, description, amount, created_by
    ):
        """
        Logic for creating a new cash transaction.
        Validates amount and required fields before calling DAL.
        """
        # Basic Validation
        if not date or not account_id or not amount:
            return {
                "status": "error",
                "message": "Date, Account, and Amount are required!",
            }

        try:
            # Convert amount to float and check
            if float(amount) <= 0:
                return {
                    "status": "error",
                    "message": "Amount must be greater than zero!",
                }

            return TransactionDAL.insert_cash_entry(
                service_id, date, account_id, description, amount, created_by
            )
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
        Updates an existing transaction with concurrency check (version_hex).
        """
        try:
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
            return TransactionDAL.delete_transaction(
                service_id, trans_id, version_hex, requested_by
            )
        except Exception as e:
            print(f"--- BLL ERROR (Delete Transaction): {str(e)} ---")
            return {"status": "error", "message": f"BLL Delete Error: {str(e)}"}
