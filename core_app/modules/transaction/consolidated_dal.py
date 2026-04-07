from django.db import connection
from core_app.layers.base_dal import BaseDAL


class ConsolidatedDAL(BaseDAL):
    @staticmethod
    def get_report_data(service_id, from_date, to_date):
        results = []
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC [dbo].[sp_Report_ConsolidatedCashBook] %s, %s, %s",
                    [service_id, from_date, to_date],
                )

                # 1. Opening Balance Set
                results.append(ConsolidatedDAL.dictfetchall(cursor))

                # 2. Account Details Set
                if cursor.nextset():
                    results.append(ConsolidatedDAL.dictfetchall(cursor))

                # 3. Grand Totals Set
                if cursor.nextset():
                    results.append(ConsolidatedDAL.dictfetchall(cursor))

            return results
        except Exception as e:
            print(f"--- DAL ERROR: {str(e)} ---")
            return [[], [], []]

    @staticmethod
    def dictfetchall(cursor):
        if cursor.description is None:
            return []
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
