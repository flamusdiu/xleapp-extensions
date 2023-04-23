import plistlib

import nska_deserialize as nd

from xleapp import Artifact, Search, WebIcon


class AppItunesMeta(
    Artifact, category="Installed Apps", label="Itunes & Bundle Metadata"
):
    def __post_init__(self) -> None:
        self.description = "iTunes & Bundle ID Metadata contents for apps"

        self.report_headers = (
            "Installed Date",
            "App Purchase Date",
            "Bundle ID",
            "Item Name",
            "Artist Name",
            "Version Number",
            "Downloaded by",
            "Genre",
            "Factory Install",
            "App Release Date",
            "Source App",
            "Sideloaded?",
            "Variant ID",
            "Source File Location",
        )

    @Search("**/iTunesMetadata.plist")
    @Search("**/BundleMetadata.plist")
    def process(self) -> None:
        for fp in self.found:
            if fp.path.name == "iTunesMetadata.plist":
                pl = plistlib.load(fp())

                purchasedate = pl.get("com.apple.iTunesStore.downloadInfo", {}).get(
                    "purchaseDate",
                    "",
                )
                bundleid = pl.get("softwareVersionBundleId", "")
                itemname = pl.get("itemName", "")
                artistname = pl.get("artistName", "")
                versionnum = pl.get("bundleShortVersionString", "")
                downloadedby = (
                    pl.get("com.apple.iTunesStore.downloadInfo", {})
                    .get("accountInfo", {})
                    .get("AppleID", "")
                )
                genre = pl.get("genre", "")
                factoryinstall = pl.get("isFactoryInstall", "")
                appreleasedate = pl.get("releaseDate", "")
                sourceapp = pl.get("sourceApp", "")
                sideloaded = pl.get("sideLoadedDeviceBasedVPP", "")
                variantid = pl.get("variantID", "")
                metadata = [
                    purchasedate,
                    bundleid,
                    itemname,
                    artistname,
                    versionnum,
                    downloadedby,
                    genre,
                    factoryinstall,
                    appreleasedate,
                    sourceapp,
                    sideloaded,
                    variantid,
                    fp.path,
                ]

            if fp.path.name == "BundleMetadata.plist":
                deserialized_plist = nd.deserialize_plist(fp())
                install_date = deserialized_plist.get("installDate", "")

        self.data.append((install_date, *metadata))
