"""Download Fan, Barker & Porter 2003 from UT Austin."""

import urllib.request
from pathlib import Path

URL = "http://www.cs.utexas.edu/users/mfkb/papers/ijcai03-nn.pdf"
DEST = Path(__file__).parent / "fan_barker_porter_2003.pdf"


def main():
    if DEST.exists():
        print(f"Already downloaded: {DEST}")
        return
    print(f"Downloading {URL} ...")
    urllib.request.urlretrieve(URL, DEST)
    print(f"Saved to {DEST}")


if __name__ == "__main__":
    main()
