from core_app.modules.transaction.consolidated_dal import ConsolidatedDAL


class ConsolidatedBLL:
    @staticmethod
    def get_consolidated_context(service_id, from_date, to_date):
        raw_data = ConsolidatedDAL.get_report_data(service_id, from_date, to_date)

        final_data = {"opening_balance": "0.00", "account_data": [], "totals": {}}

        if raw_data:
            # Index 0: Opening Balance
            if len(raw_data) > 0 and raw_data[0]:
                # SP return kar rahi hai column name 'OpeningBalance'
                final_data["opening_balance"] = raw_data[0][0].get("OpeningBalance", 0)

            # Index 1: Account Table Records (Entertainment, Fees etc)
            if len(raw_data) > 1:
                final_data["account_data"] = raw_data[1]

            # Index 2: Grand Totals (Footer labels)
            if len(raw_data) > 2 and raw_data[2]:
                final_data["totals"] = raw_data[2][0]

        return final_data
