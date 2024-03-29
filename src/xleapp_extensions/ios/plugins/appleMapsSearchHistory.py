import plistlib

from xleapp import Artifact, Search


class AppleMapsSearchHistory(
    Artifact, category="Locations", label="Apple Maps Search History"
):
    def __post_init__(self) -> None:
        self.report_headers = ("Tempstamp", "Search Entry")
        self.timeline = True

    @Search(
        (
            "*private/var/mobile/Containers/Data/Application/*/Library/Maps/"
            "GeoHistory.mapsdata"
        ),
    )
    def process(self) -> None:
        for fp in self.found:
            plist_content = plistlib.load(fp())
            for entry in plist_content["MSPHistory"]["records"]:
                search_history = plist_content["MSPHistory"]["records"][entry]
                content = search_history.get("contents")
                if content:
                    content = content.decode("UTF-8", "ignore")
                else:
                    content = None
                timestamp = search_history.get("modificationDate")
                formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                if content:
                    if len(content) < 300:
                        id_search_entry = content.split("\n")
                        search_entry = id_search_entry[1].split('"')
                        search_entry_split = str(search_entry[0]).split("\x12")
                        search_entry_filtered = list(filter(None, search_entry_split))
                        self.data.append(
                            (formatted_timestamp, ", ".join(search_entry_filtered)),
                        )
