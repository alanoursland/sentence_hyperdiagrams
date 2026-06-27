"""Run all download scripts in the reference directory."""

import subprocess
import sys
from pathlib import Path

REF_DIR = Path(__file__).parent


def main():
    scripts = sorted(REF_DIR.glob("*/download.py"))
    if not scripts:
        print("No download scripts found.")
        return

    failed = []
    for script in scripts:
        name = script.parent.name
        print(f"\n{'='*60}")
        print(f"  {name}")
        print(f"{'='*60}")
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(script.parent),
        )
        if result.returncode != 0:
            failed.append(name)

    print(f"\n{'='*60}")
    print(f"  Done. {len(scripts) - len(failed)}/{len(scripts)} succeeded.")
    if failed:
        print(f"  Failed: {', '.join(failed)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
