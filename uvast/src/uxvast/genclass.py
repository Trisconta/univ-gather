""" Generic class for handling json
"""

import json


class GenData:
    """ Generic class for json handling. """
    def json_data(self, obj, indent=2, ensure_ascii=False):
        assert ensure_ascii in (True, False), "ensure_ascii"
        astr = json.dumps(obj, indent=indent, ensure_ascii=ensure_ascii)
        return astr + "\n"
