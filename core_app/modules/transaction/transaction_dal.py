from core_app.layers.base_dal import BaseDAL


class TransactionDAL(BaseDAL):
    """
    Transaction-specific Data Access Layer.
    """

    @staticmethod
    def get_cash_book_data(service_id, from_date, to_date, search_term=""):
        params = [service_id, from_date, to_date, search_term]
        return BaseDAL.execute_sp("sp_Trans_GetList", params)

    @staticmethod
    def insert_cash_entry(**kwargs):
        """
        Calls spTransAdd with 20 parameters.
        Handling potential 'None' results from BaseDAL.
        """
        params = [
            kwargs.get("user_code"),  # @pINUSCODE
            kwargs.get("vt_code"),  # @pINVTCODE
            0,  # @pBITRVNMB
            kwargs.get("date"),  # @pDTTRDATE
            kwargs.get("ac_code"),  # @pINACCODE
            kwargs.get("dp_code"),  # @pINDPCODE
            kwargs.get("title", ""),  # @pVCTRTITL
            kwargs.get("description", ""),  # @pVCTRDESC
            kwargs.get("amount"),  # @pMNTRAMNT
            kwargs.get("cc_code"),  # @pINCCCODE
            kwargs.get("invoice", ""),  # @pVCTRINVC
            "",  # @pVCTRCHQD
            "",  # @pVCTRMNTH
            kwargs.get("am_code"),  # @pINAMCODE
            0,  # @pINVNCODE
            kwargs.get("ys_code", 10),  # @pINYSCODE
            0,  # @pINTRVRSN
            0,  # @pINTRCODE (Output)
            "",  # @pVCTRNMBR (Output)
            0,  # @pRetVal (Output)
        ]

        # Execute SP
        result = BaseDAL.execute_sp_single_row("spTransAdd", params)

        # Agar result None hai, to iska matlab SP ne SELECT statement execute nahi ki
        if not result:
            return {
                "status": "error",
                "message": "Database did not return a response. Please ensure the Stored Procedure ends with a SELECT statement for output parameters.",
            }

        # Normalize keys to lowercase for safety
        res_normal = {str(k).lower(): v for k, v in result.items()}

        retval = res_normal.get("pretval")

        if retval == 101:
            return {
                "status": 101,
                "message": "Transaction saved successfully!",
                "new_id": res_normal.get("pintrcode"),
                "voucher_no": res_normal.get("pvctrnmbr"),
            }

        # Specific Error Mapping
        error_map = {
            2002: "Insufficient Funds in the selected Cost Center.",
            2001: "The record has not been added (Database Error).",
            2004: "User Log Failure.",
        }

        msg = error_map.get(retval, f"Failed to save transaction (Code: {retval})")
        return {"status": retval, "message": msg}

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
        return {
            "status": "error",
            "message": result.get("message") if result else "Update failed.",
        }

    @staticmethod
    def delete_transaction(service_id, trans_id, version_bin, requested_by):
        params = (service_id, trans_id, version_bin, requested_by)
        result = BaseDAL.execute_sp_single_row("sp_Transactions_Delete", params)
        if result and str(result.get("status", "")).lower() == "success":
            return {"status": "success", "message": "Transaction deleted!"}
        return {
            "status": "error",
            "message": result.get("message") if result else "Delete failed.",
        }

    @staticmethod
    def get_lookup_data(lookup_type, search_term=""):
        params = [lookup_type, search_term]
        raw_data = BaseDAL.execute_sp("sp_Common_GetLookup", params)
        return [
            {
                "id": str(row.get("id") or row.get("ID") or ""),
                "text": str(row.get("text") or row.get("TEXT") or "No Name"),
            }
            for row in raw_data
        ]
