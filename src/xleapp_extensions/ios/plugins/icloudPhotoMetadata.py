import base64
import io
import json
import plistlib

from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.utils import filter_json, time_factor_conversion


class IcloudPhotoMetadata(
    Artifact, category="iCloud Returns", label="iCloud Photos Metadata"
):
    def __post_init__(self) -> None:
        self.report_headers = (
            "Timestamp",
            "Row ID",
            "Record Type",
            "Decoded",
            "Title",
            "Filesize",
            "Latitude",
            "Longitude",
            "Altitude",
            "GPS Datestamp",
            "GPS Time",
            "Added Date",
            "Timezone Offset",
            "Decoded TZ",
            "Is Deleted?",
            "Is Expunged?",
            "Import Date",
            "Modification Date",
            "Filesize",
            "ID",
            "TIFF",
            "EXIF",
        )
        self.web_icon = WebIcon.CLOUD

    @Search("*/cloudphotolibrary/Metadata.txt", file_names_only=True)
    def process(self) -> None:
        class Photo:
            artifact = self.app
            id = ""
            rowid = ""
            created_timestamp = ""
            created_user = ""
            created_device = ""
            modified_timestamp = ""
            modified_user = ""
            modified_device = ""
            decoded = ""
            is_deleted = ""
            is_expunged = ""
            org_filesize = ""
            rec_mod_date = ""
            import_date = ""
            f_org_creation_date = ""
            res_org_filesize = ""
            added_date = ""
            timezoneoffse = ""
            latitude = ""
            longitude = ""
            altitude = ""
            datestamp = ""
            timestamp = ""
            vid_name = ""
            decoded_tz = ""
            title = ""
            recordtype = ""
            tiff = ""
            exif = ""

            def __init__(self, metadata: dict) -> None:
                photo_fields = (
                    "id",
                    "recordType",
                    ("created", "timestamp"),
                    ("modified", "timestamp"),
                    ("fields", "filenameEnc"),
                    ("fields", "timeZoneNameEnc"),
                    ("fields", "isDeleted"),
                    ("fields", "isExpunged"),
                    ("fields", "resOriginalFileSize"),
                    ("fields", "recordModificationData"),
                    ("fields", "addedDate"),
                    ("fields", "timeZoneOffset"),
                    ("fields", "title"),
                    ("fields", "mediaMetaDataEnc"),
                )

                photo_json_data = filter_json(metadata, photo_fields)

                self.metadata = self.parse_enc_plist(
                    self.rowid,
                    photo_json_data["mediaMetaDataEnc"],
                )

            def parse_enc_plist(self, rowid: int, encoded_pl: str) -> dict:
                decoded_pl = base64.b64decode(encoded_pl)
                self.artifact.copyfile(io.BytesIO(decoded_pl), f"{rowid}.bplist")
                pl = plistlib.loads(decoded_pl)

                pl_json_fields = (
                    "{TIFF}",
                    "{ExiF}",
                    ("{GPS}", "Latitude"),
                    ("{GPS}", "Longitude"),
                    ("{GPS}", "Altitude"),
                    ("{GPS}", "DateStamp"),
                    ("{GPS}", "Timestamp"),
                )

                return filter_json(pl, pl_json_fields)

        for fp in self.found:
            with open(fp()) as json_data:
                for line in json_data:
                    json_parse = json.loads(json_data)

                    if isinstance(json_parse, dict):
                        json_parse = json_parse.get("results")

                    for item in json_parse:
                        photo = Photo(item)
                        self.data.append(photo.metadata)
