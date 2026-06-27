"""Download Allen 1983 temporal intervals paper.

Note: The ACM Digital Library may require institutional access.
If the download fails, obtain the paper through your institution or ACM.
"""

import urllib.request
from pathlib import Path

URL = "https://dl.acm.org/doi/pdf/10.1145/182.358434"
DEST = Path(__file__).parent / "allen_1983_temporal_intervals.pdf"


def main():
    if DEST.exists():
        print(f"Already downloaded: {DEST}")
        return
    print(f"Downloading {URL} ...")
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp:
            with open(DEST, "wb") as f:
                f.write(resp.read())
        print(f"Saved to {DEST}")
    except Exception as e:
        print(f"Download failed (may require ACM access): {e}")
        print("Obtain manually from: https://dl.acm.org/doi/10.1145/182.358434")


if __name__ == "__main__":
    main()
