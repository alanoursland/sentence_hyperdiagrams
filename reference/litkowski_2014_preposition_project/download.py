"""Download Preposition Project papers."""

import urllib.request
from pathlib import Path

PAPERS = [
    ("https://www.clres.com/files/online-papers/prepwsd2013.pdf",
     "litkowski_2013_preposition_corpora.pdf"),
    ("https://aclanthology.org/W06-2106.pdf",
     "litkowski_hargraves_2006_coverage.pdf"),
]

DIR = Path(__file__).parent


def main():
    for url, filename in PAPERS:
        dest = DIR / filename
        if dest.exists():
            print(f"Already downloaded: {dest}")
            continue
        print(f"Downloading {url} ...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as resp:
                dest.write_bytes(resp.read())
            print(f"Saved to {dest}")
        except Exception as e:
            print(f"Failed ({e}). Download manually from: {url}")


if __name__ == "__main__":
    main()
