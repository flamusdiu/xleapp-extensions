import datetime
import plistlib

from xleapp import Artifact, Search, WebIcon, core_artifact


@core_artifact
class LastBuild(Artifact, category="Core", label="Build Information"):
    def __post_init__(self) -> None:
        self.web_icon = WebIcon.GIT_COMMIT

    @Search("*LastBuildInfo.plist")
    def process(self):
        device_info = self.app.device
        for fp in self.found:
            pl = plistlib.load(fp())
            for key, value in pl.items():
                self.data.append((key, value))
                if key in ["ProductVersion", "ProductBuildVersion", "ProductName"]:
                    device_info.update({key: value})


@core_artifact
class ItunesBackupInfo(Artifact, category="IOS Build", label="iTunes Backup"):
    def __post_init__(self) -> None:
        self.description = "iTunes Backup Information"

    @Search("Info.plist")
    def process(self):
        device_info = self.app.device
        for fp in self.found:
            pl = plistlib.load(fp())
            data_list = []
            for key, value in pl.items():
                if (
                    isinstance(value, str)
                    or isinstance(value, int)
                    or isinstance(value, datetime.datetime)
                ):

                    self.data.append((key, value))
                    if key in (
                        "Build Version",
                        "Device Name",
                        "ICCID",
                        "IMEI",
                        "Last Backup Date",
                        "MEID",
                        "Phone Number",
                        "Product Name",
                        "Product Type",
                        "Product Version",
                        "Serial Number",
                    ):
                        device_info.update({key: value})

                elif key == "Installed Applications":
                    data_list.append((key, ", ".join(value)))
            self.save_data(data_list)
