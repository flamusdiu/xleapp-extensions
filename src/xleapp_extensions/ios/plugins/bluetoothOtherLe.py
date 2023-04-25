from xleapp import Artifact, Search
from xleapp.helpers.db import dict_from_row


class BluetoothOtherLe(Artifact, category="Bluetooth", label="Bluetooth Other LE"):
    def __post_init__(self) -> None:
        self.report_headers = ("Name", "Address", "UUID")

    @Search("**/Library/Database/com.apple.MobileBluetooth.ledevices.other.db")
    def process(self):
        for fp in self.found:
            cursor = fp().cursor()

            cursor.execute(
                """
                    SELECT
                    Name,
                    Address,
                    Uuid
                    FROM
                    OtherDevices
                    order by Name desc
                """,
            )

            all_rows = cursor.fetchall()
            if all_rows:
                for row in all_rows:
                    row_dict = dict_from_row(row)
                    self.data.append(tuple(row_dict.values()))
