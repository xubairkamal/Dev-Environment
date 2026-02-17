from core_app.layers.base_dal import BaseDAL


class TransactionDAL(BaseDAL):
    """
    Transaction-specific Data Access Layer.
    Inherits execute_sp and execute_sp_single_row from BaseDAL.
    Fully synced with UserDAL pattern and sp_Trans_GetList.
    """

    @staticmethod
    def get_cash_book_data(service_id, from_date, to_date, search_term=""):
        """
        Fetches transactions for the Cash Book using the new sp_Trans_GetList.
        Parameters: @ServiceID, @FromDate, @ToDate, @SearchTerm
        """
        params = [service_id, from_date, to_date, search_term]
        # Calling the SP you provided earlier
        return BaseDAL.execute_sp("sp_Trans_GetList", params)

    @staticmethod
    def insert_cash_entry(
        service_id, date, account_id, description, amount, created_by
    ):
        """
        Inserts a new cash transaction.
        Note: Ensure sp_Transactions_Insert exists in DB.
        """
        params = (service_id, date, account_id, description, amount, created_by)
        result = BaseDAL.execute_sp_single_row("sp_Transactions_Insert", params)

        if result and str(result.get("status", "")).lower() == "success":
            return {
                "status": "success",
                "message": "Transaction saved successfully!",
                "new_id": result.get("newid"),
            }

        error_msg = result.get("message") if result else "Failed to save transaction."
        return {"status": "error", "message": error_msg}

    @staticmethod
    def update_transaction(
        service_id,
        trans_id,
        date,
        account_id,
        description,
        amount,
        version_bin,
        changed_by,
    ):
        """
        Updates transaction details with concurrency check.
        @version_bin is the TIMESTAMP from SQL Server.
        """
        params = (
            service_id,
            trans_id,
            date,
            account_id,
            description,
            amount,
            version_bin,
            changed_by,
        )
        result = BaseDAL.execute_sp_single_row("sp_Transactions_Update", params)

        if result and str(result.get("status", "")).lower() == "success":
            return {"status": "success", "message": "Transaction updated!"}

        # Concurrency handling: if DB returns a specific message
        msg = (
            result.get("message")
            if result
            else "Update failed (Concurrency or DB error)."
        )
        return {"status": "error", "message": msg}

    @staticmethod
    def delete_transaction(service_id, trans_id, version_bin, requested_by):
        """
        Soft deletes or cancels a transaction.
        """
        params = (service_id, trans_id, version_bin, requested_by)
        result = BaseDAL.execute_sp_single_row("sp_Transactions_Delete", params)

        if result and str(result.get("status", "")).lower() == "success":
            return {"status": "success", "message": "Transaction deleted!"}

        msg = result.get("message") if result else "Delete failed."
        return {"status": "error", "message": msg}

    @staticmethod
    def get_lookup_data(lookup_type, search_term=""):
        """
        Common lookup for transaction dropdowns (Accounts, Depts etc).
        Returns format: [{'id': '1', 'text': 'Cash Account'}]
        """
        params = [lookup_type, search_term]
        raw_data = BaseDAL.execute_sp("sp_Common_GetLookup", params)

        # Mapping raw SQL columns to Select2 format
        return [
            {
                "id": str(row.get("id") or row.get("ID") or ""),
                "text": str(row.get("text") or row.get("TEXT") or "No Name"),
            }
            for row in raw_data
        ]
