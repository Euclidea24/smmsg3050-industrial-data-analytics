"""Download the six UCI datasets used by the SpaDC study, verify, extract.

Usage
-----
    python scripts/download_data.py                      # small datasets only (~40 MB)
    python scripts/download_data.py --include-hydraulic-raw   # + 17 sensor curves (530 MB)
    python scripts/download_data.py --verify-only        # just check what is already there

Why a script instead of committing everything?
    ``data/raw/hydraulic/PS*.txt`` alone is 530 MB, above GitHub's 100 MiB line.
    The repo keeps the authentic small files and this script reproduces the rest,
    so a fresh clone is fully reproducible.

Every download is checked against the SHA-256 that ``docs/data-sources.md`` records.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(os.path.dirname(HERE), "data", "raw")

BASE = "https://archive.ics.uci.edu/static/public/%s/%s"

# key: (uci id, zip slug, files we expect inside)
DATASETS = {
    "secom": ("179", "secom.zip", ["secom.data", "secom_labels.data", "secom.names"]),
    "steel_plates": ("198", "steel+plates+faults.zip", ["Faults.NNA", "Faults27x7_var"]),
    "wine_quality": ("186", "wine+quality.zip",
                     ["winequality-red.csv", "winequality-white.csv", "winequality.names"]),
    "appliances": ("374", "appliances+energy+prediction.zip", ["energydata_complete.csv"]),
    "gas_drift": ("224", "gas+sensor+array+drift+dataset.zip", None),
    "hydraulic": ("447", "condition+monitoring+of+hydraulic+systems.zip", None),
}

# file (relative to data/raw) -> sha256, as computed on 2026-11-25
SHA256 = {
    "secom/secom.data":
        "20f0e7ee434f7dcbae0eea9ffff009a2b57f42d6b0dc9a5bd4f00782c0a3374c",
    "secom/secom_labels.data":
        "126884cf453705c9e61a903fe906f0665a3b45ce3639e621edc5c93c89627e03",
    "steel_plates/Faults.NNA":
        "08994f5b0185a8e6cc22afe9910fd36834990fb1ca30852ed79012a832fbff55",
    "wine_quality/winequality-red.csv":
        "4a402cf041b025d4566d954c3b9ba8635a3a8a01e039005d97d6a710278cf05e",
    "wine_quality/winequality-white.csv":
        "76c3f809815c17c07212622f776311faeb31e87610d52c26d87d6e361b169836",
    "appliances/energydata_complete.csv":
        "2820bf712ad0275cb18b85a05250926100d8e65ebb9f4d2d016ca91ea152a25d",
    "hydraulic/profile.txt":
        "867987ca884b2f0fd607ad3918329eba887d095af2befa21122cea518eaa584a",
}


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    print("  GET %s" % url)
    with urllib.request.urlopen(url, timeout=180) as r, open(dest, "wb") as fh:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            fh.write(chunk)
    print("      -> %s (%.1f MB)" % (dest, os.path.getsize(dest) / 1e6))


def extract(zip_path, target):
    """Extract, then flatten one redundant top-level directory if present."""
    os.makedirs(target, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(target)
    entries = [e for e in os.listdir(target) if not e.startswith(".")]
    if len(entries) == 1 and os.path.isdir(os.path.join(target, entries[0])):
        inner = os.path.join(target, entries[0])
        for name in os.listdir(inner):
            os.replace(os.path.join(inner, name), os.path.join(target, name))
        os.rmdir(inner)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--include-hydraulic-raw", action="store_true",
                    help="also download the 17 per-cycle sensor curves (530 MB)")
    ap.add_argument("--verify-only", action="store_true")
    args = ap.parse_args()

    tmp = os.path.join(RAW, "_zips")
    os.makedirs(tmp, exist_ok=True)
    failed = []

    for key, (uci_id, slug, files) in DATASETS.items():
        target = os.path.join(RAW, key if key != "gas_drift" else "gas_drift")
        if key == "hydraulic" and not args.include_hydraulic_raw:
            print("[%s] skipped (pass --include-hydraulic-raw to fetch 530 MB)" % key)
            continue
        if args.verify_only:
            continue
        print("[%s] UCI %s" % (key, uci_id))
        zpath = os.path.join(tmp, slug)
        try:
            download(BASE % (uci_id, slug), zpath)
            extract(zpath, target)
        except Exception as exc:  # noqa: BLE001
            failed.append((key, str(exc)))
            print("      !! %s" % exc)

    print("\nverifying checksums ...")
    for rel, expect in SHA256.items():
        path = os.path.join(RAW, rel.replace("/", os.sep))
        if not os.path.exists(path):
            print("  MISSING  %s" % rel)
            continue
        got = sha256_of(path)
        print("  %-9s %s" % ("OK" if got == expect else "MISMATCH", rel))
        if got != expect:
            failed.append((rel, "sha256"))

    if failed:
        print("\n%d problem(s):" % len(failed))
        for k, v in failed:
            print("  - %s: %s" % (k, v))
        return 1
    print("\nall good")
    return 0


if __name__ == "__main__":
    sys.exit(main())
