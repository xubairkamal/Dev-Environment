from core_app.layers.base_dal import BaseDAL


class TransactionDAL(BaseDAL):
    @staticmethod
    def get_cash_book_list(service_id, from_date, to_date, search=""):
        """
        SP [spTransGrid] call karta hai.
        Parameters: ServiceID, FromDate, ToDate, SearchString, ReturnValue (Output)
        """
        # SP expects: @pINAMCODE, @pFROM, @pTO, @pSEARCH, @pRETVAL OUTPUT
        # Hamara BaseDAL execute_sp handle karega inhein
        params = (service_id, from_date, to_date, search)

        # Note: Agar aapka BaseDAL generic hai, toh SP ka naam yahan change karein
        return BaseDAL.execute_sp("spTransGrid", params)
