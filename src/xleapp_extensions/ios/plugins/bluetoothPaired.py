import datetime
import plistlib

from xleapp import Artifact, Search


class BluetoothPaired(Artifact, category="Bluetooth", label="Bluetooth Paired"):
    def __post_init__(self) -> None:
        self.report_headers = (
            "Last Seen Time",
            "MAC Address",
            "Name Key",
            "Name",
            "Device Product ID",
            "Default Name",
        )
        self.timeline = True

    @Search("**/com.apple.MobileBluetooth.devices.plist")
    def process(self):
        for fp in self.found:
            pl: dict[str, dict] = plistlib.load(fp())

            for mac_address in pl.keys():
                mac_address_info = pl[mac_address]

                try:
                    lastseen = datetime.datetime.fromtimestamp(
                        int(mac_address_info.get("lastseen")),
                    ).strftime("%Y-%m-%d %H:%M:%S")
                except TypeError:
                    lastseen = None

                userkey = mac_address_info.get("UserNameKey", "")
                nameu = mac_address_info.get("Name", "")
                deviceid = mac_address_info.get("DeviceIDProduct", "")
                defname = mac_address_info.get("DefaultName", "")

                self.data.append(
                    (lastseen, mac_address, userkey, nameu, deviceid, defname),
                )
