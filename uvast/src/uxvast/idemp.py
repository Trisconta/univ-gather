#!/usr/bin/env python3
""" itemp.py -- Itempotent json operations.

Example:
	python3 idemp.py ../../../uvast/uv-json/cldr-s-iso3166.json | grep :::
should show:
	::: detected key: **type**
"""

import sys
import os.path
import json


def main():
    code = do_script(sys.argv[1:])
    if code is None:
        print("Usage: python3 {__file__} [options] [file1.json ...]")
    sys.exit(0 if code is None else code)


def do_script(args):
    param = args
    if param:
        do_run(param)
    else:
        do_run(["--stdin"])
    return 0

def do_run(param):
    for fname in param:
        if fname == "--stdin":
            jsin = JsonParser(name="(stdin)")
        else:
            jsin = JsonParser(origin=fname, name="1(json)")
        isok = do_test(jsin)
        assert isok, fname

def do_test(jsin):
    """ Simple json input testing. """
    assert len(jsin.get_data()) == 0, jsin.name
    jsin.set_keys(["type"])
    jsin.load()
    data = jsin.get_data()
    jsout = JsonParser(data, name=jsin.name + "(out)")
    print(jsout.to_json())
    print(f"::: detected key: **{jsin.key_field()}**")
    return True


class JsonParser:
    """ Json generic parser. """
    def __init__(self, data=None, origin="", name="J"):
        self.name = name
        self._data = [] if data is None else data
        self._bykey, self._keys = None, {
            "AId": "Identification",
            "Type": "type",
        }
        self._found_keys = []
        self._origin = origin
        self._rpath = os.path.realpath(origin) if origin else ""
        if not isinstance(self._data, list):
            raise TypeError(f"Provide a list: {name}, got {type(self._data).__name__}")

    def get_data(self):
        return self._data

    def key_field(self):
        assert self._found_keys, self.name
        return self._found_keys[0]

    def origin(self) -> tuple:
        return self._origin, self._rpath

    def set_keys(self, dct):
        """ Set keying: if 'dct' is a list, they will be just ordered. """
        if isinstance(dct, dict):
            self._keys = dct
            return True
        assert isinstance(dct, (list, tuple)), self.name
        self._keys = {}
        for idx, name in enumerate(dct, 1):
            self._keys[name] = str(idx)
        return True

    def save(self):
        return self.save_to(self._origin)

    def save_to(self, out_path):
        if not out_path:
            return False
        with open(out_path, "w", encoding="utf-8") as fdout:
            fdout.write(self.to_json())
        return True

    def load(self):
        origin = self._origin
        if origin:
            with open(origin, "r", encoding="utf-8") as fdin:
                astr = fdin.read()
        else:
            astr = sys.stdin.read()
        self._load_json_list(astr)
        return True

    def to_json(self, indent=2, ascii_only=False):
        astr = json.dumps(
            self._data,
            ensure_ascii=ascii_only,
            indent=indent,
            sort_keys=True,
        )
        return astr + "\n"

    def _load_json_list(self, json_data):
        """ Accepts either:
          - a JSON string representing a list
          - a Python list already loaded
        Converts it into the canonical internal dict structure.
        """
        if isinstance(json_data, list):
            self._data = json_data
            return True
        if not isinstance(json_data, str):
            raise TypeError(f"Expected a string: {self.name}")
        try:
            json_data = json.loads(json_data)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON input: {exc}")
        lst, dct = self._list_to_internal(json_data)
        self._data, self._bykey = lst, dct
        return True

    def _list_to_internal(self, items):
        """ Convert a list of dicts into the canonical internal structure.
        You can adjust the schema mapping here.
        """
        result, e_keys = {}, list(self._keys)
        self._found_keys = []
        for entry in items:
            if not isinstance(entry, dict):
                raise TypeError(f"Each list item must be a dict: {self.name}")
            key = None
            if self._found_keys:
                key = entry.get(self._found_keys[0])
            else:
                a_key = None
                for a_key in e_keys:
                    try:
                        key = entry[a_key]
                    except KeyError:
                        continue
                    break
                if a_key is not None:
                    self._found_keys.append(a_key)
            if key is None:
                raise ValueError(f"Missing required key field: {e_keys}")
            result[key] = entry
        return items, result


if __name__ == "__main__":
    main()
