#!/usr/bin/env python3
"""
Hook: validate role sub-agent output AND execution trace.

Triggers on:
  - SubagentStop (preferred): full sub-agent introspection via agent_transcript_path.
    Validates both the final text output AND the sub-agent's tool_use history
    (was Skill('<role>') called? were the required character/* and docs/* files Read?).
  - PostToolUse on Task/Agent (legacy fallback): output-only validation.
    Used when SubagentStop fires without agent_transcript_path or when the user is
    on an older Claude Code build that only supports PostToolUse.

Two validation layers:
  Layer 1 — text purity:
    1. No markdown headers (^#)
    2. No code blocks (```)
    3. No meta annotations ([分析:, [思考:, [策略:, etc.)
    4. No self-description phrases ("作为大老板", "以下是我的发言", ...)
    5. Non-empty
  Layer 2 — execution trace (only when agent_transcript_path is available):
    a. Sub-agent called Skill('<role>') to load its SKILL.md
    b. Sub-agent Glob'd .claude/skills/<role>/character/*.md
    c. Sub-agent Read at least one character/*.md file
    d. Sub-agent Read every required docs/social-patterns/*.md file (per role)

If any layer reports violations, the hook returns a block decision so the parent
orchestrator can re-spawn the sub-agent with feedback.

Input protocol (stdin JSON, varies by event):
  SubagentStop: { hook_event_name: "SubagentStop", agent_type: "...",
                  last_assistant_message: "...", agent_transcript_path: "..." }
  PostToolUse:  { hook_event_name: "PostToolUse", tool_name: "Task"|"Agent",
                  tool_input: { subagent_type: "..." }, tool_response: ... }

Output protocol (stdout JSON when blocking):
  { "decision": "block", "reason": "<feedback for parent>" }
"""
import json
import os
import re
import sys

# Force UTF-8 for stdin/stdout on Windows (default GBK can't encode emoji/CJK).
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass


# ---------- Role registry ----------

ROLE_AGENTS = {
    "big-boss-agent",
    "mixed-advisor-agent",
    "expert-advisor-agent",
    "phd-brother-agent",
    "phd-sister-agent",
    "reporter-agent",
    "curious-junior-agent",
    "bold-freshman-agent",
}

# Per-role required files (substring match against Read tool's file_path).
# `skill_name` is the argument expected in Skill(name=...).
# `character_dir` is the substring that should appear in the Glob pattern AND
# at least one Read file_path.
# `docs` is the list of substrings (each must match at least one Read file_path).
REQUIRED_READS = {
    "big-boss-agent": {
        "skill_name": "big-boss",
        "character_dir": "skills/big-boss/character",
        "docs": [
            "social-patterns/advisor-subtext/big-boss-subtext",
            "social-patterns/power-dynamics/advisor-archetypes",
        ],
    },
    "mixed-advisor-agent": {
        "skill_name": "mixed-advisor",
        "character_dir": "skills/mixed-advisor/character",
        "docs": [
            "social-patterns/advisor-subtext/mixed-advisor-traps",
            "social-patterns/rhetoric-patterns/face-management",
        ],
    },
    "expert-advisor-agent": {
        "skill_name": "expert-advisor",
        "character_dir": "skills/expert-advisor/character",
        "docs": [
            "social-patterns/power-dynamics/advisor-archetypes",
            "social-patterns/rhetoric-patterns/upward-management",
        ],
    },
    "phd-brother-agent": {
        "skill_name": "phd-brother",
        "character_dir": "skills/phd-brother/character",
        "docs": [
            "social-patterns/rhetoric-patterns/peer-interaction",
            "social-patterns/rhetoric-patterns/defense-tactics",
        ],
    },
    "phd-sister-agent": {
        "skill_name": "phd-sister",
        "character_dir": "skills/phd-sister/character",
        "docs": [
            "social-patterns/rhetoric-patterns/peer-interaction",
            "social-patterns/rhetoric-patterns/face-management",
        ],
    },
    "reporter-agent": {
        "skill_name": "reporter",
        "character_dir": "skills/reporter/character",
        "docs": [
            "social-patterns/rhetoric-patterns/upward-management",
            "social-patterns/rhetoric-patterns/high-pressure-moments",
        ],
    },
    "curious-junior-agent": {
        "skill_name": "curious-junior",
        "character_dir": "skills/curious-junior/character",
        "docs": [
            "social-patterns/rhetoric-patterns/junior-questioning",
        ],
    },
    "bold-freshman-agent": {
        "skill_name": "bold-freshman",
        "character_dir": "skills/bold-freshman/character",
        "docs": [
            "social-patterns/rhetoric-patterns/junior-questioning",
        ],
    },
}


