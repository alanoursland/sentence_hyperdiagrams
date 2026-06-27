"""Download Barker, Porter & Clark 2001 from UT Austin."""

import urllib.request
from pathlib import Path

URL = "http://www.cs.utexas.edu/users/mfkb/papers/kcap01.pdf"
DEST = Path(__file__).parent / "barker_porter_clark_2001.pdf"


def main():
    if DEST.exists():
        print(f"Already downloaded: {DEST}")
        return
    print(f"Downloading {URL} ...")
    urllib.request.urlretrieve(URL, DEST)
    print(f"Saved to {DEST}")


if __name__ == "__main__":
    main()
