from xleapp import Artifact, Search
from xleapp.helpers.db import dict_from_row


class CalendarList(Artifact, category="Calendar", label="Calendar List"):
    def __post_init__(self) -> None:
        self.report_headers = (
            "Title",
            "Flags",
            "Color",
            "Symbolic Color Name",
            "External ID",
            "Self Identity Email",
        )

    @Search("**/Calendar.sqlitedb")
    def process(self) -> None:
        for fp in self.found:
            cursor = fp().cursor()
            cursor.execute(
                """
                    select
                    title,
                    flags,
                    color,
                    symbolic_color_name,
                    external_id,
                    self_identity_email
                    from Calendar
                """,
            )

            all_rows = cursor.fetchall()
            if all_rows:
                for row in all_rows:
                    row_dict = dict_from_row(row)
                    self.data.append(tuple(row_dict.values()))
