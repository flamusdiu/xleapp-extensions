import json

from xleapp import Artifact, Search


class DiscordManifest(Artifact, category="Discord", label="Discord Manifest"):
    def __post_init__(self) -> None:
        pass

    @Search(
        (
            "*/private/var/mobile/Containers/Data/Application/*/Documents/"
            "RCTAsyncLocalStorage_V1/manifest.json"
        ),
    )
    def process(self) -> None:
        for fp in self.found:
            for json_data in fp():
                json_parse = json.loads(json_data)

            for key, value in json_parse.items():
                self.data.append((key, value))
