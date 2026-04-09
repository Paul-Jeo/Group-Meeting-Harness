#!/usr/bin/env python3
"""
Initialize a new meeting session: creates directories, archives the original
report, and writes the 4 process files (discussion_log.md, anti_pattern_log.md,
social_records.jsonl, meeting_meta.json).

Usage:
  python .claude/scripts/init_meeting.py \
      --date 2026-04-09 \
      --mode auto \
      --report-file /tmp/report_input.md

Effect:
  - Resolves slug (uses --date as-is; if docs/组会过程/{date} already exists,
    falls back to -2, -3, ...)
  - Creates docs/原始汇报/, docs/组会过程/{slug}/, ppt/ (all with exist_ok)
  - Copies --report-file contents to docs/原始汇报/{slug}.md
  - Creates 4 process files inside docs/组会过程/{slug}/ with headers + sentinels
  - Loads last 3 timestamp blocks from research-profile.md as history_context
  - Writes meeting_meta.json with all fields populated

Output (stdout):
  Single line with the resolved slug (e.g., "2026-04-09" or "2026-04-09-2")
"""

import argparse
import json
import re
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Initialize a meeting session")
    parser.add_argument("--date", required=True, help="Meeting date YYYY-MM-DD")
    parser.add_argument("--mode", choices=["auto", "manual"], default="auto")
    parser.add_argument("--report-file", required=True, help="Path to original report markdown file")
    args = parser.parse_args()

    # Force UTF-8 for Windows
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

    # 1. Read report content
    report_path_in = Path(args.report_file)
    if not report_path_in.exists():
        print(f"ERROR: --report-file not found: {report_path_in}", file=sys.stderr)
        sys.exit(1)
    report_text = report_path_in.read_text(encoding="utf-8")

    # 2. Resolve slug
    slug = resolve_slug(args.date)

    # 3. Create directories
    meeting_dir = Path(f"docs/组会过程/{slug}")
    meeting_dir.mkdir(parents=True, exist_ok=True)
    Path("docs/原始汇报").mkdir(parents=True, exist_ok=True)
    Path("ppt").mkdir(parents=True, exist_ok=True)

    # 4. Archive report
    (Path(f"docs/原始汇报/{slug}.md")).write_text(report_text, encoding="utf-8")

    # 5. Load history context from research-profile.md
    history_context, history_count = load_history_context()

    # 6. Create discussion_log.md
    (meeting_dir / "discussion_log.md").write_text(
        f"# 组会讨论日志 — {slug}\n\n"
        f"> 主线 R1/R3/R4/R5/R6 发言（按 R 编号顺序追加）。R2 反例在 anti_pattern_log.md。\n\n"
        f"<!-- APPEND_DISCUSSION -->\n",
        encoding="utf-8",
    )

    # 7. Create anti_pattern_log.md
    (meeting_dir / "anti_pattern_log.md").write_text(
        f"# 反例隔离日志 — {slug}\n\n"
        f"> ⚠️ 仅装 R2 mixed-advisor 反例 / 作 R3-R6 反驳输入 / "
        f"禁入 Part A 汇报草稿 / report-synthesis 生成 Part A 时禁 Read 本文件\n\n"
        f"<!-- APPEND_ANTI_PATTERN -->\n",
        encoding="utf-8",
    )

    # 8. Create social_records.jsonl
    (meeting_dir / "social_records.jsonl").write_text(
        '{"_sentinel":true,"_note":"DO NOT REMOVE - append marker; readers skip lines with _sentinel:true"}\n',
        encoding="utf-8",
    )

    # 9. Create meeting_meta.json
    meta = {
        "slug": slug,
        "date": args.date,
        "mode": args.mode,
        "history_loaded_count": history_count,
        "history_context": history_context,
        "r5_round_count": 0,
        "interjection_count": 0,
        "termination_reason": None,
        "files": {
            "原始汇报": f"docs/原始汇报/{slug}.md",
            "discussion_log": f"docs/组会过程/{slug}/discussion_log.md",
            "anti_pattern_log": f"docs/组会过程/{slug}/anti_pattern_log.md",
            "social_records": f"docs/组会过程/{slug}/social_records.jsonl",
            "社交复盘": f"docs/社交复盘/{slug}.md",
            "汇报草稿": f"docs/汇报草稿/{slug}.md",
            "私密备忘": f"docs/私密备忘/{slug}.md",
            "ppt": f"ppt/{slug}.pptx",
        },
    }
    (meeting_dir / "meeting_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # 10. Output slug to stdout
    print(slug)


def resolve_slug(date: str) -> str:
    """Return first available slug: date, date-2, date-3, ..."""
    if not Path(f"docs/组会过程/{date}").exists():
        return date
    n = 2
    while Path(f"docs/组会过程/{date}-{n}").exists():
        n += 1
    return f"{date}-{n}"


def load_history_context():
    """Extract last 3 '## YYYY-MM-DD' timestamp blocks from research-profile.md."""
    profile = Path("research-profile.md")
    if not profile.exists():
        return "", 0

    text = profile.read_text(encoding="utf-8")
    # Find all timestamp heading positions
    heading_pattern = re.compile(r"(?m)^## \d{4}-\d{2}-\d{2}")
    matches = list(heading_pattern.finditer(text))

    if not matches:
        return "", 0

    # Take last 3 blocks (from i-th heading to next heading or EOF)
    last_3 = matches[-3:]
    blocks = []
    for i, m in enumerate(last_3):
        start = m.start()
        # End is the start of next heading (in full matches list) or EOF
        idx_in_all = matches.index(m)
        if idx_in_all + 1 < len(matches):
            end = matches[idx_in_all + 1].start()
        else:
            end = len(text)
        blocks.append(text[start:end].strip())

    return "\n\n".join(blocks), len(blocks)


if __name__ == "__main__":
    main()
