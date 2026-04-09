#!/usr/bin/env python3
"""
Build the XML-formatted prompt for a role sub-agent (Task tool prompt field).

Usage:
  python .claude/scripts/build_prompt.py \
      --slug 2026-04-09 \
      --round R1 \
      --agent big-boss-agent

  python .claude/scripts/build_prompt.py \
      --slug 2026-04-09 \
      --round R5 \
      --sub 2 \
      --agent curious-junior-agent

  python .claude/scripts/build_prompt.py \
      --slug 2026-04-09 \
      --round R5 \
      --sub 2 \
      --interjection \
      --agent phd-brother-agent

Effect:
  - Reads docs/原始汇报/{slug}.md for original_report
  - Reads meeting_meta.json.history_context
  - Reads discussion_log.md (if round is R2+) for prior_main_discussion
  - Reads anti_pattern_log.md (if round is R3+) for anti_pattern_for_correction
  - Fills the XML template with all fields

Output (stdout):
  Complete XML prompt ready to paste into Task tool's `prompt` parameter.
"""

import argparse
import json
import sys
from pathlib import Path


# Map agent-name → Chinese role name
ROLE_ZH = {
    "big-boss-agent": "大老板",
    "mixed-advisor-agent": "小老板2",
    "expert-advisor-agent": "小老板1",
    "phd-sister-agent": "博士师姐",
    "phd-brother-agent": "博士师兄",
    "reporter-agent": "汇报者",
    "curious-junior-agent": "硕一师妹",
    "bold-freshman-agent": "研一师弟",
}

# Which rounds need which data sources
NEEDS_PRIOR = {"R2", "R3", "R4", "R5", "R6"}
NEEDS_ANTI_PATTERN = {"R3", "R4", "R5", "R6"}


def main():
    parser = argparse.ArgumentParser(description="Build XML prompt for role sub-agent")
    parser.add_argument("--slug", required=True)
    parser.add_argument("--round", required=True, help="R1 / R2 / R3 / R4 / R5 / R6")
    parser.add_argument("--agent", required=True, help="big-boss-agent / ...")
    parser.add_argument("--sub", type=int, help="R5 sub-index (1, 2, 3, ...)")
    parser.add_argument("--interjection", action="store_true")
    args = parser.parse_args()

    # Force UTF-8
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

    if args.agent not in ROLE_ZH:
        print(f"ERROR: unknown agent '{args.agent}'. Known: {sorted(ROLE_ZH.keys())}", file=sys.stderr)
        sys.exit(1)
    role_zh = ROLE_ZH[args.agent]
    skill_name = args.agent.replace("-agent", "")

    # Load files
    meta_path = Path(f"docs/组会过程/{args.slug}/meeting_meta.json")
    if not meta_path.exists():
        print(f"ERROR: meta file not found: {meta_path}", file=sys.stderr)
        sys.exit(1)
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    report_path = Path(f"docs/原始汇报/{args.slug}.md")
    if not report_path.exists():
        print(f"ERROR: original report not found: {report_path}", file=sys.stderr)
        sys.exit(1)
    original_report = report_path.read_text(encoding="utf-8").strip()

    history_context = (meta.get("history_context") or "").strip()

    prior_main = ""
    if args.round in NEEDS_PRIOR:
        p = Path(f"docs/组会过程/{args.slug}/discussion_log.md")
        if p.exists():
            prior_main = p.read_text(encoding="utf-8").strip()

    anti_pattern = ""
    if args.round in NEEDS_ANTI_PATTERN:
        p = Path(f"docs/组会过程/{args.slug}/anti_pattern_log.md")
        if p.exists():
            anti_pattern = p.read_text(encoding="utf-8").strip()

    round_index = str(args.sub) if args.sub is not None else ""
    is_interjection = "true" if args.interjection else "false"

    xml = (
        f"<context>\n"
        f"<round>{args.round}</round>\n"
        f"<round_index>{round_index}</round_index>\n"
        f"<is_interjection>{is_interjection}</is_interjection>\n"
        f"<your_role>{role_zh}（{args.agent}）</your_role>\n"
        f"<original_report>\n{original_report}\n</original_report>\n"
        f"<history_context>\n{history_context}\n</history_context>\n"
        f"<prior_main_discussion>\n{prior_main}\n</prior_main_discussion>\n"
        f"<anti_pattern_for_correction>\n{anti_pattern}\n</anti_pattern_for_correction>\n"
        f"</context>\n\n"
        f"<task>\n"
        f'调用 `Skill("{skill_name}")` 加载角色定义，然后按加载的 SKILL.md 执行 {args.round} 发言。只返回纯发言文本。\n'
        f"</task>"
    )

    print(xml)


if __name__ == "__main__":
    main()
