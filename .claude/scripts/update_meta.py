#!/usr/bin/env python3
"""
Update a single field in meeting_meta.json (落盘步骤 C + 其他 meta 更新).

Usage:
  python .claude/scripts/update_meta.py --slug 2026-04-09 --increment r5_round_count
  python .claude/scripts/update_meta.py --slug 2026-04-09 --increment interjection_count
  python .claude/scripts/update_meta.py --slug 2026-04-09 --set termination_reason=无新问题
  python .claude/scripts/update_meta.py --slug 2026-04-09 --set mode=manual

Value parsing for --set:
  - "null" → Python None (JSON null)
  - Pure digits → integer
  - Everything else → string

Output (stdout):
  OK
"""

import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Update meeting_meta.json field")
    parser.add_argument("--slug", required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--increment", metavar="FIELD", help="Increment integer field by 1")
    group.add_argument("--set", dest="set_expr", metavar="KEY=VALUE", help="Set field to value")
    args = parser.parse_args()

    # Force UTF-8
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

    file_path = Path(f"docs/组会过程/{args.slug}/meeting_meta.json")
    if not file_path.exists():
        print(f"ERROR: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    try:
        meta = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: meta file not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if args.increment:
        field = args.increment
        if field not in meta:
            print(f"ERROR: field '{field}' not in meta", file=sys.stderr)
            sys.exit(1)
        if not isinstance(meta[field], int):
            print(f"ERROR: field '{field}' is not int (got {type(meta[field]).__name__})", file=sys.stderr)
            sys.exit(1)
        meta[field] = meta[field] + 1

    elif args.set_expr:
        if "=" not in args.set_expr:
            print("ERROR: --set requires 'key=value' format", file=sys.stderr)
            sys.exit(1)
        key, _, raw_value = args.set_expr.partition("=")
        # Value parsing
        if raw_value == "null":
            value = None
        elif raw_value.lstrip("-").isdigit():
            value = int(raw_value)
        else:
            value = raw_value
        meta[key] = value

    file_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("OK")


if __name__ == "__main__":
    main()
