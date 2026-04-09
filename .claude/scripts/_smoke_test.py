#!/usr/bin/env python3
"""
Smoke test for all 5 orchestrator scripts.

Run from project root:
  python .claude/scripts/_smoke_test.py

Creates a temporary test meeting, exercises each script, verifies outputs,
then cleans up.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPTS = Path(".claude/scripts")
TEST_DATE = "9999-99-99"  # Obviously fake date, easy to clean up


def run(cmd, stdin_text=None, check=True):
    """Run a subprocess, capture output."""
    result = subprocess.run(
        cmd,
        input=stdin_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if check and result.returncode != 0:
        print(f"  ✗ Command failed: {' '.join(cmd)}")
        print(f"    stdout: {result.stdout}")
        print(f"    stderr: {result.stderr}")
        sys.exit(1)
    return result


def cleanup():
    """Remove test artifacts."""
    for p in [
        Path(f"docs/组会过程/{TEST_DATE}"),
        Path(f"docs/原始汇报/{TEST_DATE}.md"),
    ]:
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()


def test_init_meeting():
    print("TEST: init_meeting.py")
    # Write a test report to a temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write("这是测试研究汇报。本周进行了 Legal Predicate Graph 的实验。")
        report_path = f.name

    try:
        result = run([
            sys.executable, str(SCRIPTS / "init_meeting.py"),
            "--date", TEST_DATE,
            "--mode", "auto",
            "--report-file", report_path,
        ])
        slug = result.stdout.strip()
        assert slug == TEST_DATE, f"expected slug={TEST_DATE}, got {slug}"

        # Verify files exist
        meeting_dir = Path(f"docs/组会过程/{slug}")
        assert meeting_dir.exists()
        assert (meeting_dir / "discussion_log.md").exists()
        assert (meeting_dir / "anti_pattern_log.md").exists()
        assert (meeting_dir / "social_records.jsonl").exists()
        assert (meeting_dir / "meeting_meta.json").exists()
        assert Path(f"docs/原始汇报/{slug}.md").exists()

        # Verify meta structure
        meta = json.loads((meeting_dir / "meeting_meta.json").read_text(encoding="utf-8"))
        assert meta["slug"] == TEST_DATE
        assert meta["mode"] == "auto"
        assert meta["r5_round_count"] == 0
        assert meta["interjection_count"] == 0
        assert meta["termination_reason"] is None
        assert "files" in meta

        # Verify sentinels
        assert "<!-- APPEND_DISCUSSION -->" in (meeting_dir / "discussion_log.md").read_text(encoding="utf-8")
        assert "<!-- APPEND_ANTI_PATTERN -->" in (meeting_dir / "anti_pattern_log.md").read_text(encoding="utf-8")
        assert '"_sentinel":true' in (meeting_dir / "social_records.jsonl").read_text(encoding="utf-8")

        print("  ✓ init_meeting.py")
        return slug
    finally:
        os.unlink(report_path)


def test_append_speech(slug):
    print("TEST: append_speech.py")

    # R1 big-boss → discussion
    run([
        sys.executable, str(SCRIPTS / "append_speech.py"),
        "--slug", slug,
        "--round", "R1",
        "--role-zh", "大老板",
        "--agent", "big-boss-agent",
        "--target", "discussion",
    ], stdin_text="这个方向很好，但格局可以再大一点。如果能和跨学科结合，那就是一篇 Nature。")

    discussion = Path(f"docs/组会过程/{slug}/discussion_log.md").read_text(encoding="utf-8")
    assert "## R1·大老板（big-boss-agent）" in discussion
    assert "格局可以再大一点" in discussion
    assert discussion.count("<!-- APPEND_DISCUSSION -->") == 1  # still only 1 sentinel

    # R2 mixed-advisor → anti_pattern
    run([
        sys.executable, str(SCRIPTS / "append_speech.py"),
        "--slug", slug,
        "--round", "R2",
        "--role-zh", "小老板2",
        "--agent", "mixed-advisor-agent",
        "--target", "anti_pattern",
    ], stdin_text="老师说得太对了！我觉得可以直接融合所有模型，效果肯定最好！")

    anti = Path(f"docs/组会过程/{slug}/anti_pattern_log.md").read_text(encoding="utf-8")
    assert "## R2·小老板2（mixed-advisor-agent）" in anti
    assert "融合所有模型" in anti

    # R5.2 with sub-index and interjection
    run([
        sys.executable, str(SCRIPTS / "append_speech.py"),
        "--slug", slug,
        "--round", "R5",
        "--sub", "2",
        "--interjection",
        "--role-zh", "博士师兄",
        "--agent", "phd-brother-agent",
        "--target", "discussion",
    ], stdin_text="等一下，补充一句，baseline 跑对了吗？")

    discussion = Path(f"docs/组会过程/{slug}/discussion_log.md").read_text(encoding="utf-8")
    assert "## R5.2·插话·博士师兄（phd-brother-agent）" in discussion

    # R4 manual
    run([
        sys.executable, str(SCRIPTS / "append_speech.py"),
        "--slug", slug,
        "--round", "R4",
        "--role-zh", "汇报者",
        "--agent", "reporter-agent",
        "--source", "manual",
        "--target", "discussion",
    ], stdin_text="谢谢大家的建议，我回去再想想。")

    discussion = Path(f"docs/组会过程/{slug}/discussion_log.md").read_text(encoding="utf-8")
    assert "## R4·汇报者（reporter-agent / manual）" in discussion

    print("  ✓ append_speech.py")


def test_append_social_record(slug):
    print("TEST: append_social_record.py")

    record = {
        "speech_id": "R1-big-boss",
        "round": "R1",
        "round_index": None,
        "is_interjection": False,
        "is_anti_pattern": False,
        "role": "大老板",
        "agent": "big-boss-agent",
        "source": "ai_generated",
        "target": "all",
        "power_dynamics": "定调者，居高临下，从战略层面对全局发言",
        "face_management": "给汇报者留余地，用暗示不用直接否定",
        "rhetoric_techniques": "弦外之音 — 格局再大一点",
        "game_type": "BRIDGE",
        "key_quote": "这个方向很好，但格局可以再大一点",
        "lesson": "学会读懂'格局再大一点'的真实含义",
    }

    run([
        sys.executable, str(SCRIPTS / "append_social_record.py"),
        "--slug", slug,
    ], stdin_text=json.dumps(record, ensure_ascii=False))

    jsonl = Path(f"docs/组会过程/{slug}/social_records.jsonl").read_text(encoding="utf-8")
    lines = [l for l in jsonl.splitlines() if l.strip()]
    assert len(lines) == 2  # 1 record + 1 sentinel
    first = json.loads(lines[0])
    assert first["speech_id"] == "R1-big-boss"
    assert first["game_type"] == "BRIDGE"
    assert '"_sentinel":true' in lines[1]  # sentinel is last

    # Invalid JSON should error
    result = run([
        sys.executable, str(SCRIPTS / "append_social_record.py"),
        "--slug", slug,
    ], stdin_text="not json", check=False)
    assert result.returncode != 0, "should reject invalid JSON"
    assert "invalid JSON" in result.stderr

    print("  ✓ append_social_record.py")


def test_update_meta(slug):
    print("TEST: update_meta.py")

    # Increment r5_round_count
    run([
        sys.executable, str(SCRIPTS / "update_meta.py"),
        "--slug", slug,
        "--increment", "r5_round_count",
    ])
    meta = json.loads(Path(f"docs/组会过程/{slug}/meeting_meta.json").read_text(encoding="utf-8"))
    assert meta["r5_round_count"] == 1

    # Increment again
    run([
        sys.executable, str(SCRIPTS / "update_meta.py"),
        "--slug", slug,
        "--increment", "r5_round_count",
    ])
    meta = json.loads(Path(f"docs/组会过程/{slug}/meeting_meta.json").read_text(encoding="utf-8"))
    assert meta["r5_round_count"] == 2

    # Set termination_reason
    run([
        sys.executable, str(SCRIPTS / "update_meta.py"),
        "--slug", slug,
        "--set", "termination_reason=无新问题",
    ])
    meta = json.loads(Path(f"docs/组会过程/{slug}/meeting_meta.json").read_text(encoding="utf-8"))
    assert meta["termination_reason"] == "无新问题"

    # Set to null
    run([
        sys.executable, str(SCRIPTS / "update_meta.py"),
        "--slug", slug,
        "--set", "termination_reason=null",
    ])
    meta = json.loads(Path(f"docs/组会过程/{slug}/meeting_meta.json").read_text(encoding="utf-8"))
    assert meta["termination_reason"] is None

    # Invalid field increment should error
    result = run([
        sys.executable, str(SCRIPTS / "update_meta.py"),
        "--slug", slug,
        "--increment", "nonexistent_field",
    ], check=False)
    assert result.returncode != 0

    print("  ✓ update_meta.py")


def test_build_prompt(slug):
    print("TEST: build_prompt.py")

    # R1 big-boss: no prior_main, no anti_pattern
    result = run([
        sys.executable, str(SCRIPTS / "build_prompt.py"),
        "--slug", slug,
        "--round", "R1",
        "--agent", "big-boss-agent",
    ])
    xml = result.stdout
    assert "<round>R1</round>" in xml
    assert "<your_role>大老板（big-boss-agent）</your_role>" in xml
    assert "<round_index></round_index>" in xml
    assert "<is_interjection>false</is_interjection>" in xml
    assert "Legal Predicate Graph" in xml  # from test report
    assert 'Skill("big-boss")' in xml

    # R5.2 with sub and interjection
    result = run([
        sys.executable, str(SCRIPTS / "build_prompt.py"),
        "--slug", slug,
        "--round", "R5",
        "--sub", "2",
        "--interjection",
        "--agent", "curious-junior-agent",
    ])
    xml = result.stdout
    assert "<round>R5</round>" in xml
    assert "<round_index>2</round_index>" in xml
    assert "<is_interjection>true</is_interjection>" in xml
    assert "<your_role>硕一师妹（curious-junior-agent）</your_role>" in xml
    assert 'Skill("curious-junior")' in xml
    # R5 should include prior_main and anti_pattern
    assert "格局可以再大一点" in xml  # from R1 big-boss speech written earlier
    assert "融合所有模型" in xml  # from R2 mixed-advisor anti_pattern

    # Unknown agent should error
    result = run([
        sys.executable, str(SCRIPTS / "build_prompt.py"),
        "--slug", slug,
        "--round", "R1",
        "--agent", "nonexistent-agent",
    ], check=False)
    assert result.returncode != 0

    print("  ✓ build_prompt.py")


def main():
    # Force UTF-8
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

    # Must run from project root
    if not SCRIPTS.exists():
        print(f"ERROR: run from project root (no {SCRIPTS} found)", file=sys.stderr)
        sys.exit(1)

    # Clean up any leftovers from previous runs
    cleanup()

    try:
        slug = test_init_meeting()
        test_append_speech(slug)
        test_append_social_record(slug)
        test_update_meta(slug)
        test_build_prompt(slug)
        print()
        print("ALL TESTS PASSED ✓")
    finally:
        cleanup()


if __name__ == "__main__":
    main()
