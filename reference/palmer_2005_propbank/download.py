"""Download Palmer, Gildea & Kingsbury 2005 PropBank paper."""

import urllib.request
from pathlib import Path

URL = "https://www.cs.rochester.edu/~gildea/palmer-propbank-cl.pdf"
DEST = Path(__file__).parent / "palmer_2005_propbank.pdf"


def main():
    if DEST.exists():
        print(f"Already downloaded: {DEST}")
        return
    print(f"Downloading {URL} ...")
    urllib.request.urlretrieve(URL, DEST)
    print(f"Saved to {DEST}")


if __name__ == "__main__":
    main()
