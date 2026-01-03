#!/usr/bin/env python3

""" Simple JSON dir loader
"""

import sys
import os
import json
try:
    from uxvast.genclass import GenData
except ModuleNotFoundError:
    from genclass import GenData

DEF_DIR = "../../uv-json"	# cldr-s-iso3166.json

def main():
    do_script(sys.argv[1:])

def do_script(args):
    j_data = GenData()
    mydir = os.path.realpath(DEF_DIR)
    param = args if args else [mydir]
    a_dir = param[0]
    ldr = JSONDirectoryLoader(a_dir)
    ldr.load()
    what = ldr.get_data()
    astr = j_data.json_data(what, ensure_ascii=True)
    print(astr)


class JSONDirectoryLoader:
    """ Load all .json files under base_dir (non-recursive).
    Returns a dictionary indexed by the basename of each file.
    """
    def __init__(self, base_dir, do_load=True):
        self.base_dir = base_dir
        self._cache = None
        if do_load:
            self.load()

    def get_data(self):
        return self._cache

    def load(self):
        """ Load all JSON files and cache the result.
        """
        if self._cache is not None:
            return self._cache
        result = {}
        for name in sorted(os.listdir(self.base_dir)):
            if not name.endswith(".json"):
                continue
            full_path = os.path.join(self.base_dir, name)
            with open(full_path, "r", encoding="utf-8") as fdin:
                result[name] = json.load(fdin)
        self._cache = result
        return result

    def get(self, filename):
        """ Retrieve a specific JSON file by its basename.
        """
        data = self.load()
        return data.get(filename)

    def keys(self):
        """ Return the list of JSON basenames.
        """
        return list(self.load().keys())

    def items(self):
        """ Iterate over (basename, parsed_json).
        """
        return self.load().items()


if __name__ == "__main__":
    main()
