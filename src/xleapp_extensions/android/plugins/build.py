from xleapp import Artifact, Search, WebIcon, core_artifact


@core_artifact
class Build(Artifact, category="Device Info", label="Device Info"):
    def __post_init___(self) -> None:
        self.web_icon = WebIcon.TERMINAL

    @Search("*/vender/build.prop")
    def process(self):
        device_info = self.device
        device_key_info = {
            "ro.product.vendor.manufacturer": {
                "label": "Manufacturer",
                "log": "Manufacturer: ",
            },
            "ro.product.vendor.brand": {"label": "Brand", "log": "Brand:"},
            "ro.product.vendor.model": {"label": "Model", "log": "Model:"},
            "ro.product.vendor.device": {"label": "Device", "log": "Device"},
            "ro.vendor.build.version.release": {
                "label": "Android Version",
                "log": "Android version per build.props:",
            },
            "ro.vendor.build.version.sdk": {"label": "SDK", "log": "SDK:"},
            "ro.system.build.version.release": {"label": "", "log": ""},
        }

        for fp in self.found:
            with fp() as f:
                for line in f:
                    key, value = line.split("=")
                    if key in device_key_info:
                        self.data.append((device_key_info[key]["label"], value))
                        device_info.update({device_key_info[key]["label"]: value})
                        self.log(f'{device_key_info["log"]}')
