#!/usr/bin/env python3
"""Check servers/*.json and that README.md matches them. Run from anywhere, no arguments."""

import sys

from lib import README, load_servers, render_directory, splice_readme, validate


def main() -> int:
    servers = load_servers()
    errors, warnings = validate(servers)

    readme = README.read_text(encoding="utf-8")
    if not errors and splice_readme(readme, render_directory(servers)) != readme:
        errors.append(
            "README.md is out of date. The directory is generated: add or edit a file in servers/, "
            "then run `python3 scripts/build.py --readme`. Do not edit the list in README.md by hand."
        )

    for w in warnings:
        print(f"warning: {w}")
    if errors:
        print(f"\n{len(errors)} problem(s) found:\n")
        for e in errors:
            print(f"  {e}")
        print("\nSee CONTRIBUTING.md for the entry format.")
        return 1
    print(f"OK — {len(servers)} servers, all well-formed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
