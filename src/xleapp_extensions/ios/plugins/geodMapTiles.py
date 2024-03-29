import base64
import gzip
import logging
import struct
import zlib

from xleapp import Artifact, Search


logger = logging.getLogger("xleapp.logfile")


class GeodMapTiles(Artifact, category="Locations", label="GeoD Map Tiles"):
    def __post_init__(self) -> None:
        self.report_headers = (
            "Timestamp",
            "Places_from_VLOC",
            "Labels_in_tile",
            "Image",
            "Tileset",
            "Key A",
            "Key B",
            "Key C",
            "Key D",
            # "Size",
            # "ETAG"
        )

    @Search("**/com.apple.geod/MapTiles/MapTiles.sqlitedb")
    def process(self):
        def parsetcol(data) -> tuple:
            tcol_places = []
            data_size = len(data)
            if data_size >= 8:
                tcol_data_offset = struct.unpack("<I", data[4:8])[0]
                tcol_compressed_data = data[tcol_data_offset:]
                if tcol_compressed_data:
                    try:
                        tcol_places = gzip.decompress(tcol_compressed_data)
                    except (OSError, EOFError, zlib.error) as ex:
                        logger.info(
                            f"Gzip decompression error from parsetcol() - {str(ex)}",
                        )
                        tcol_places = ""
                vmp4_places = parsevmp4(data[8:tcol_data_offset])
                return vmp4_places, readvloc(tcol_places)

        def parsevmp4(data):
            num_items = struct.unpack("<H", data[6:8])[0]
            pos = 8
            for _item in range(num_items):
                item_type, offset, size = struct.unpack("<HII", data[pos : pos + 10])
                if item_type == 10:
                    item_data = data[offset : offset + size]
                    if item_data[0] == 1:
                        compressed_data = item_data[5:]
                        try:
                            places_data = zlib.decompress(compressed_data)
                        except zlib.error as ex:
                            logging.error(
                                f"Zlib decompression error from parsevmp4() - {str(ex)}",
                            )
                            places_data = ""
                    else:
                        places_data = item_data[1:]
                    return [
                        x.decode("UTF8", "ignore")
                        for x in places_data.rstrip(b"\0").split(b"\0")
                    ]
                pos += 10
            return []

        def get_hex(num):
            if num:
                return hex(num).upper()
            return ""

        def readvloc(data) -> list:
            names = []
            total_len = len(data)
            pos = 8
            while pos < total_len:
                if data[pos] < 0x80:
                    skip_len = 2
                else:
                    skip_len = 3
                end_pos = data[pos + skip_len :].find(b"\0")
                if end_pos >= 0:
                    name = data[pos + skip_len : pos + skip_len + end_pos].decode(
                        "utf8",
                        "ignore",
                    )
                    if name:
                        names.append(name)
                    pos += skip_len + end_pos + 1
                else:
                    break
            return names

        for fp in self.found:
            cursor = fp().cursor()
            cursor.execute(
                """
                SELECT datetime(access_times.timestamp, 'unixepoch') as timestamp, key_a, key_b, key_c, key_d, tileset, data, size, etag
                FROM data
                INNER JOIN access_times on data.rowid = access_times.data_pk
                """,
            )

            all_rows = cursor.fetchall()
            if all_rows:
                for row in all_rows:
                    tcol_places = ""
                    vmp4_places = ""
                    data_parsed = ""

                    data = row["data"]
                    if data:  # NULL sometimes
                        if (
                            len(data) >= 11
                            and data[:11]
                            == b"\xff\xd8\xff\xe0\x00\x10\x4a\x46\x49\x46\x00"
                        ):
                            img_base64 = base64.b64encode(data).decode("utf-8")
                            img_html = f'<img src="data:image/jpeg;base64, {img_base64}" alt="Map Tile" />'
                            data_parsed = img_html
                        elif len(data) >= 4 and data[:4] == b"TCOL":
                            vmp4_places, tcol_places = parsetcol(data)
                            vmp4_places = ", ".join(vmp4_places)
                            tcol_places = ", ".join(tcol_places)
                        elif len(data) >= 4 and data[:4] == b"VMP4":
                            vmp4_places = parsevmp4(data)
                            vmp4_places = ", ".join(vmp4_places)
                    # else:
                    # header_bytes = data[:28]
                    # hexdump = generate_hexdump(header_bytes, 5) if header_bytes else ''
                    # data_parsed = hexdump

                    self.data.append(
                        (
                            row["timestamp"],
                            tcol_places,
                            vmp4_places,
                            data_parsed,
                            get_hex(row["tileset"]),
                            get_hex(row["key_a"]),
                            get_hex(row["key_b"]),
                            get_hex(row["key_c"]),
                            get_hex(row["key_d"]),
                        ),
                    )
