import json

from datetime import datetime

from xleapp import Artifact, Search
from xleapp.helpers.utils import filter_json


class IcloudMetadata(Artifact, category="iCloud Returns", label="iCloud - File Metadata"):
    def __post_init__(self) -> None:
        self.report_headers = (
            "Btime",
            "Ctime",
            "Mtime",
            "Name",
            "Last Editor Name",
            "Doc ID",
            "Parent ID",
            "Type",
            "Deleted?",
            "Size",
            "Zone",
            "Executable?",
            "Hidden?",
        )

    @Search("*/iclouddrive/Metadata.txt", file_names_only=True)
    def process(self) -> None:
        for fp in self.found:
            with open(fp()) as json_file:
                for line in json_file:
                    json_data = json.loads(line)
                    json_fields = (
                        "document_id",
                        "parent_id",
                        "name",
                        "type",
                        "deleted",
                        "mtime",
                        "ctime",
                        "btime",
                        "size",
                        "zone",
                        ("file_flags", "is_executable"),
                        ("file_flags", "is_hidden"),
                        "last_editor_name",
                        "basehash",
                    )
                    for json_parse in json_data:
                        json_dict = filter_json(json_parse, json_fields)

                        for field in json_dict:
                            if "time" in field:
                                json_dict[field] = datetime.fromtimestamp(
                                    json_dict[field] / 1000,
                                )

                            if field == "last_editor_name":
                                last_editor_name_json = json.loads(
                                    json_dict["last_editor_name"],
                                )
                                json_dict["last_editor_name"] = last_editor_name_json.get(
                                    "name",
                                    "",
                                )

                        self.data.append(tuple(json_dict.values()))
