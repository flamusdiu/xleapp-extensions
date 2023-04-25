import logging
import plistlib

from datetime import datetime

from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.utils import deep_get


class IcloudWifi(Artifact, category="Wifi Connections", label="iCloud Wifi Networks"):
    def __post__init__(self) -> None:
        self.web_icon = WebIcon.WIFI

    @Search("**/com.apple.wifid.plist")
    def process(self) -> None:
        class WifiNetwork:
            ssid: str = ""
            bssid: str = ""
            added_by: str = ""
            added_at: str = ""
            enabled: str = ""
            wnpmd: str = ""
            plist: str = ""

            def __init__(self, network: dict) -> None:
                self.ssid = str(deep_get(network, "SSID_STR"))
                self.bssid = str(deep_get(network, "BSSID"))
                self.enabled = deep_get(network, "enabled")
                self.added_by = str(deep_get(network, "added_by"))

                added_at = str(deep_get(network, "added_at"))

                if added_at:
                    self.added_at = str(datetime.strftime(added_at, "%b  %d %Y %H:%M:%S"))

            def attributes(self) -> tuple[str]:
                return (
                    self.bssid,
                    self.ssid,
                    self.added_by,
                    self.enabled,
                    self.added_at,
                )

        for fp in self.found:
            deserialized = plistlib.load(fp())

            try:
                for _, network_info in deserialized["values"].items():
                    network = WifiNetwork(network_info)
                    self.data.append(network.attributes())
            except KeyError:
                self.log(logging.INFO, "-> No networks found in plist.")
