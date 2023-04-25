import plistlib

from xleapp import Artifact, Search, WebIcon
from xleapp.templating.html import NavigationItem


class CellularWirless(Artifact, category="Celluar Wireless", label="Celluar Wireless"):
    def __post_init__(self) -> NavigationItem:
        self.web_icon = WebIcon.BAR_CHART
        self.report_headers = ("Key", "Value", "Source")

    @Search("**/com.apple.commcenter.plist")
    @Search("**/com.apple.commcenter.device_specific_nobackup.plist")
    def process(self) -> None:
        device_info = self.device

        for fp in self.found:
            pl = plistlib.load(fp())
            for key, value in pl.items():
                tmp_key = key
                self.data.append((tmp_key, value))
                if tmp_key in (
                    "ReportedPhoneNumber",
                    "CDMANetworkPhoneNumberICCID",
                    "imei",
                    "LastKnownICCID",
                    "meid",
                ):
                    if tmp_key in ["imei", "meid"]:
                        tmp_key = tmp_key.upper()
                    device_info.update({tmp_key: value})
