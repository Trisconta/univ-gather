""" CLDR Territories
"""

import xml.etree.ElementTree as ET

class CLDRTerritories:
    """ Minimal converter for <territories> XML blocks into a Python dict.
    """
    def __init__(self, xml_string, origin=""):
        self.xml_string, self._origin = xml_string, origin
        self._root = None
        self._territories = None

    def load(self):
        """Parse the XML string and store the root element."""
        self._root = ET.fromstring(self.xml_string)

    def extract(self):
        """Return a dict: { territory_code: name }."""
        if self._root is None:
            self.load()
        # Loaded e.g.: <territory type="DE">Germany</territory>
        #print("CHECKING:", self._origin, self._root.findall(".//territory"))
        self._territories = {
            elem.get("type"): elem.text
            for elem in self._root.findall(".//territory")
        }
        return self._territories

    def as_dict(self):
        """Public accessor for the dictionary."""
        if self._territories is None:
            return self.extract()
        return self._territories
