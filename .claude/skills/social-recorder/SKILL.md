---
name: social-recorder
description: "[INTERNAL: group-meeting only] 学术组会四维社交分析规范（权力/面子/话术/博弈类型）+ JSON schema。仅供 group-meeting 在落盘步骤 B 通过 Skill('social-recorder') 调用，禁止在 group-meeting 流程之外自动触发。"
disable-model-invocation: false
user-invocable: false
---

# 人情世故实时记录

每次角色发言后，从以下四个维度分析并记录一条 JSON 条目。

## 分析维度

### 权力动态
- 迎合行为：谁在附和谁？具体观点还是笼统站队？
- 反驳行为：谁敢反驳谁？直接还是委婉？
- 沉默：谁在某话题上沉默？是否策略性的？
- 话语权变化：发言量与发言质量的关系

### 面子管理
- 给面子：谁在帮谁圆场或找台阶？
- 伤面子：谁被公开否定？用什么方式？
- 自我保护：谁在用什么方式保护自己？
- 面子修复：被否定后谁帮忙修复气氛？

### 话术技巧
- 委婉否定："其实那个说法可能需要再确认一下"
- 先扬后抑："做得挺好的！不过..."
- 请教式质疑："我有个基础问题..."
- 弦外之音："你可以先试试看"
- 落地化调和："老师的方向落地的话..."

### 社交博弈类型
每段发言标注为：`FOLLOW`（迎合）| `CORRECT_SOFT`（委婉纠正）| `CORRECT_HARD`（直接纠正）| `CHALLENGE`（质疑）| `SUPPORT`（鼓励）| `DEFLECT`（回避）| `BRIDGE`（调和）| `SILENCE`（策略性沉默）

## 输出 schema（与 group-meeting v4 持久化设计对齐）

每条记录是 `docs/组会过程/{date}/social_records.jsonl` 的一行 JSON。group-meeting 编排器在每条发言落盘后（"落盘三步骤"的步骤 B），按本 schema 追加一行。

```json
{
  "speech_id": "R1-big-boss",
  "round": "R1",
  "round_index": null,
  "is_interjection": false,
  "is_anti_pattern": false,
  "role": "大老板",
  "agent": "big-boss-agent",
  "source": "ai_generated",
  "timestamp": "2026-04-07T15:23:11",
  "target": "all 或 reporter / phd-brother 等指向对象",
  "power_dynamics": "（按上文 4 维度的"权力动态"4 子项一句话总结）",
  "face_management": "（按上文 4 维度的"面子管理"4 子项一句话总结）",
  "rhetoric_techniques": "（话术模板标注，例如 '弦外之音 — 你可以先试试看'）",
  "game_type": "BRIDGE",
  "key_quote": "方向很好，格局可以再大一点",
  "lesson": "学会读懂'格局再大一点'的真实含义"
}
```

### 字段约束

| 字段 | 约束 |
|---|---|
| `speech_id` | 与 `discussion_log.md` / `anti_pattern_log.md` 的二级标题锚点一一对应。命名规则见 group-meeting/SKILL.md 的 "social_records.jsonl schema" 节 |
| `round` | R1 / R2 / R3 / R4 / R5 / R6 |
| `round_index` | 仅 R5 多轮使用，整数（1, 2, 3...）；其他轮为 `null` |
| `is_interjection` | 仅 R5 插话发言为 `true`，其他为 `false` |
| `is_anti_pattern` | 仅 R2 mixed-advisor 发言为 `true`，其他为 `false` |
| `role` | 大老板 / 小老板1 / 小老板2 / 博士师姐 / 博士师兄 / 汇报者 / 硕一师妹 / 研一师弟 |
| `agent` | big-boss-agent / mixed-advisor-agent / expert-advisor-agent / phd-sister-agent / phd-brother-agent / reporter-agent / curious-junior-agent / bold-freshman-agent |
| `source` | `ai_generated` 或 `manual`（manual 模式 R4/R5 用户亲自输入） |
| `target` | 指向对象的 agent 短名（big-boss / phd-brother 等），或 `all` 表示泛指全场 |
| `game_type` | **必须**是上文"社交博弈类型"枚举的 8 个之一：FOLLOW / CORRECT_SOFT / CORRECT_HARD / CHALLENGE / SUPPORT / DEFLECT / BRIDGE / SILENCE |
| `key_quote` | 本次发言里最能代表立场的一句原话，不要超过 30 字 |
| `lesson` | 从这条发言能学到的一条社交智慧，一句话 |

### 后续读取

`social_records.jsonl` 由 group-meeting 编排器在第二阶段步骤 1 Read，按 social-dynamics 模板生成 `docs/社交复盘/{date}.md`；report-synthesis 在 Step 1 也 Read 此文件用于 A5 防御话术抽取。读取时需跳过任何带 `_sentinel: true` 的 sentinel 行。
