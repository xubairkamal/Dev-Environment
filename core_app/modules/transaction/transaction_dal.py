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
    def insert_cash_entry(data):
        """
        Calls spTransAdd with all 20 required parameters.
        Data dictionary must contain: inuscode, invtcode, dttrdate, inaccode, indpcode,
        vctrtitl, vctrdesc, mntramnt, incccode, inamcode, invncode, inyscode.
        """
        # Mapping parameters according to spTransAdd definition
        params = [
            data.get("inuscode"),  # @pINUSCODE
            data.get("invtcode"),  # @pINVTCODE
            0,  # @pBITRVNMB (BigInt - Output/Internal)
            data.get("dttrdate"),  # @pDTTRDATE
            data.get("inaccode"),  # @pINACCODE
            data.get("indpcode"),  # @pINDPCODE
            data.get("vctrtitl", ""),  # @pVCTRTITL
            data.get("vctrdesc", ""),  # @pVCTRDESC
            data.get("mntramnt"),  # @pMNTRAMNT
            data.get("incccode"),  # @pINCCCODE
            data.get("vctrinvc", ""),  # @pVCTRINVC
            data.get("vctrchqd", ""),  # @pVCTRCHQD
            "",  # @pVCTRMNTH (Internal)
            data.get("inamcode"),  # @pINAMCODE
            data.get("invncode"),  # @pINVNCODE
            data.get("inyscode"),  # @pINYSCODE
            0,  # @pINTRVRSN
            0,  # @pINTRCODE (Output)
            "",  # @pVCTRNMBR (Output)
            0,  # @pRetVal (Output)
        ]

        # Note: execute_sp_single_row handles the execution.
        # Ensure your BaseDAL can handle SPs with Output parameters if needed.
        result = BaseDAL.execute_sp_single_row("spTransAdd", params)

        # Checking the Return Value (101 is Success in your SP)
        retval = result.get("pretval") if result else None
        if retval == 101:
            return {
                "status": "success",
                "message": "Transaction saved successfully!",
                "new_id": result.get("pintrcode"),
                "voucher_no": result.get("pvctrnmbr"),
            }

        error_map = {2002: "Insufficient Funds", 2001: "Record not added"}
        msg = error_map.get(retval, "Failed to save transaction.")
        return {"status": "error", "message": msg}

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
