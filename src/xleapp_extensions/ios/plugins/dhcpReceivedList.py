import plistlib

from xleapp import Artifact, Search


class DhcpReceivedList(Artifact, category="DHCP", label="Recevied List"):
    def __post_init__(self):
        pass

    @Search("**/private/var/db/dhcpclient/leases/en*")
    def process(self) -> None:
        for fp in self.found:
            pl = plistlib.load(fp())
            for key, value in pl.items():
                if key in [
                    "IPAddress",
                    "LeastLength",
                    "LeastStartDate",
                    "RouterHardwareAddress",
                    "RouterIPAddress",
                    "SSID",
                ]:
                    self.data.append((key, value))
