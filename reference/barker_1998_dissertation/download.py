"""Download Barker & Szpakowicz 1998 (ACL paper) from ACL Anthology."""

import urllib.request
from pathlib import Path

URL = "https://aclanthology.org/P98-1015.pdf"
DEST = Path(__file__).parent / "barker_szpakowicz_1998.pdf"


def main():
    if DEST.exists():
        print(f"Already downloaded: {DEST}")
        return
    print(f"Downloading {URL} ...")
    urllib.request.urlretrieve(URL, DEST)
    print(f"Saved to {DEST}")


if __name__ == "__main__":
    main()
