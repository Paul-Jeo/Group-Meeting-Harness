#!/usr/bin/env python3
"""
Append a social analysis JSON record to social_records.jsonl (落盘步骤 B).

Usage:
  echo '{"speech_id":"R1-big-boss","round":"R1",...}' | \
      python .claude/scripts/append_social_record.py --slug 2026-04-09

Effect:
  - Reads JSON object from stdin
  - Validates it parses as a JSON object (not array, not scalar)
  - Re-serializes to canonical single-line form (ensure_ascii=False)
  - Inserts the line immediately before the `_sentinel:true` line

Output (stdout):
  OK
"""

import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Append JSON record to social_records.jsonl")
    parser.add_argument("--slug", required=True)
    args = parser.parse_args()

    # Force UTF-8
    try:
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

    raw = sys.stdin.read().strip()
    if not raw:
        print("ERROR: empty JSON on stdin", file=sys.stderr)
        sys.exit(1)

    # Validate JSON
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(parsed, dict):
        print("ERROR: JSON must be an object (got %s)" % type(parsed).__name__, file=sys.stderr)
        sys.exit(1)

    if parsed.get("_sentinel"):
        print("ERROR: refusing to append a sentinel record", file=sys.stderr)
        sys.exit(1)

    # Canonical single-line form (compact, UTF-8 preserved)
    canonical = json.dumps(parsed, ensure_ascii=False, separators=(",", ":"))

    file_path = Path(f"docs/组会过程/{args.slug}/social_records.jsonl")
    if not file_path.exists():
        print(f"ERROR: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Find first sentinel line
    sentinel_idx = None
    for i, line in enumerate(lines):
        if '"_sentinel":true' in line or '"_sentinel": true' in line:
            sentinel_idx = i
            break

    if sentinel_idx is None:
        print(f"ERROR: sentinel line not found in {file_path}", file=sys.stderr)
        sys.exit(1)

    # Insert new line before sentinel
    lines.insert(sentinel_idx, canonical)

    # Write back (preserve final newline)
    file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("OK")


if __name__ == "__main__":
    main()
