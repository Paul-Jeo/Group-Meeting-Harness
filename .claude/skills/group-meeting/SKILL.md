---
name: group-meeting
description: 学术组会模拟器。接收研究汇报，按 R1-R6 六轮编排 8 角色讨论，最终输出社交复盘、汇报草稿、私密备忘、pptx 四份产物。Use when 用户说"开组会/这周汇报/本周进展/组会内容如下"或提交研究周报内容。
argument-hint: [研究汇报内容]
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Skill(pptx)
  - Skill(social-recorder)
  - Skill(social-dynamics)
  - Skill(report-synthesis)
  - Skill(interjection-trigger)
  - Skill(discussion-terminator)
---

# /group-meeting — 学术组会模拟器

接收研究汇报 → R1-R6 编排 8 角色 → 输出社交复盘 + 汇报草稿 + 私密备忘 + pptx。

## 硬规则

1. **四阶段完整性**：第零→第四必须全部执行。`ppt/{slug}.pptx` 真实存在是**唯一**完成标志；第三阶段结束**不等于**任务结束。
2. **Skill 调用 = 真实动作**：下文 6 处 `Skill("xxx")` 是工具调用，不是对规范的文字引用。
3. **机械操作走脚本，不手搓**：文件初始化 / prompt 构造 / 发言落盘 / JSON 追加 / meta 更新，分别对应 `.claude/scripts/` 下的 5 个 Python 脚本，必须直接 Bash 调用，禁止用 Read+Edit 手工复刻。
4. **每条发言立即落盘**（调脚本），不依赖 main context 暂存。
5. **反例物理隔离**：R2 只入 `anti_pattern_log.md`；report-synthesis 生成 Part A 时禁 Read 该文件。
6. **hook 校验**：sub-agent 停止时 hook 检查 Skill 调用 + Read trace + 纯文本输出；违反则 block 并反馈，必须重新 spawn。

## 输入

用户在 `/group-meeting` 后的文本即为本次研究汇报。若未附带：

> 请粘贴你的研究汇报内容（本周做了什么、实验结果、遇到的问题等），我来开组会。

收到后询问模式：

```
1️⃣  AI 全自动 — 8 个角色全部由 AI 扮演
2️⃣  亲自上场 — R4/R5 中"你自己"由你输入，其他仍由 AI 扮演
输入 1 或 2（默认 1）：
```

记为 `mode`（`auto` / `manual`）。

---

## 第零阶段：初始化

`{date}` = Claude Code system prompt 注入的当前日期（`YYYY-MM-DD`），**禁止自行生成时间**。

1. **暂存汇报** — Write 用户汇报原文到 `docs/原始汇报/_pending.md`
2. **一键初始化** — Bash：
   ```bash
   python .claude/scripts/init_meeting.py --date {date} --mode {mode} --report-file docs/原始汇报/_pending.md
   ```
   stdout 是本次 slug（例 `2026-04-08` 或 `2026-04-08-2`）。**记住这个 slug，后续所有步骤都用它**。
3. **清理** — Bash `rm docs/原始汇报/_pending.md`

此脚本一次性完成：加载 `research-profile.md` 最近 3 个历史块、归档汇报（含 `-2 / -3` 冲突）、创建 `docs/组会过程/{slug}/`、初始化 4 个过程文件（含 sentinel 和 meta schema）。

→ 进入第一阶段

---

## 第一阶段：R1-R6 讨论

### 单条发言的 4 步标准流程

对任何一条发言，固定执行：

**① 构造 prompt**
```bash
python .claude/scripts/build_prompt.py --slug {slug} --round R{N} --agent {agent-name} [--sub {n}] [--interjection]
```
stdout 是完整 XML prompt（已含 original_report / history_context / prior_main / anti_pattern / Skill 指令），直接作为 Task 参数。脚本每次从磁盘重新 Read，不依赖 main context 缓存。

**② Spawn sub-agent**
调用 Task 工具，`subagent_type` = `{agent-name}`，`prompt` = 上一步 stdout。捕获返回的纯发言文本。

**③ 落盘发言**
```bash
echo "{发言全文}" | python .claude/scripts/append_speech.py \
  --slug {slug} --round R{N} \
  --role-zh {角色中文名} --agent {agent-name} \
  --target {discussion|anti_pattern} \
  [--sub {n}] [--interjection] [--source manual]
```
R2 → `--target anti_pattern`；其他 → `--target discussion`。
角色中文名：大老板 / 小老板2 / 小老板1 / 博士师姐 / 博士师兄 / 汇报者 / 硕一师妹 / 研一师弟。

**④ 写社交记录**
1. `Skill("social-recorder")` 加载 schema
2. 基于刚才的发言生成 JSON 对象（R2 设 `is_anti_pattern: true`；R5 插话设 `is_interjection: true`；`speech_id` = `R{N}-{agent 短名}` 或 `R5.{n}-{agent 短名}` 或 `R5.{n}-interject-{agent 短名}`）
3. Bash：
   ```bash
   echo '{json...}' | python .claude/scripts/append_social_record.py --slug {slug}
   ```

### R 轮执行顺序

按以下顺序执行，每步都跑完上述"4 步标准流程"。**每步必须显式使用指定的 sub-agent**——编排器不得在未调用 sub-agent 的情况下自己代写发言。

#### R1 — 大老板定调
使用 **`big-boss-agent`** 生成 R1 发言。4 步流程，`target=discussion`。

#### R2 — 小老板2 示范错误（反例）
使用 **`mixed-advisor-agent`** 生成 R2 发言。4 步流程，`target=anti_pattern`（**唯一进 anti_pattern_log 的一轮**）。

