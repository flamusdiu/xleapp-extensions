import contextlib
import json

import magic

from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.utils import filter_json


class DiscordMessages(Artifact, category="Discord", label="Discord Messages"):
    def __post_init__(self):
        self.report_headers = (
            "Timestamp",
            "Edited Timestamp",
            "Username",
            "Bot?",
            "Content",
            "Attachments",
            "User ID",
            "Channel ID",
            "Embedded Author",
            "Author URL",
            "Author Icon URL",
            "Embedded URL",
            "Embedded Script",
            "Footer Text",
            "Footer Icon URL",
            "Source File",
        )
        self.web_icon = WebIcon.MESSAGE_SQUARE

    @Search("*/com.hammerandchisel.discord/fsCachedData/*", return_on_first_hit=False)
    def process(self) -> None:
        for fp in self.found:
            mime = magic.from_file(str(fp()), mime=True)

            if mime != "text/plain":
                continue  # Checks if not text

            with open(fp()) as file_in:
                for json_data in file_in:
                    with contextlib.suppress(ValueError):
                        json_parse = json.loads(json_data)

                        if not isinstance(json_parse, list):
                            continue

                        message_json_fields = (
                            "timestamp",
                            "edited_timestamp",
                            ("author", "username"),
                            ("author", "bot"),
                            "content",
                            "attachments",
                            ("author", "id"),
                            "channel",
                            "embeds",
                        )
                        for message in json_parse:
                            message_dict = filter_json(
                                json=message, fields=message_json_fields
                            )
                            attachments = message_dict.get("attachments", "")
                            if attachments:
                                message_dict["attachments"] = "\n".join(
                                    {
                                        attachment.get("url", "")
                                        for attachment in attachments
                                    },
                                )
                            else:
                                message_dict["attachments"] = ""

                            embed_metadata = []
                            embeds = message_dict.pop("embeds", "")
                            if embeds:
                                embed_json_fields = (
                                    "url",
                                    "description",
                                    ("author", "name"),
                                    ("author", "url"),
                                    ("author", "icon_url"),
                                    ("footer", "text"),
                                    ("footer", "icon_url"),
                                )
                                for embed in embeds:
                                    embeds_dict = filter_json(embed, embed_json_fields)
                                    embed_metadata.append(list(embeds_dict.values()))
                            else:
                                embed_metadata = ["", "", "", "", "", "", ""]

                            file_path = fp.path.resolve()

                            self.data.append(
                                (
                                    *tuple(message_dict.values()),
                                    *embed_metadata,
                                    file_path,
                                ),
                            )
