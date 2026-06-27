"""Download Yeh, Porter & Barker 2006 from UT Austin."""

import urllib.request
from pathlib import Path

URL = "http://www.cs.utexas.edu/users/mfkb/papers/aaai06-unified-approach.pdf"
DEST = Path(__file__).parent / "yeh_porter_barker_2006.pdf"


def main():
    if DEST.exists():
        print(f"Already downloaded: {DEST}")
        return
    print(f"Downloading {URL} ...")
    urllib.request.urlretrieve(URL, DEST)
    print(f"Saved to {DEST}")


if __name__ == "__main__":
    main()
