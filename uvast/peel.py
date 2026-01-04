
import sys
import os
import m3iso
sys.path.append(os.path.join(os.path.realpath(os.path.dirname(__file__)), "src"))
import uxvast
from uxvast import JsonParser


W_IGNORE = (
    "ZZ",	# Unknown
    "XA",	# Pseudo accents
    "XB",	# Pseudo bidi
)


def main():
    isok = consolidate_peel(
        os.path.realpath(os.path.dirname(__file__)),
    )
    assert isok, "consolidate_peel()"


def consolidate_peel(b_dir):
    dct = m3iso.ISO3166_NUMERIC
    assert isinstance(dct, dict), "m3iso numeric country dictionary"
    cldr_simple = os.path.join(b_dir, "uv-json/cldr-s-iso3166.json")
    territ = JsonParser(origin=cldr_simple, name="simple")
    territ.set_keys(["type"])
    plain = JsonParser([dct], name="raw-country-a3-list")
    plain_map = dict(dct)
    isok = territ.load()
    assert isok, territ.name
    dct = territ.by_key()
    new = JsonParser(
        [
            territ.get_data(),
            plain.get_data(),
            dct,
            plain_map,
        ],
        name="peel",
    )
    isok = comment_check(new)
    return isok


def comment_check(new):
    """ Comment bundled structure, said 'new'.

Hint:
	[key for key in m3iso.ISO3166_NUMERIC
	if "PORTUGAL" in m3iso.ISO3166_NUMERIC[key].upper()]
yields ['620']
    """
    astr = new.to_json()
    assert astr, new.name
    one, plain, dct, plain_map = new.get_data()
    num_to_english = plain[0]	# "620": "Portugal", ...etc.
    for two in sorted(dct):
        item = dct[two]
        s_num, en_name = item["numeric"], item["en-name"]
        if en_name is None:
            continue
        lst = [
            key for key in num_to_english
            if friendly_ascii7(en_name.upper()) == num_to_english[key].upper()
        ]
        if not lst:
            lst = [
                key for key in num_to_english
                if en_name.upper() in num_to_english[key].upper()
            ]
        if len(lst) == 1:
            if s_num in ("826",):
                continue
            assert s_num == lst[0], f"Must match ({s_num}): {item}, against: {lst}"
            continue
        if two in W_IGNORE:
            continue
        if en_name.startswith("St."):
            # Ignore small islands...
            continue
        print(two, lst, short_show(item, plain_map))
        assert not lst, two
    return True

def short_show(item, plain_map):
    mapa = plain_map.get(item["numeric"])
    astr = f"{repr(mapa)}"
    for key, val in item.items():
        if val is None:
            val = "-"
        part = f"{key}: {friendly_ascii7(val)}"
        if astr:
            astr += ", "
        astr += part
    return astr

def friendly_ascii7(astr):
    assert isinstance(astr, str), "Only strings to ASCII-7bit here!"
    s_val = ''.join(
        [
            friendly_chr(uchr, ".") for uchr in astr
        ]
    )
    return s_val

def friendly_chr(uchr, safe="."):
    """ Fridendly ASCII char
	It also deviates, and allows chars such as "\u00C5land"
    """
    if uchr == "\u00C5":
        return "A"
    astr = uchr if uchr <= "~" else "."
    return astr


if __name__ == "__main__":
    main()
