import logging
import pathlib

from xleapp import Plugin


logger = logging.getLogger("xleapp.logfile")


class AndroidPlugin(Plugin):
    def __init__(self) -> None:
        super().__init__()

    @property
    def folder(self) -> pathlib.Path:
        """Returns path of the plugin folder"""
        return pathlib.Path(__file__).parent / "plugins"
