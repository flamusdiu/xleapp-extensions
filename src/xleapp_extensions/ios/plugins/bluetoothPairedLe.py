from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.db import dict_from_row


class BluetoothPairedLe(Artifact, category="Bluetooth", label="Bluetooth Paired LE"):
    def __post_init__(self) -> None:

        self.report_headers = (
            "UUID",
            "Name",
            "Name Origin",
            "Address",
            "Resolved Address",
            "Last Connection Time",
        )

    @Search("**/com.apple.MobileBluetooth.ledevices.paired.db")
    def process(self):
        for fp in self.found:
            cursor = fp().cursor()

            cursor.execute(
                """
                    select
                    Uuid,
                    Name,
                    NameOrigin,
                    Address,
                    ResolvedAddress,
                    LastSeenTime,
                    LastConnectionTime
                    from
                    PairedDevices
                """,
            )

            all_rows = cursor.fetchall()
            if all_rows:
                for row in all_rows:
                    row_dict = dict_from_row(row)
                    self.data.append(tuple(row_dict.values()))