#### R3 — 博士师姐 + 博士师兄并行纠偏
**同一条 assistant 消息里同时发出两个 Task 调用**（顺序发两次不算并行）：
- 使用 **`phd-sister-agent`** 生成 R3 师姐发言
- 使用 **`phd-brother-agent`** 生成 R3 师兄发言

两条都返回后，分别跑各自的 4 步落盘，`target=discussion`。

#### R4 / R5 — 汇报者主导的自由讨论循环

R4 是循环的 sub-index = 1 起点，R5 继续递增。每个 sub-index `{n}`（从 1 开始）依次执行：

1. 使用 **`reporter-agent`** 生成本轮汇报者发言。4 步流程，`--round R5 --sub {n}`，`target=discussion`。
   - **Manual 模式**：跳过 spawn，Read `discussion_log.md` 展示前文 → 等用户输入 → 执行 ③④（加 `--source manual`）；用户输入 `pass` 则整个 sub-index 跳到下一步
2. 使用 **`curious-junior-agent`** 生成硕一师妹发言。4 步流程，`--sub {n}`
3. 使用 **`bold-freshman-agent`** 生成研一师弟发言。4 步流程，`--sub {n}`
4. **插话判定** — `Skill("interjection-trigger")` 加载规则 → 若触发：再选一位在场 agent，加 `--interjection`（prompt 限"100-200 字短发言"）跑 4 步，然后：
   ```bash
   python .claude/scripts/update_meta.py --slug {slug} --increment interjection_count
   ```
5. **终止判定** — `Skill("discussion-terminator")` 加载规则 → 读 `discussion_log.md` 最近 3 轮 → 决定：
   - **终止** → `python .claude/scripts/update_meta.py --slug {slug} --set termination_reason={原因}`，退出循环进 R6
   - **继续** → `python .claude/scripts/update_meta.py --slug {slug} --increment r5_round_count`，`{n}` 加 1 回到步骤 1

#### R6 — 小老板1 整体升华
使用 **`expert-advisor-agent`** 生成 R6 发言。4 步流程，`target=discussion`。

→ 进入第二阶段

---

## 第二阶段：合成

1. **社交复盘** — `Skill("social-dynamics")` → Read `social_records.jsonl`（跳 sentinel）+ `discussion_log.md` + `anti_pattern_log.md` + `meeting_meta.json.history_context` → 按加载规范生成 → Write `docs/社交复盘/{slug}.md`
2. **汇报合成** — `Skill("report-synthesis")` → 严格按其 Step 1-9 执行（Read → 写 Part A → 切人格 → 写 Part B 完整流程由 skill 内部包含）→ 输出 `docs/汇报草稿/{slug}.md`（Part A 对外）+ `docs/私密备忘/{slug}.md`（Part B 对内）

**红线**：`anti_pattern_log.md` 仅允许进入 Part A 的 A3 "已识别并避开的方向" 子节；其他位置禁 Read。由 report-synthesis 内部强制实施。

→ 进入第三阶段

---

## 第三阶段：归档

1. Read `docs/私密备忘/{slug}.md`（Part B 诚实层）+ `docs/社交复盘/{slug}.md` → `research-profile.md` 末尾追加时间戳快照：

   ```markdown
   ## YYYY-MM-DD

   - **研究方向**：（一句话）
   - **当前阶段**：（一句话）
   - **持续问题**：（一句话，来自 Part B 的 B2）
   - **能力成长**：（一句话，来自 Part A 的 A2 对比 Part B 的 B1）
   - **社交进步**：（一句话，来自 docs/社交复盘/ 第 5 节）
   ```

   主观判断字段取 Part B（**不**用 Part A 包装层），避免 archive 被污染。

→ 进入第四阶段（组会未完，pptx 是终点）

---

## 第四阶段：PPTX + 展示

1. `Skill("pptx")` — 加载设计指南、pptxgenjs 使用说明、QA 要求
2. Read `docs/汇报草稿/{slug}.md`（主）+ `docs/原始汇报/{slug}.md`（补）。**禁 Read**：`docs/私密备忘/` / `anti_pattern_log.md` / `docs/社交复盘/`（私密内容禁入对外演示）
3. Write `ppt/gen_{slug}.js`：用 pptxgenjs 实现 **A1 → 封面 + 立论 2 slides** / **A2 → 每条进展 1 slide** / **A3 → 主段 1-2 slides + "已避开方向" 独立 1 页** / **A4 → 1 slide 带优先级**。商务风格，白底黑字商务蓝 + 项目符号，禁花哨配色
4. Bash `cd ppt && node gen_{slug}.js` 生成 `ppt/{slug}.pptx`
5. Glob 验证 `ppt/{slug}.pptx` 存在——不存在则修脚本重试一次；仍失败则 `python .claude/scripts/update_meta.py --slug {slug} --set files.ppt=null` 并在面板标 ❌
6. 展示面板：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 归档完成
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 原始汇报      → docs/原始汇报/{slug}.md
✅ 组会过程      → docs/组会过程/{slug}/
   ├─ discussion_log.md
   ├─ anti_pattern_log.md
   ├─ social_records.jsonl
   └─ meeting_meta.json
✅ 社交复盘      → docs/社交复盘/{slug}.md
✅ 汇报草稿      → docs/汇报草稿/{slug}.md（Part A 对外演讲稿）
🔒 私密备忘      → docs/私密备忘/{slug}.md（Part B 对内反思，仅自己看）
✅ 研究画像      → research-profile.md
🎤 演示文稿      → ppt/{slug}.pptx
```
