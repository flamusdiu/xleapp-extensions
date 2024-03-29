import logging
import plistlib

from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.utils import deep_get


class AppleWifiKnownNetworks(Artifact, category="Locations", label="Wifi Known Networks"):
    def __post_init__(self) -> None:
        self.description = (
            "WiFi known networks data. Dates are taken straight from the source plist."
        )
        self.report_headers = (
            "SSID",
            "BSSID",
            "Network Usage",
            "Country Code",
            "Device Name",
            "Manufacturer",
            "Serial Number",
            "Model Name",
            "Last Joined",
            "Last Auto Joined",
            "Last Updated",
            "Enabled",
            "WiFi Network Password Modification Date",
            "File",
        )
        self.report_title = "WiFi Known Networks"
        self.web_icon = WebIcon.WIFI
        self.timeline = True

    @Search("**/com.apple.wifi.plist")
    @Search("**/com.apple.wifi-networks.plist.backup")
    @Search("**/com.apple.wifi.known-networks.plist")
    @Search("**/com.apple.wifi-private-mac-networks.plist")
    def process(self):
        class KnownNetwork:
            ssid: str
            bssid: str
            net_usage: str
            country_code: str
            device_name: str = ""
            manufacturer: str = ""
            serial_number: str = ""
            model_name: str = ""
            last_joined: str
            last_updated: str
            last_auto_joined: str
            enabled: str
            wnpmd: str
            plist: str

            def __init__(self, network: dict) -> None:
                self.ssid = str(deep_get(network, "SSID_STR"))
                self.bssid = str(deep_get(network, "BSSID"))
                self.net_usage = str(deep_get(network, "networkUsage"))
                self.country_code = str(
                    deep_get(network, "80211D_IE", "IE_KEY_80211D_COUNTRY_CODE"),
                )
                self.last_updated = str(deep_get(network, "lastUpdated"))
                self.last_joined = str(deep_get(network, "lastJoined"))
                self.last_auto_joined = str(deep_get(network, "lastAutoJoined"))
                self.wnpmd = str(deep_get(network, "WiFiNetworkPasswordModificationDate"))
                self.enabled = deep_get(network, "enabled")
                self.device_name = deep_get(
                    network,
                    "WPS_PROB_RESP_IE",
                    "IE_KEY_WPS_DEV_NAME",
                )
                self.manufacturer = deep_get(
                    network,
                    "WPS_PROB_RESP_IE",
                    "IE_KEY_WPS_MANUFACTURER",
                )
                self.serial_number = deep_get(
                    network,
                    "WPS_PROB_RESP_IE",
                    "IE_KEY_WPS_SERIAL_NUM",
                )
                self.model_name = deep_get(
                    network,
                    "WPS_PROB_RESP_IE",
                    "IE_KEY_WPS_MODEL_NAME",
                )

            def attributes(self) -> tuple[str]:
                return (
                    self.ssid,
                    self.bssid,
                    self.net_usage,
                    self.country_code,
                    self.device_name,
                    self.manufacturer,
                    self.serial_number,
                    self.model_name,
                    self.last_joined,
                    self.last_updated,
                    self.last_auto_joined,
                    self.enabled,
                    self.wnpmd,
                    self.plist,
                )

        for fp in self.found:
            deserialized = plistlib.load(fp())

            try:
                for known_network in deserialized["List of known networks"]:
                    network = KnownNetwork(known_network)
                    network.plist = fp().name
                    self.data.append(network.attributes())
            except KeyError:
                self.log(logging.INFO, "-> No networks found in plist.")
