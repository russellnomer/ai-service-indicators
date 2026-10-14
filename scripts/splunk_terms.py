#!/usr/bin/env python3
"""Print a Splunk keyword prefilter covering every pattern in data/ai_services.csv.

Uses the longest wildcard-free part of each pattern as an indexed search term, so a
search like `index=dns (<terms>) | lookup ai_services ...` only reads candidate events.
Regenerate it whenever the dataset changes.
"""

import csv
import re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "ai_services.csv"


def term(pattern: str) -> str:
    return max(pattern.split("*"), key=len).strip(".-")


def main() -> None:
    with DATA.open(newline="") as f:
        terms = sorted({term(r["host_pattern"]) for r in csv.DictReader(f)})
    # Drop terms that already contain another term at a label boundary
    # (copilot.com.cdn.cloudflare.net is found by copilot.com; bedrock-runtime-fips by bedrock-runtime)
    kept = [t for t in terms
            if not any(o != t and re.search(rf"(^|[.-]){re.escape(o)}([.-]|$)", t) for o in terms)]
    print("(" + " OR ".join(kept) + ")")


if __name__ == "__main__":
    main()
