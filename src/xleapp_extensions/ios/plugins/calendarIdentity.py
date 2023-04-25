from xleapp import Artifact, Search
from xleapp.helpers.db import dict_from_row


class CalendarIdentity(Artifact, category="Calendar", label="Calendar Identity"):
    def __post_init__(self) -> None:
        self.report_headers = ("Display Name", "Address", "First Name", "Last Name")
        self.timeline = True

    @Search("**/Calendar.sqlitedb")
    def process(self) -> None:
        for fp in self.found:
            cursor = fp().cursor()
            cursor.execute(
                """
                    SELECT
                    display_name,
                    address,
                    first_name,
                    last_name
                    from Identity
                """,
            )

            all_rows = cursor.fetchall()
            if all_rows:
                for row in all_rows:
                    row_dict = dict_from_row(row)
                    self.data.append(tuple(row_dict.values()))
