**English** | [中文](README.zh-CN.md)

# Group Meeting Harness

> An academic group meeting simulator powered by eight AI roles.

Group Meeting Harness helps graduate students rehearse high-pressure research
meetings before they happen. It turns a rough weekly update into a structured
multi-role discussion, then produces a polished report draft, a private meeting
retrospective, action items, and a presentation-ready PPTX.

The project is built around Claude Code Skills, isolated subagents, and a
test-driven meeting flow. Each role sees only the context it should see, so the
discussion can surface conflicts, weak assumptions, hidden social dynamics, and
practical next steps instead of becoming a single flat chat.

## Quick Start

```bash
git clone https://github.com/Paul-Jeo/Group-Meeting-Harness.git
cd Group-Meeting-Harness

# Required for the PPTX generation stage on first use.
npm install -g pptxgenjs

claude
```

Then run the skill command with your weekly research update:

```text
/group-meeting This week I ran ablation experiments for contrastive learning. Accuracy reached 75%, but I am not sure how to analyze the results...
```

Choose a discussion mode:

| Mode | What happens |
| --- | --- |
| AI autoplay | All eight roles are played by AI. You observe the full meeting simulation. |
| Interactive rehearsal | The "reporter" turns in R4/R5 are written by you, so you can practice live responses. |

## What It Does

Group Meeting Harness is not a random brainstorming bot. It follows a structured
meeting protocol:

```text
Stage 0  Initialize meeting files and metadata
              |
Stage 1  R1  Lead advisor sets the direction          Red
         R2  Risky advisor introduces bad advice       Red
         R3  Senior researchers correct the issues     Green
         R4  Reporter responds and makes tradeoffs
         R5  Open discussion loop with interruptions
         R6  Expert advisor turns the debate into plan Refactor
              |
Stage 2  Synthesize social review, public report draft, and private memo
              |
Stage 3  Archive the meeting and update research-profile.md
              |
Stage 4  Generate the next-meeting PPTX
```

The deliberately wrong R2 round is part of the design. Real group meetings often
include misleading, premature, or socially motivated advice. The harness exposes
that failure mode early, isolates it in `anti_pattern_log.md`, and lets later
roles correct it before it contaminates the final report.

## Meeting Roles

```text
                    +-----------------+
                    | Submitted report |
                    +--------+--------+
                             |
          +------------------+------------------+
          |                  |                  |
    +-----+------+     +-----+------+     +-----+------+
    | Advisor    |     | Senior     |     | Presenter  |
    | layer      |     | layer      |     | layer      |
    +------------+     +------------+     +------------+
```

| Role | Codename | Purpose |
| --- | --- | --- |
| Lead advisor | Vision setter | Pushes for ambition, framing, and long-term value. |
| Risky advisor | Misdirector | Provides intentionally flawed advice so the system can detect and quarantine it. |
| Expert advisor | Stabilizer | Synthesizes debate into an executable plan. |
| Senior researcher 1 | Gentle reviewer | Finds reviewer-style concerns and soft risks. |
| Senior researcher 2 | Hard reviewer | Challenges baselines, experiments, claims, and missing controls. |
| Reporter | You | Defends the work, resolves contradictions, and decides the path forward. |
| Junior researcher 1 | Basic-question asker | Raises simple questions that reveal unclear explanations. |
| Junior researcher 2 | Bold challenger | Suggests direct alternatives and forces hidden assumptions into the open. |

Each role is implemented as an isolated subagent with its own prompt, tool
permissions, and context boundary.

## Outputs

After each simulated meeting, the harness writes concrete artifacts. `{slug}` is
the meeting date, with `-2`, `-3`, and so on added automatically for duplicate
same-day runs.

| File | Purpose |
| --- | --- |
| `docs/原始汇报/{slug}.md` | Archive of the original report you submitted. |
| `docs/组会过程/{slug}/discussion_log.md` | Full R1-R6 discussion transcript. |
| `docs/组会过程/{slug}/anti_pattern_log.md` | Isolated bad-advice log that must not enter the public report. |
| `docs/组会过程/{slug}/social_records.jsonl` | Structured social-dynamics records for each utterance. |
| `docs/组会过程/{slug}/meeting_meta.json` | Meeting metadata and historical context. |
| `docs/社交复盘/{slug}.md` | Power dynamics, face management, rhetoric patterns, and social review. |
| `docs/汇报草稿/{slug}.md` | Public-facing report draft suitable for weekly reporting. |
| `docs/私密备忘/{slug}.md` | Private memo for honest reflection and next-step tracking. |
| `ppt/{slug}.pptx` | Business-style PPTX for the next meeting. |
| `research-profile.md` | Research profile snapshot used to keep continuity across meetings. |

The public draft and private memo are intentionally separated. The public draft
is optimized for presentation. The private memo keeps the candid analysis,
mistakes, interpersonal risks, and action-item history that should not appear in
the PPT.

## Customizing Roles

Each role can be customized. Add a Markdown file under:

```text
.claude/skills/<role>/character/
```

Example:

```markdown
<!-- .claude/skills/phd-brother/character/my-senior.md -->

Catchphrases:
- "This loss curve does not look right."
- "Check the repo from the XX group; they did this last year."

Style:
Short, direct, never more than three sentences.

Attitude toward you:
Not hostile, but will only help when the question is specific enough.
```

Custom character files override the default role profile, making the rehearsal
closer to the people and meeting culture you actually work with.

## Project Structure

```text
Group-Meeting-Harness/
|-- .claude/
|   |-- skills/
|   |   |-- group-meeting/          # Main /group-meeting orchestrator
|   |   |-- big-boss/               # Lead advisor role
|   |   |-- mixed-advisor/          # Risky advisor role
|   |   |-- expert-advisor/         # Expert advisor role
|   |   |-- phd-sister/             # Senior researcher role
|   |   |-- phd-brother/            # Senior researcher role
|   |   |-- reporter/               # Reporter role
|   |   |-- curious-junior/         # Basic-question role
|   |   |-- bold-freshman/          # Bold-challenger role
|   |   |-- social-recorder/        # Structured social data recorder
|   |   |-- social-dynamics/        # Social review synthesis
|   |   |-- report-synthesis/       # Public/private report synthesis
|   |   |-- interjection-trigger/   # R5 interruption rules
|   |   |-- discussion-terminator/  # R5 termination rules
|   |   `-- pptx/                   # PPTX generation stage
|   |-- agents/                     # Isolated subagent definitions
|   |-- scripts/                    # File I/O and prompt-building scripts
|   |-- hooks/                      # Subagent output validation hooks
|   `-- settings.json               # Claude Code settings
|-- docs/
|   `-- social-patterns/            # Research material for rhetoric and social dynamics
|-- README.md
`-- .gitignore
```

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- Node.js and globally installed `pptxgenjs` for the PPTX generation stage
- Optional: Zotero MCP integration for literature-aware senior-reviewer roles

## Why This Exists

Group meetings are one of the most important training environments in graduate
research, but they are also noisy. Useful academic feedback, status pressure,
advisor preferences, hidden assumptions, and interpersonal signals often arrive
mixed together.

This harness separates those layers. It helps you:

1. Rehearse the academic argument before the real meeting.
2. Detect weak experiments, unclear claims, and risky framing.
3. Translate ambiguous feedback into concrete next actions.
4. Preserve continuity across meetings through `research-profile.md`.
5. Produce both a polished external report and an honest internal memo.

The goal is simple: walk into the real meeting with a clearer argument, a better
plan, and fewer surprises.
