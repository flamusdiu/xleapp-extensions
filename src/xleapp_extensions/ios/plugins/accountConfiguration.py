import plistlib

from unicodedata import category

from xleapp import Artifact, Search, WebIcon


class AccountConfiguration(Artifact, category="Accounts", label="Account Configuration"):
    def __post_init__(self) -> None:
        self.web_icon = WebIcon.USER

    @Search("**/com.apple.accounts.exists.plist")
    def process(self):
        for fp in self.found:
            pl = plistlib.load(fp())
            for item in pl.items():
                self.data.append(item)
