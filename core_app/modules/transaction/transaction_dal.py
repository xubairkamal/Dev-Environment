from core_app.layers.base_dal import BaseDAL


class TransactionDAL(BaseDAL):
    """
    Transaction-specific Data Access Layer.
    Using exact SP field names for parameter mapping.
    """

    @staticmethod
    def get_cash_book_data(service_id, from_date, to_date, search_term=""):
        params = [service_id, from_date, to_date, search_term]
        return BaseDAL.execute_sp("sp_Trans_GetList", params)

    @staticmethod
    def insert_cash_entry(**kwargs):
        """
        Calls spTransAdd with 20 parameters.
        Mapping using exact SP field names provided.
        """
        params = [
            kwargs.get("inuscode"),  # @pINUSCODE (From Session)
            kwargs.get("invtcode"),  # @pINVTCODE
            kwargs.get("bitrvnmb", 0),  # @pBITRVNMB
            kwargs.get("dttrdate"),  # @pDTTRDATE
            kwargs.get("inaccode"),  # @pINACCODE
            kwargs.get("indpcode"),  # @pINDPCODE
            kwargs.get("vctrtitl"),  # @pVCTRTITL
            kwargs.get("vctrdesc"),  # @pVCTRDESC
            kwargs.get("mntramnt"),  # @pMNTRAMNT
            kwargs.get("incccode"),  # @pINCCCODE
            kwargs.get("vctrinvc"),  # @pVCTRINVC
            kwargs.get("vctrchqd"),  # @pVCTRCHQD
            kwargs.get("vctrmnth"),  # @pVCTRMNTH
            kwargs.get("inamcode"),  # @pINAMCODE
            0,  # @pINVNCODE (Default 0)
            kwargs.get("inyscode"),  # @pINYSCODE
            0,  # @pINTRVRSN (New Entry is 0)
            0,  # @pINTRCODE (Output)
            "",  # @pVCTRNMBR (Output)
            0,  # @pRetVal (Output)
        ]

        result = BaseDAL.execute_sp_single_row("spTransAdd", params)
        if not result:
            return {"status": "error", "message": "No response from DB."}

        # Normalize keys for output
        res_normal = {str(k).lower(): v for k, v in result.items()}
        retval = res_normal.get("pretval")

        if retval == 101:
            return {
                "status": 101,
                "message": "Transaction saved successfully!",
                "new_id": res_normal.get("pintrcode"),
                "voucher_no": res_normal.get("pvctrnmbr"),
            }

        error_map = {
            2002: "Insufficient Funds.",
            2001: "Record not added.",
            2004: "Log Failure.",
        }
        return {"status": retval, "message": error_map.get(retval, f"Failed: {retval}")}

    @staticmethod
    def update_transaction(**kwargs):
        """
        Calls spTransEdit with 20 parameters.
        Standardized return value handling (like insert_cash_entry).
        """
        params = [
            kwargs.get("inuscode"),  # @pINUSCODE
            kwargs.get("intrcode"),  # @pINTRCODE
            kwargs.get("invtcode"),  # @pINVTCODE
            kwargs.get("vctrnmbr"),  # @pVCTRNMBR
            kwargs.get("bitrvnmb"),  # @pBITRVNMB
            kwargs.get("dttrdate"),  # @pDTTRDATE
            kwargs.get("inaccode"),  # @pINACCODE
            kwargs.get("indpcode"),  # @pINDPCODE
            kwargs.get("vctrtitl"),  # @pVCTRTITL
            kwargs.get("vctrdesc"),  # @pVCTRDESC
            kwargs.get("mntramnt"),  # @pMNTRAMNT
            kwargs.get("incccode"),  # @pINCCCODE
            kwargs.get("vctrinvc"),  # @pVCTRINVC
            kwargs.get("vctrchqd"),  # @pVCTRCHQD
            kwargs.get("vctrmnth"),  # @pVCTRMNTH
            kwargs.get("inamcode"),  # @pINAMCODE
            0,  # @pINVNCODE
            kwargs.get("inyscode"),  # @pINYSCODE
            kwargs.get("intrvrsn"),  # @pINTRVRSN
            0,  # @pRetVal (Output)
        ]

        # SQL Server execution
        result = BaseDAL.execute_sp_single_row("spTransEdit", params)

        if not result:
            return {
                "status": "error",
                "message": "No response from DB during update.",
            }

        # Normalize keys for output (consistent with insert method)
        res_normal = {str(k).lower(): v for k, v in result.items()}
        retval = res_normal.get("pretval")

        # Success handling
        if retval == 101:
            return {"status": 101, "message": "Record modified successfully."}

        # Error Mapping matching the Stored Procedure logic
        error_map = {
            2001: "Record not found or modified.",
            2002: "Insufficient Funds for this update.",
            2003: "Concurrency Error: Another user has modified this record. Please refresh.",
            2004: "Security Error: User log failure.",
        }

        return {
            "status": retval,
            "message": error_map.get(retval, f"Update failed with code: {retval}"),
        }

    @staticmethod
    def delete_transaction(service_id, trans_id, version_bin, requested_by):
        # Note: If delete also needs exact SP field names in a specific SP,
        # we can adjust the params list accordingly.
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
