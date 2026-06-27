"""Download Reed & Kellogg texts from Project Gutenberg."""

import urllib.request
from pathlib import Path

TEXTS = [
    ("https://www.gutenberg.org/cache/epub/7188/pg7188.txt",
     "higher_lessons_in_english.txt"),
    ("https://www.gutenberg.org/cache/epub/7010/pg7010.txt",
     "graded_lessons_in_english.txt"),
]

DIR = Path(__file__).parent


def main():
    for url, filename in TEXTS:
        dest = DIR / filename
        if dest.exists():
            print(f"Already downloaded: {dest}")
            continue
        print(f"Downloading {url} ...")
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req) as resp:
                dest.write_bytes(resp.read())
            print(f"Saved to {dest}")
        except Exception as e:
            print(f"Failed ({e}). Download manually from: {url}")


if __name__ == "__main__":
    main()
