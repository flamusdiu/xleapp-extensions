import plistlib

import blackboxprotobuf

from xleapp import Artifact, Search


class AppleMapsGroup(Artifact, category="Locations", label="Apple Maps Group"):
    def __post_init__(self) -> None:
        self.report_headers = ("Latitude", "Longitude")

    @Search("**/Shared/AppGroup/*/Library/Preferences/group.com.apple.Maps.plist")
    def process(self) -> None:
        for fp in self.found:
            deserialized_plist = plistlib.load(fp())
            types = {
                "1": {
                    "type": "message",
                    "message_typedef": {
                        "1": {"type": "int", "name": ""},
                        "2": {"type": "int", "name": ""},
                        "5": {
                            "type": "message",
                            "message_typedef": {
                                "1": {"type": "double", "name": "Latitude"},
                                "2": {"type": "double", "name": "Longitude"},
                                "3": {"type": "double", "name": ""},
                                "4": {"type": "fixed64", "name": ""},
                                "5": {"type": "double", "name": ""},
                            },
                            "name": "",
                        },
                        "7": {"type": "int", "name": ""},
                    },
                    "name": "",
                },
            }
            try:
                internal_deserialized_plist, _ = blackboxprotobuf.decode_message(
                    (deserialized_plist["MapsActivity"]),
                    types,
                )
            except KeyError:
                self.log(message="-> No data in Apple Maps Groups!")
                return

            latitude = internal_deserialized_plist["1"]["5"]["Latitude"]
            longitude = internal_deserialized_plist["1"]["5"]["Longitude"]

            self.data.append((latitude, longitude))
