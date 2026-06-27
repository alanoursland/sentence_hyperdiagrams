"""Download Clark & Porter 1997 from AAAI."""

import urllib.request
from pathlib import Path

URL = "https://cdn.aaai.org/AAAI/1997/AAAI97-057.pdf"
DEST = Path(__file__).parent / "clark_porter_1997.pdf"


def main():
    if DEST.exists():
        print(f"Already downloaded: {DEST}")
        return
    print(f"Downloading {URL} ...")
    urllib.request.urlretrieve(URL, DEST)
    print(f"Saved to {DEST}")


if __name__ == "__main__":
    main()
