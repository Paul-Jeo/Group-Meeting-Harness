---
name: social-patterns
description: 学术组会社交话术知识库（导师潜台词/向上管理/面子管理/冲突场景/权力动态），由角色 agent 通过 skills 字段预加载。
disable-model-invocation: true
user-invocable: false
allowed-tools: Read Glob
---

# 话术模式库 (Social Rhetoric Pattern Library)

学术组会社交交互的结构化模式库 | 导师潜台词 | 话术模板 | 冲突场景 | 权力博弈

---

## 加载方式

本 Skill 通过**subagent 的 `skills:` 字段预加载**（全量注入 SKILL.md 到 context）。
支持文件（子目录 markdown）需要通过 Read 工具显式加载。推荐引用方式：

| 使用者 | 加载方式 |
|--------|---------|
| 角色 Agent | 在 frontmatter 的 `skills:` 字段加入 `social-patterns` — SKILL.md 自动注入，子文件按需 Read |
| group-meeting 编排器 | 生成 social_dynamics.md 时通过 Read 读取相关子目录文件 |

### 预加载后的使用

需要使用话术知识时，通过相对路径 Read 子目录文件（相对项目根目录）：
```
docs/social-patterns/advisor-subtext/big-boss-subtext.md
```

Agent 应在发言前，根据角色定位选择性 Read 最相关的 1-2 个子文件：
- **大老板** → `advisor-subtext/big-boss-subtext.md`
- **小老板2** → `advisor-subtext/mixed-advisor-traps.md`
- **博士师兄/师姐** → `rhetoric-patterns/peer-interaction.md`、`rhetoric-patterns/defense-tactics.md`
- **汇报者** → `rhetoric-patterns/upward-management.md`、`rhetoric-patterns/high-pressure-moments.md`
- **师弟/师妹** → `rhetoric-patterns/junior-questioning.md`
- **小老板1** → `power-dynamics/advisor-archetypes.md`、`power-dynamics/game-theory-cases.md`

---

## 目录结构

```
social-patterns/
├── SKILL.md                              ← 本文件（索引）
├── advisor-subtext/                      ← 导师潜台词库
│   ├── big-boss-subtext.md               ← 大老板弦外之音（34条）
│   ├── mixed-advisor-traps.md            ← 小老板2甜蜜陷阱（20条）
│   └── advisor-manipulation-tactics.md   ← 导师操控手段识别（23条 + 决策树）
├── rhetoric-patterns/                    ← 话术模式库
│   ├── upward-management.md              ← 向上管理话术（21条）
│   ├── peer-interaction.md               ← 同辈交互话术（16条）
│   ├── junior-questioning.md             ← 低年级提问话术（12条）
│   ├── defense-tactics.md                ← 防御性话术（15条）
│   ├── face-management.md                ← 面子管理话术（15条）
│   ├── high-pressure-moments.md          ← 高压时刻话术（17条：微信/深夜/请假/情绪处理）
│   └── team-dynamics.md                  ← 团队内部动态话术（18条：派系/竞争/边界/新人融入）
├── conflict-scenarios/                   ← 冲突场景库
│   ├── scenario-templates.md             ← 场景模板格式
│   ├── high-freq-conflicts.md            ← 10个基础冲突场景
│   └── extended-conflicts.md             ← 10个复杂冲突场景（团队分化/红白脸/毕业/线上）
└── power-dynamics/                       ← 权力动态模式
    ├── hierarchy-patterns.md             ← 5层权力互动模式
    ├── game-theory-cases.md              ← 12类博弈 × 3案例 = 36案例
    ├── advisor-archetypes.md             ← 3基础+5衍生导师类型画像 + 匹配指南
    └── nonverbal-signals.md              ← 非语言信号与"读空气"（座位/表情/沉默/节奏/肢体/线上）
```

---

## 面子双层模型

本库区分两种面子类型（Brown & Levinson + 中国本土概念）：

| 类型 | 英文 | 含义 | 损伤后果 | 修复难度 |
|------|------|------|----------|----------|
| **面子 (Mianzi)** | Social prestige | 社会声望、能力认可 | 尴尬、地位下降 | 可修复 |
| **脸 (Lian)** | Moral standing | 道德人品、学术诚信 | 信任崩塌、社交排斥 | 极难修复 |

social-recorder 记录时应标注威胁的是 mianzi 还是 lian。

---

## 博弈类型标签（扩展版）

| 标签 | 中文 | 含义 | 面子影响 |
|------|------|------|----------|
| FOLLOW | 迎合 | 附和/跟随权威观点 | 给对方面子 |
| CORRECT_SOFT | 委婉纠正 | 不点名地纠正错误 | 留面子式批评 |
| CORRECT_HARD | 直接纠正 | 用事实直接推翻 | 可能伤面子 |
| CHALLENGE | 质疑 | 挑战根本假设 | 高面子风险 |
| SUPPORT | 支持 | 引用数据/经验背书 | 给面子 |
| DEFLECT | 回避 | 转移话题/延迟回应 | 自我面子保护 |
| BRIDGE | 调和 | 连接对立观点 | 双方面子都顾 |
| SILENCE | 沉默 | 策略性不发言 | 可能是最强否定 |
| REFRAME | 重新框架 | 把负面结果转为正面叙事 | 面子重建 |
| DELEGATE | 借刀 | 借他人之口表达自己观点 | 避免直接冲突 |
| ESCALATE | 升维 | 将技术问题升至原则层面 | 提高博弈筹码 |
| TRAP | 甜蜜陷阱 | 用热情包装错误建议 | 表面给面子实则挖坑 |

---

## 数据来源

本库内容提炼自以下调研报告（原始素材存档于 `docs/`）：

- `docs/知乎学术组会社交话术研究.md`
- `docs/小木虫学术社交动态研究报告.md`
- `docs/话术模式库-研究素材.md`
- `docs/学术社交动态深度研究_英文源.md`

所有内容均为**模式提炼**，不含原帖原文，已匿名化处理。
