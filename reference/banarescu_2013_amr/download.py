"""Download Banarescu et al. 2013 AMR paper from ACL Anthology."""

import urllib.request
from pathlib import Path

URL = "https://aclanthology.org/W13-2322.pdf"
DEST = Path(__file__).parent / "banarescu_2013_amr.pdf"


def main():
    if DEST.exists():
        print(f"Already downloaded: {DEST}")
        return
    print(f"Downloading {URL} ...")
    urllib.request.urlretrieve(URL, DEST)
    print(f"Saved to {DEST}")


if __name__ == "__main__":
    main()
