from core_app.layers.base_dal import BaseDAL


class JournalDAL(BaseDAL):

    @staticmethod
    def get_journal_book_data(service_id, from_date, to_date, search_term=""):
        """Journal list lane ke liye"""
        params = [service_id, from_date, to_date, search_term]
        return BaseDAL.execute_sp("sp_GJournal_GetList", params)

    @staticmethod
    def insert_journal_entry(**kwargs):
        """
        Calls [dbo].[spGjrnlAdd]
        Note: Ye SP internally Debit (11) aur Credit (12) ki 2 rows insert karti hai.
        """
        params = [
            kwargs.get("inuscode"),  # @pINUSCODE
            kwargs.get("dtgjdate"),  # @pDTGJDATE
            kwargs.get("indrcode"),  # @pINDRCODE (Debit Account)
            kwargs.get("incrcode"),  # @pINCRCODE (Credit Account)
            kwargs.get("indpcode"),  # @pINDPCODE
            kwargs.get("vcgjtitl", ""),  # @pVCGJTITL
            kwargs.get("vcgjdesc", ""),  # @pVCGJDESC
            kwargs.get("mngjamnt"),  # @pMNGJAMNT
            kwargs.get("vcgjmnth", ""),  # @pVCGJMNTH
            kwargs.get("inamcode"),  # @pINAMCODE
            kwargs.get("invncode", 0),  # @pINVNCODE
            kwargs.get("inetcode", 1),  # @pINETCODE
            kwargs.get("vcgjrtyp", "GJ"),  # @pVCGJRTYP
            kwargs.get("ingjrefr", 0),  # @pINGJREFR
            kwargs.get("inyscode", 10),  # @pINYSCODE
            kwargs.get("ingjvrsn", 0),  # @pINGJVRSN
        ]

        # SP has 3 OUTPUT params: @pVCGJNMBR, @pBIGJVNMB, @pRETVAL
        result = BaseDAL.execute_sp_with_outputs("spGjrnlAdd", params, output_count=3)

        outputs = result.get("output_params", [])
        retval = outputs[2] if len(outputs) > 2 else 0

        if retval == 101:
            return {
                "success": True,
                "message": "Journal Entry saved!",
                "voucher_no": outputs[0],
                "status": retval,
            }
        return {"success": False, "message": f"Error Code: {retval}", "status": retval}

    @staticmethod
    def update_journal_entry(**kwargs):
        """
        Calls [dbo].[spGjrnlEdit]
        Handles concurrency using @pINGJVRSN
        """
        params = [
            kwargs.get("inuscode"),  # @pINUSCODE
            kwargs.get("vcgjnmbr"),  # @pVCGJNMBR
            kwargs.get("bigjvnm"),  # @pBIGJVNMB
            kwargs.get("dtgjdate"),  # @pDTGJDATE
            kwargs.get("indrcode"),  # @pINDRCODE
            kwargs.get("incrcode"),  # @pINCRCODE
            kwargs.get("indpcode"),  # @pINDPCODE
            kwargs.get("vcgjtitl", ""),  # @pVCGJTITL
            kwargs.get("vcgjdesc", ""),  # @pVCGJDESC
            kwargs.get("mngjamnt"),  # @pMNGJAMNT
            kwargs.get("vcgjmnth", ""),  # @pVCGJMNTH
            kwargs.get("inamcode"),  # @pINAMCODE
            kwargs.get("inyscode"),  # @pINYSCODE
            kwargs.get("ingjvrsn"),  # @pINGJVRSN (Current Version for check)
        ]

        # spGjrnlEdit has 1 OUTPUT: @pRETVAL
        result = BaseDAL.execute_sp_single_row("spGjrnlEdit", params)
        retval = result.get("pRETVAL") if result else 0

        error_map = {
            101: ("success", "Record modified successfully."),
            2001: ("error", "Record not found or no changes made."),
            2003: (
                "error",
                "Concurrency Error: Another user has modified this record.",
            ),
            2004: ("error", "Security Error: User log failure."),
        }

        status, message = error_map.get(retval, ("error", f"Update failed ({retval})"))

        return {"success": status == "success", "message": message, "status": retval}
