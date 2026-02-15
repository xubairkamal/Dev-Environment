from core_app.modules.transaction.transaction_dal import TransactionDAL


class TransactionBLL:
    @staticmethod
    def get_transactions(service_id, from_date, to_date, search=""):
        try:
            # SP spTransGrid call ho rahi hai DAL ke zariye
            return TransactionDAL.get_cash_book_list(
                service_id, from_date, to_date, search
            )
        except Exception as e:
            print(f"--- BLL Error (spTransGrid): {str(e)} ---")
            return []
