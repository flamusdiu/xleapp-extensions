import plistlib

from packaging import version
from xleapp import Artifact, Search, WebIcon


class IconScreen(Artifact, category="iOS Screens", label="Apps per screen"):
    def __post__init__(self) -> None:
        self.web_icon = WebIcon.MAXIMIZE

    @Search("**/SpringBoard/IconState.plist")
    def process(self) -> None:
        ios_version = self.device["ProductVersion"]
        if version.parse(ios_version) >= version.parse("14"):
            self.log(message=f"iOS Screen artifact not compatible with iOS {ios_version}")
            return

        for fp in self.found:
            deserialized = plistlib.load(fp())

            class Screen:
                screen_num: int = 0
                folder: str | None = ""
                bundles: list = []

                def __init__(self, icon_list: list, folder: str = "", num: int = None):
                    self.screen_num = num
                    for bundle in icon_list:
                        if isinstance(bundle, dict):
                            screen_folder = Screen(bundle, folder=bundle["displayName"])
                            self.bundles.append(screen_folder.attributes())
                        else:
                            self.bundles.append(bundle)

                def attributes(self) -> str:
                    table: list = []
                    row: list = []

                    if self.folder:
                        row.append(f"Folder:{self.folder}")
                    else:
                        table.append("<table>")
                        table.append(
                            f'<tr><td colspan="4"> Icons screen #{self.screen_num}'
                            "</td></tr>",
                        )

                    for num, bundle in enumerate(self.bundles):
                        if self.folder:
                            row.append(bundle)
                        else:
                            if isinstance(bundle, Screen):
                                row.append(bundle.attributes())
                            else:
                                row.append(bundle)

                            if num % 4 == 0:
                                table.append(
                                    f"<tr><td width = 25%>{''.join(row)}</td></tr>",
                                )
                                row.clear()

                    if not self.folder:
                        table.append("</table>")
                    return "".join(table) or "<br />".join(row)

            for screen_num, icon_list in enumerate(deserialized["iconLists"]):
                icon_screen = Screen(icon_list, num=screen_num)
                self.data.append(icon_screen.attributes())
