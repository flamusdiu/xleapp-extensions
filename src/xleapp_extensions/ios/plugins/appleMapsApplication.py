import plistlib

import blackboxprotobuf

from xleapp import Artifact, Search, WebIcon


class AppleMapsApplication(Artifact, category="Locations", label="Apple Maps App"):
    def __post_init__(self) -> None:

        self.report_headers = ("Latitude", "Longitude")

    @Search("**/Data/Application/*/Library/Preferences/com.apple.Maps.plist")
    def process(self) -> None:
        for fp in self.found:
            pl = plistlib.load(fp())

            types = {
                "1": {"type": "double", "name": "Latitude"},
                "2": {"type": "double", "name": "Longitude"},
                "3": {"type": "double", "name": ""},
                "4": {"type": "fixed64", "name": ""},
                "5": {"type": "double", "name": ""},
            }
            protobuf = pl.get("__internal__LastActivityCamera", None)

            if protobuf:
                internal_plist, _ = blackboxprotobuf.decode_message(protobuf, types)
                latitude = internal_plist["Latitude"]
                longitude = internal_plist["Longitude"]

                self.data.append((latitude, longitude))
