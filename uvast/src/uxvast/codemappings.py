#!/usr/bin/env python3
import sys
import os
import xml.etree.ElementTree as ET
import ctcodes
from cterritories import CLDRTerritories


def main():
    code = do_script(sys.argv[1:])
    if code is None:
        print("Usage: python3 codemappings.py supplementalData.xml")
    sys.exit(0 if code is None else code)


def do_script(args):
    param = args
    if not param:
        print("Usage: python3 codemappings.py supplementalData.xml")
        sys.exit(0)
    fname = param[0]
    del param[0]
    xml_path = os.path.realpath(fname)
    terr = os.path.join(os.path.dirname(os.path.dirname(xml_path)), "main", "en.xml")
    #print("# Territories:", terr)
    with open(terr, "r", encoding="utf-8") as fdin:
        xml_terr = fdin.read()
    cldr_t = CLDRTerritories(xml_terr, origin=terr)
    t_dict = cldr_t.as_dict()
    #print(t_dict)
    parser = ctcodes.CLDRTerritoryCodes(
        xml_path,
        (t_dict,),
    )
    print(parser.to_json())
    return 0


if __name__ == "__main__":
    main()
