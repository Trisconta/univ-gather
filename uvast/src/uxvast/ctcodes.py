""" CLDR Territory Codes -- from said supplementalData
"""

from pathlib import Path
import xml.etree.ElementTree as ET
import genclass


class CLDRTerritoryCodes(genclass.GenData):
    """
    Minimal, deterministic extractor for <territoryCodes> entries
    from CLDR supplementalData.xml.
    """
    def __init__(self, xml_path, tup=None):
        self.xml_path = Path(xml_path)
        self._root = None
        self._contexts = tup
        assert tup is not None, "tup"
        self._ctx = {
            "cldr-territories": tup[0],
        }
        self._mappings = None

    def load(self):
        """Parse the XML file and keep the root element."""
        tree = ET.parse(self.xml_path)
        self._root = tree.getroot()

    def extract(self):
        """
        Extract all <territoryCodes> entries into a list of dicts.
        Deterministic ordering: numeric code (int), then type.
        """
        if self._root is None:
            self.load()
        mappings = []
        terr_dct = self._ctx["cldr-territories"]
        for elem in self._root.iter("territoryCodes"):
            territory = elem.get("type")
            name = "@" if terr_dct is None else terr_dct.get(territory)
            entry = {
                "type": territory,	# two letter, "PT" = Portugal
                "numeric": elem.get("numeric"),
                "alpha3": elem.get("alpha3"),
            }
            if name != "@":
                entry["en-name"] = name
            mappings.append(entry)
        self._mappings = sorted(
            mappings,
            key=lambda x: (
                int(x["numeric"]) if x["numeric"] else 9999,
                x["type"],
            ),
        )
        return mappings

    def to_json(self):
        """Return the extracted mappings as a JSON string."""
        if self._mappings is None:
            self.extract()
        return self.json_data(self._mappings)

    def save_json(self, output_path) -> bool:
        """Write the JSON output to a file."""
        data = self.to_json()
        if not output_path:
            return False
        Path(output_path).write_text(data, encoding="utf-8")
        return True
