#!/usr/bin/env python3
"""blackresign.py - re-sign Black (Xbox) save profiles so they load in BLACK-XBERecomp.

Only re-signs. It does not rename profiles or fix profile checksums; use the C++ programs for that.

The last 20 bytes of a 6144 byte `Profile` file are
    HMAC-SHA1(HDKey, HMAC-SHA1(SigKey, first 6124 bytes))
and the port uses 16 zero bytes for both keys.

Usage:
    python3 blackresign.py Profile                 writes Profile.resigned
    python3 blackresign.py Profile out_file        writes out_file
    python3 blackresign.py save_folder             copies the folder to save_folder_resigned and re-signs every Profile
    python3 blackresign.py save_folder out_folder  same, with your own output folder
    python3 blackresign.py --inplace Profile       overwrites, keeping Profile.bak (also works on a folder)
    python3 blackresign.py --check Profile         only reports whether the signature is valid (exit code 1 if not)

Needs only Python 3.6 or newer, no extra packages.
"""

import hashlib
import hmac
import shutil
import sys
from pathlib import Path

SIZE = 6144
SIG = 20
ZERO_KEY = bytes(16)


def signature(body):
    first = hmac.new(ZERO_KEY, body, hashlib.sha1).digest()   # HMAC(SigKey, data)
    return hmac.new(ZERO_KEY, first, hashlib.sha1).digest()   # HMAC(HDKey, that)


def is_valid(data):
    return signature(data[:-SIG]) == data[-SIG:]


def resigned(data):
    return data[:-SIG] + signature(data[:-SIG])


def process(src, dst, check, inplace):
    """returns 0 ok, 1 invalid signature (check mode), 2 error or skipped"""
    data = src.read_bytes()
    if len(data) != SIZE:
        print(f"{src}: {len(data)} bytes, expected {SIZE}. Skipped.", file=sys.stderr)
        return 2
    valid = is_valid(data)
    if check:
        print(f"{src}: signature {'valid for the port' if valid else 'NOT valid for the port'}")
        return 0 if valid else 1
    if valid and inplace:
        print(f"{src}: already valid, nothing to change")
        return 0
    if inplace:
        shutil.copy2(src, src.with_name(src.name + ".bak"))
    dst.write_bytes(resigned(data))
    print(f"{src} -> {dst}")
    return 0


def main(argv):
    check = "--check" in argv
    inplace = "--inplace" in argv
    args = [a for a in argv if not a.startswith("--")]
    unknown = [a for a in argv if a.startswith("--") and a not in ("--check", "--inplace")]
    if unknown or not args or len(args) > 2 or ((check or inplace) and len(args) != 1) or (check and inplace):
        print(__doc__)
        return 2

    src = Path(args[0])
    if not src.exists():
        print(f"{src} does not exist", file=sys.stderr)
        return 2

    if src.is_file():
        if inplace:
            dst = src
        elif len(args) == 2:
            dst = Path(args[1])
        else:
            dst = src.with_name(src.name + ".resigned")
        return process(src, dst, check, inplace)

    # folder: every file named Profile, at any depth
    profiles = sorted(p for p in src.rglob("Profile") if p.is_file())
    if not profiles:
        print(f"no file named Profile found in {src}", file=sys.stderr)
        return 2
    out_root = src
    if not check and not inplace:
        out_root = Path(args[1]) if len(args) == 2 else src.with_name(src.name + "_resigned")
        if out_root.exists():
            print(f"{out_root} already exists, choose another output folder", file=sys.stderr)
            return 2
        if out_root.resolve() == src.resolve() or src.resolve() in out_root.resolve().parents:
            print(f"the output folder must be outside {src}", file=sys.stderr)
            return 2
        shutil.copytree(src, out_root)
    worst = 0
    for p in profiles:
        target = p if (check or inplace) else out_root / p.relative_to(src)
        worst = max(worst, process(p, target, check, inplace))
    if not check and not inplace:
        print(f"done: the copy is in {out_root}")
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
