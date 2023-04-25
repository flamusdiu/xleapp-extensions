from xleapp import Artifact, Search, WebIcon


class DhcpHotspotClients(Artifact, category="DHCP", label="Hotspot Clients"):
    def __post_init__(self) -> None:
        self.web_icon = WebIcon.SETTINGS

    @Search("**/private/var/db/dhcpd_leases*")
    def process(self) -> None:
        for fp in self.found:
            for line in fp():
                cline = line.strip()
                if cline not in ["{", "}"]:
                    ll = cline.split("=")
                    self.data.append(ll)
