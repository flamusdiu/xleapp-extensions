import fnmatch
import functools
import logging
import pathlib
import shutil
import sqlite3
import tarfile
import typing as t

from zipfile import ZipFile

from xleapp.artifact import ArtifactError, Artifacts
from xleapp.helpers.db import open_sqlite_db_readonly
from xleapp.helpers.search import FileSearchProvider, FileSeekerBase
from xleapp.helpers.utils import is_platform_windows
from xleapp.plugins import Plugin


logger = logging.getLogger("xleapp.logfile")


class IosPlugin(Plugin):
    def __init__(self) -> None:
        super().__init__()

    @property
    def folder(self) -> pathlib.Path:
        """Returns path of the plugin folder"""
        return pathlib.Path(__file__).parent / "plugins"

    def pre_process(self, artifacts: Artifacts) -> None:
        for artifact in artifacts.data:
            # Now ready to run
            # Special processing for iTunesBackup Info.plist as it is a
            # separate entity, not part of the Manifest.db. Seeker won't find it
            if (
                artifacts.app.device["Type"] == "ios"
                and artifacts.app.extraction_type == "ITUNES"
            ):
                if artifact.name == "ITUNES_BACKUP_INFO":
                    info_plist_path = (
                        pathlib.Path(artifacts.app.input_path) / "Info.plist"
                    )
                    if not info_plist_path.exists():
                        ArtifactError("Info.plist not found for iTunes Backup!")
                    else:
                        artifacts["LAST_BUILD"].select = False
            else:
                artifacts["ITUNES_BACKUP_INFO"].select = False

    def register_seekers(self, search_providers: FileSearchProvider) -> None:
        search_providers.register_builder("ITUNES", FileSeekerItunes())


class FileSeekerItunes(FileSeekerBase):
    """Searches iTunes Backup for files."""

    manifest_db: pathlib.Path
    directory: pathlib.Path

    def __call__(
        self,
        directory_or_file,
        temp_folder,
    ) -> t.Type[FileSeekerBase]:
        self.input_path = pathlib.Path(directory_or_file)
        self.temp_folder = pathlib.Path(temp_folder)
        if self.validate:
            self.all_files = self.build_files_list()

        return self

    def build_files_list(self, folder=None) -> list:
        """Populates paths from Manifest.db files into _all_files"""

        all_files: dict[str, str] = {}
        db = open_sqlite_db_readonly(self.manifest_db)
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT
            fileID,
            relativePath
            FROM
            Files
            WHERE
            flags=1
            """,
        )
        db.row_factory = sqlite3.Row
        all_rows = cursor.fetchall()
        for row in all_rows:
            relative_path: str = row["relativePath"]
            hash_filename: str = row["fileID"]
            all_files[relative_path] = hash_filename
        db.close()

        return all_files

    def search(self, file_pattern: str):
        path_list = []

        if file_pattern.find("*") == -1:
            if is_platform_windows():
                original_location = pathlib.Path(
                    f"\\\\?\\{self.directory / file_pattern}"
                )
            else:
                original_location = self.directory / file_pattern
            path_list.append(original_location)
        else:
            matching_keys = fnmatch.filter(self._all_files, file_pattern)
            for relative_path in matching_keys:
                hash_filename = self._all_files[relative_path]

                if is_platform_windows():
                    original_location = pathlib.Path(
                        f"\\\\?\\{self.directory / hash_filename[:2] / hash_filename}"
                    )
                    temp_location = pathlib.Path(
                        f"\\\\?\\{self.temp_folder / relative_path}"
                    )
                else:
                    original_location = (
                        pathlib.Path(self.directory) / hash_filename[:2] / hash_filename
                    )
                    temp_location = pathlib.Path(self.temp_folder) / relative_path
                temp_location.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(original_location, temp_location)
                path_list.append(temp_location)

        return iter(path_list)

    def cleanup(self) -> None:
        # no cleanup for this seeker
        pass

    @functools.cached_property
    def validate(self) -> bool:
        mime: str
        input_path: pathlib.Path
        mime, input_path = self.input_path
        extract_dir = self.temp_folder / "backup"

        if mime == "dir":
            manifest_db = input_path / "Manifest.db"
            if manifest_db.exists():
                self.manifest_db = manifest_db
        elif mime in ["application/x-gzip", "application/x-tar"]:
            with tarfile.open(input_path, "r:*") as gz_or_tar_file:
                num_of_files = sum(1 for member in gz_or_tar_file if member.isreg())
                for member in gz_or_tar_file:
                    if fnmatch.fnmatch(member.name, "**/Manifest.db"):
                        logger.info(f"Manifest.db found in {repr(input_path)}...")
                        logger.info(
                            f"Extracting {num_of_files} files from backup to {repr(self.temp_folder)}"
                        )

                        gz_or_tar_file.extractall(path=extract_dir)
                        self.manifest_db = extract_dir / member.path
        elif mime == "application/zip":
            with ZipFile(input_path) as zip_file:
                num_of_files = len(zip_file.infolist())
                for member in zip_file.namelist():
                    if fnmatch.fnmatch(member, "**/Manifest.db"):
                        logger.info(f"Manifest.db found in {repr(input_path)}...")
                        logger.info(
                            f"Extracting {num_of_files} files from backup to {repr(self.temp_folder)}"
                        )
                        zip_file.extractall(path=extract_dir)
                        self.manifest_db = extract_dir / member

        if self.manifest_db:
            self.directory = self.manifest_db.parent
            return True
        return False

    @property
    def priority(self) -> int:
        return 10
