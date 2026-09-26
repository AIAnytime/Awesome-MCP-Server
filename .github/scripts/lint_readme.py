#!/usr/bin/env python3
"""Lint the community directory in README.md.

Catches the failure modes that actually broke this file: numbered lists that collide
on every concurrent PR, duplicate entries, entries stranded below the license, tracking
parameters, and out-of-order insertions. Run it with no arguments from the repo root.
"""

import re
import sys
from pathlib import Path

README = Path(__file__).resolve().parents[2] / "README.md"

DIRECTORY_START = "## 🌍 Community directory"
DIRECTORY_END = "## 🤝 Contributing"

# - **[Name](url)** `stdio` — description...
ENTRY = re.compile(r"^- \*\*\[(?P<name>[^\]]+)\]\((?P<url>[^)]+)\)\*\*(?P<rest> .*)$")
TRANSPORT = re.compile(r"^ `(stdio|http|sse)` — ")
NUMBERED = re.compile(r"^\s*\d+\.\s")

errors: list[str] = []


def error(line_no: int, msg: str) -> None:
    errors.append(f"README.md:{line_no}: {msg}")


def main() -> int:
    lines = README.read_text(encoding="utf-8").splitlines()

    try:
        start = next(i for i, l in enumerate(lines) if l.startswith(DIRECTORY_START))
        end = next(i for i, l in enumerate(lines) if l.startswith(DIRECTORY_END))
    except StopIteration:
        print("Could not locate the community directory section. Did a heading get renamed?")
        return 1

    # Nothing but the footer may live below the license.
    for i, line in enumerate(lines[end:], start=end + 1):
        if line.startswith("## 📜 License"):
            for j, tail in enumerate(lines[i:], start=i + 1):
                if ENTRY.match(tail) or NUMBERED.match(tail):
                    error(j, "entry found below the License section — move it into a category")
            break

    category = None
    seen_names: dict[str, int] = {}
    seen_urls: dict[str, int] = {}
    previous_in_category: tuple[str, int] | None = None

    for i, line in enumerate(lines[start:end], start=start + 1):
        if line.startswith("### "):
            category = line[4:].strip()
            previous_in_category = None
            continue

        if NUMBERED.match(line):
            error(i, "numbered list item in the directory — use a `- **[Name](url)**` bullet instead")
            continue

        if line.startswith("- -") or line.startswith("--"):
            error(i, "malformed bullet")
            continue

        if not line.startswith("- "):
            continue

        match = ENTRY.match(line)
        if not match:
            error(i, "entry does not match `- **[Name](url)** `transport` — description`")
            continue

        name, url, rest = match["name"], match["url"], match["rest"]

        if category is None:
            error(i, f"entry '{name}' is not under a ### category heading")

        if not TRANSPORT.match(rest) and "not a server" not in rest:
            error(i, f"'{name}': expected a `stdio`/`http`/`sse` tag then ' — ' after the link")

        if "utm_" in line:
            error(i, f"'{name}': remove tracking parameters (utm_*) from the URL")

        key = name.lower()
        if key in seen_names:
            error(i, f"duplicate entry '{name}' (already on line {seen_names[key]})")
        seen_names[key] = i

        if url in seen_urls:
            error(i, f"'{name}': duplicate URL, already used on line {seen_urls[url]}")
        seen_urls[url] = i

        if previous_in_category and key < previous_in_category[0]:
            error(
                i,
                f"'{name}' is out of alphabetical order in '{category}' "
                f"(comes before '{previous_in_category[0]}' on line {previous_in_category[1]})",
            )
        previous_in_category = (key, i)

    if errors:
        print(f"{len(errors)} problem(s) found:\n")
        for e in errors:
            print(f"  {e}")
        print("\nSee CONTRIBUTING.md for the entry format.")
        return 1

    print(f"OK — {len(seen_names)} entries, all well-formed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
