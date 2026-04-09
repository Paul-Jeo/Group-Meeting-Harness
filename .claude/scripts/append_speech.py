#!/usr/bin/env python3
"""
Append a speech to discussion_log.md or anti_pattern_log.md (落盘步骤 A).

Usage:
  echo "<speech text>" | python .claude/scripts/append_speech.py \
      --slug 2026-04-09 \
      --round R1 \
      --role-zh 大老板 \
      --agent big-boss-agent \
      --target discussion \
      [--sub 2] [--interjection] [--source manual]

Effect:
  - Reads speech text from stdin
  - Builds anchor like: "## R1·大老板（big-boss-agent）"
    or "## R5.2·插话·博士师兄（phd-brother-agent）"
  - Finds sentinel in target file, replaces with anchor + speech + separator + sentinel

Output (stdout):
  OK
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Append speech to discussion/anti_pattern log")
    parser.add_argument("--slug", required=True)
    parser.add_argument("--round", required=True, help="R1 / R2 / R3 / R4 / R5 / R6")
    parser.add_argument("--role-zh", required=True, help="大老板 / 小老板1 / 小老板2 / 博士师姐 / 博士师兄 / 汇报者 / 硕一师妹 / 研一师弟")
    parser.add_argument("--agent", required=True, help="big-boss-agent / mixed-advisor-agent / ...")
    parser.add_argument("--target", choices=["discussion", "anti_pattern"], default="discussion")
    parser.add_argument("--sub", type=int, help="R5 sub-index (1, 2, 3, ...)")
    parser.add_argument("--interjection", action="store_true", help="Mark as R5 插话")
    parser.add_argument("--source", choices=["manual"], help="Set source=manual for manual R4/R5 input")
    args = parser.parse_args()

    # Force UTF-8
    try:
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

    speech_text = sys.stdin.read().rstrip()
    if not speech_text:
        print("ERROR: empty speech text on stdin", file=sys.stderr)
        sys.exit(1)

    # Build anchor
    round_str = args.round
    if args.sub is not None:
        round_str = f"{round_str}.{args.sub}"
    if args.interjection:
        round_str = f"{round_str}·插话"

    source_suffix = f" / {args.source}" if args.source else ""
    anchor = f"## {round_str}·{args.role_zh}（{args.agent}{source_suffix}）"

    # Target file + sentinel
    if args.target == "discussion":
        file_path = Path(f"docs/组会过程/{args.slug}/discussion_log.md")
        sentinel = "<!-- APPEND_DISCUSSION -->"
    else:
        file_path = Path(f"docs/组会过程/{args.slug}/anti_pattern_log.md")
        sentinel = "<!-- APPEND_ANTI_PATTERN -->"

    if not file_path.exists():
        print(f"ERROR: target file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    content = file_path.read_text(encoding="utf-8")
    if sentinel not in content:
        print(f"ERROR: sentinel '{sentinel}' not found in {file_path}", file=sys.stderr)
        sys.exit(1)

    # Build replacement block
    new_block = f"{anchor}\n\n{speech_text}\n\n---\n\n{sentinel}"
    new_content = content.replace(sentinel, new_block, 1)

    file_path.write_text(new_content, encoding="utf-8")
    print("OK")


if __name__ == "__main__":
    main()