# ---------- Text extraction (PostToolUse fallback path) ----------

def _flatten_content(value):
    """Recursively pull text out of nested content/message structures."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(_flatten_content(item) for item in value)
    if isinstance(value, dict):
        if "text" in value and isinstance(value["text"], str):
            return value["text"]
        for key in ("content", "output", "result", "message"):
            if key in value:
                return _flatten_content(value[key])
    return ""


# ---------- Layer 1: text purity ----------

MARKDOWN_HEADER_RE = re.compile(r"^#{1,6}\s", re.MULTILINE)
META_ANNOTATION_RE = re.compile(
    r"\[(分析|思考|策略|note|meta|reasoning|thought|role|角色)[:：]",
    re.IGNORECASE,
)
SELF_DESCRIPTION_PHRASES = (
    "作为大老板", "作为小老板", "作为师兄", "作为师姐", "作为师妹",
    "作为师弟", "作为汇报者",
    "以下是我的发言", "以下是大老板的发言", "我的发言如下",
    "下面是我的", "下面是大老板",
    "Here is my", "Here's my",
)


def validate_text(text):
    """Layer 1 checks: return list of text-purity violations."""
    violations = []

    if not text or not text.strip():
        return ["发言为空（last_assistant_message / tool_response 均无文本）"]

    if MARKDOWN_HEADER_RE.search(text):
        violations.append("包含 markdown 标题（以 # 开头的行）")

    if "```" in text:
        violations.append("包含代码块（```）")

    if META_ANNOTATION_RE.search(text):
        violations.append("包含元注释（如 [分析:/[思考:/[策略: 等）")

    for phrase in SELF_DESCRIPTION_PHRASES:
        if phrase in text:
            violations.append(f"包含自我描述/元叙事：'{phrase}'")
            break

    return violations


# ---------- Layer 2: execution trace ----------

def parse_tool_uses(transcript_path):
    """
    Parse a JSONL transcript and return list of {name, input} for each tool_use.
    Returns None if file is missing/unreadable so callers can skip the check.
    Defensive: handles several possible JSONL structures.
    """
    if not transcript_path:
        return None
    expanded = os.path.expanduser(transcript_path)
    if not os.path.exists(expanded):
        return None

    tool_uses = []
    try:
        with open(expanded, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(entry, dict):
                    continue

                # Collect every candidate "content" array we can find.
                content_lists = []
                msg = entry.get("message")
                if isinstance(msg, dict):
                    msg_content = msg.get("content")
                    if isinstance(msg_content, list):
                        content_lists.append(msg_content)
                top_content = entry.get("content")
                if isinstance(top_content, list):
                    content_lists.append(top_content)

                for content_list in content_lists:
                    for item in content_list:
                        if (
                            isinstance(item, dict)
                            and item.get("type") == "tool_use"
                        ):
                            tool_uses.append({
                                "name": item.get("name", ""),
                                "input": item.get("input", {}) or {},
                            })

                # Sometimes tool_use sits at the top level of an entry.
                if entry.get("type") == "tool_use":
                    tool_uses.append({
                        "name": entry.get("name", ""),
                        "input": entry.get("input", {}) or {},
                    })
    except OSError:
        return None

    return tool_uses


def _normalize_path(p):
    """Normalize a file path for substring matching across OSes."""
    return (p or "").replace("\\", "/")


def validate_trace(tool_uses, role):
    """
    Layer 2 checks: verify the sub-agent's tool_use history matches role requirements.
    Returns list of trace violations. Empty if requirements satisfied OR if check
    cannot be performed (tool_uses is None).
    """
    if tool_uses is None:
        return []  # Cannot inspect — silent skip, don't false-block.

    requirements = REQUIRED_READS.get(role)
    if not requirements:
        return []

    skill_name = requirements["skill_name"]
    character_dir = requirements["character_dir"]
    required_docs = requirements["docs"]

    skill_called = False
    glob_pattern_ok = False
    files_read = []

    for tu in tool_uses:
        name = tu["name"]
        inp = tu["input"]

        if name == "Skill":
            sk = (
                inp.get("name")
                or inp.get("skill_name")
                or inp.get("skill")
                or ""
            )
            if sk == skill_name:
                skill_called = True

        elif name == "Read":
            fp = inp.get("file_path") or inp.get("path") or ""
            if fp:
                files_read.append(_normalize_path(fp))

        elif name == "Glob":
            pattern = _normalize_path(inp.get("pattern", ""))
            if character_dir in pattern:
                glob_pattern_ok = True

    violations = []

    if not skill_called:
        violations.append(
            f"未调用 Skill('{skill_name}') — 角色定义未加载，"
            f"不可能符合 SKILL.md 的执行规范"
        )

    if not glob_pattern_ok:
        violations.append(
            f"未对 '{character_dir}/*.md' 执行 Glob — 缺少基础短语调色板的发现步骤"
        )

    character_files_read = [fp for fp in files_read if character_dir in fp]
    if not character_files_read:
        violations.append(
            f"未 Read 任何 {character_dir}/*.md 文件 — 没读 character 调色板"
        )

    for doc_substring in required_docs:
        if not any(doc_substring in fp for fp in files_read):
            violations.append(
                f"未 Read 必读素材文件: docs/{doc_substring}.md"
            )

    return violations


# ---------- Hook entry ----------

def emit_block(role, all_violations):
    """Emit a block decision JSON to stdout."""
    reason_lines = [
        f"❌ {role} 执行不合格，违反规则：",
        *[f"  - {v}" for v in all_violations],
        "",
        "请重新调用该角色 agent 并严格执行：",
        "  1. 调用 Skill('<角色 skill 名>') 加载角色定义",
        "  2. 完成 SKILL.md 的 ⚠️ 运行时素材清单：Glob+Read character/* 和 Read docs/social-patterns/*",
        "  3. 按 SKILL.md 的融合方式与发言结构生成内容",
        "  4. 只返回纯发言文本（无 markdown 标题/代码块/元注释/自我描述）",
    ]
    payload = {
        "decision": "block",
        "reason": "\n".join(reason_lines),
    }
    print(json.dumps(payload, ensure_ascii=False))


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    if not isinstance(data, dict):
        sys.exit(0)

    event = data.get("hook_event_name", "")
    role = ""
    text = ""
    transcript_path = ""

    if event == "SubagentStop":
        role = data.get("agent_type", "") or ""
        if role not in ROLE_AGENTS:
            sys.exit(0)
        text = data.get("last_assistant_message", "") or ""
        transcript_path = data.get("agent_transcript_path", "") or ""

    elif event == "PostToolUse":
        if data.get("tool_name") not in ("Task", "Agent"):
            sys.exit(0)
        tool_input = data.get("tool_input") or {}
        role = tool_input.get("subagent_type", "") or ""
        if role not in ROLE_AGENTS:
            sys.exit(0)
        text = _flatten_content(data.get("tool_response", {})).strip()
        # Some Claude Code versions also expose agent_transcript_path on PostToolUse.
        transcript_path = data.get("agent_transcript_path", "") or ""

    else:
        sys.exit(0)

    text_violations = validate_text(text)

    trace_violations = []
    if transcript_path:
        tool_uses = parse_tool_uses(transcript_path)
        trace_violations = validate_trace(tool_uses, role)

    all_violations = text_violations + trace_violations

    if all_violations:
        emit_block(role, all_violations)

    sys.exit(0)


if __name__ == "__main__":
    main()
