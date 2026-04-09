# 🎓 Group Meeting Harness

> 全世界科研能力下降100倍，这次我带了组会harness来开组会！！！

<br>

<p align="center">
🌙 凌晨三点，ppt 改到第 8 版<br>
🐉 导师甩一句："格局再大一点"——你：？？？<br>
🦊 小老板："用那个新方法试试"——一周后发现是坑<br>
🌸 师姐已毕业，再也没人给你翻译弦外之音<br>
⏰ 八点开会，你还没想好开场第一句话<br>
</p>

<p align="center"><b>别怕，这次你带了 8 个 AI 进组会。</b></p>

<p align="center">
📝 <b>直接能交的</b>：汇报文案 + 商务风 PPT（导师看了都沉默）<br>
🕵️ <b>偷偷给你的</b>：那句"很有意思"到底是夸你还是劝你跑路，弦外之音翻译成人话<br>
🩹 <b>顺手帮你的</b>：8 个角色先把你往死里骂一遍，真组会上就不疼了<br>
🧠 <b>默默记着的</b>：上周说的行动项做了没？AI 都给你记着——虽然导师都不记着<br>
</p>

<p align="center"><b><i>在中国读研，你不只要学会做研究，还要学会做人。</i></b></p>

<p align="right"><i>——不知名研究生</i></p>

---

## 快速开始

```bash
git clone https://github.com/Paul-Jeo/group-meeting-skill.git
cd group-meeting-skill

# 第四阶段的 PPT 生成依赖 pptxgenjs（首次使用必装，否则 pptx skill 会报缺依赖）
cd ppt && npm install pptxgenjs && cd ..

claude
```

```
/group-meeting 这周在做对比学习的消融实验，准确率到了75%，但不知道该怎么分析结果...
```

选择讨论模式：

- **1️⃣ AI 全自动** — 8 个角色全部 AI 扮演，你坐着看就行
- **2️⃣ 亲自上场** — R4/R5 中"你自己"的发言由你在对话框输入，练习真实组会应答

---

## 谁在开会

```
                    ┌─────────────┐
                    │  你提交汇报  │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
    ┌─────┴──────┐   ┌─────┴──────┐   ┌─────┴──────┐
    │   导师层    │   │   博士层    │   │   新锐层    │
    │            │   │            │   │            │
    │ 🐉 大老板  │   │ 🌸 博士师姐 │   │ 🎓 你自己   │
    │ 🦊 小老板2 │   │ 🐺 博士师兄 │   │ 🐱 硕一师妹 │
    │ 🦅 小老板1 │   │            │   │ 🦁 研一师弟 │
    └────────────┘   └────────────┘   └────────────┘

    每个角色独立 SubAgent · 隔离上下文 · 互不可见推理过程
```

| 角色        | 代号     | 干什么                                            | 杀伤力            |
| ----------- | -------- | ------------------------------------------------- | ----------------- |
| 🐉 大老板   | 造梦大师 | "如果能和量子计算结合，那就是 Nature"             | 画饼 MAX          |
| 🦊 小老板2  | 人情练达 | 意见 100% 错误——**这是 feature 不是 bug** | 带偏能力 MAX      |
| 🌸 博士师姐 | 温柔の刀 | "做得挺好的！不过 reviewer 可能会问..."           | 温柔一刀          |
| 🐺 博士师兄 | 善战の狼 | "SOTA 是 82.3，你差了 7 个点。消融实验做了没？"   | 物理伤害          |
| 🎓 你自己   | 当局者迷 | 五方建议全矛盾，你来拍板                          | 自我怀疑          |
| 🐱 硕一师妹 | 好奇宝宝 | "学长我有个可能比较基础的问题..." 全场沉默        | 暗杀              |
| 🦁 研一师弟 | 初生牛犊 | "等一下，为什么不直接用 XX？"                     | 12% 天才 88% 胡说 |
| 🦅 小老板1  | 定海神针 | 综合所有人，给你一份下周一能动手的计划            | 定海              |

---

## 怎么开的会

这不是随机闲聊，是按 **TDD（测试驱动开发）** 设计的结构化流程：

```
第零阶段  初始化（一键脚本）
              ↓
第一阶段  R1  🐉 大老板定调              Red      ← 先画个大饼
         R2  🦊 小老板2 全错引爆         Red      ← 故意给错方向（帮你排雷，物理隔离进 anti_pattern_log）
         R3  🌸🐺 师姐+师兄并行纠偏      Green    ← 纠正错误，给出真建议
         R4  🎓 你回应                            ← 消化矛盾，做出判断
         R5  🎓🐱🦁 自由讨论循环                  ← 追问 + 插话 + 自动终止
         R6  🦅 小老板1 收尾             Refactor ← 炼成可执行计划
              ↓
第二阶段  合成：社交复盘 + 汇报草稿（Part A 对外）+ 私密备忘（Part B 对内）
              ↓
第三阶段  归档：更新 research-profile.md 时间戳快照
              ↓
第四阶段  pptx：生成下周组会用的 ppt/{date}.pptx（真实文件存在才算完成）
```

> **为什么小老板2要全错？** 真实组会里总有人给你错误建议。让你提前见识过错的，才不会在真正的组会里被带偏。博士层在 R3 会把错纠回来——从师兄那里过了，reviewer 那里大概率也过得了。

---

## 输出什么

每次组会结束，自动生成以下产物（`{slug}` = 会议日期，同日重名自动加 `-2 / -3`）：

| 文件                                          | 你拿来干什么                                       |
| --------------------------------------------- | -------------------------------------------------- |
| `docs/原始汇报/{slug}.md`                   | 你交给组会的原始版本存档                           |
| `docs/组会过程/{slug}/discussion_log.md`    | 8 角色完整发言记录（R1-R6）                        |
| `docs/组会过程/{slug}/anti_pattern_log.md`  | R2 反例物理隔离区（禁入对外汇报）                  |
| `docs/组会过程/{slug}/social_records.jsonl` | 每条发言的社交四维结构化数据                       |
| `docs/组会过程/{slug}/meeting_meta.json`    | 会议元信息 + 历史上下文                            |
| `docs/社交复盘/{slug}.md`                   | 权力博弈、面子管理、话术技巧、社交评分             |
| **`docs/汇报草稿/{slug}.md`**         | **Part A 对外演讲稿 — 直接当周报交给导师**  |
| 🔒`docs/私密备忘/{slug}.md`                 | Part B 诚实层，只给自己看（禁入 PPT）              |
| **`ppt/{slug}.pptx`**                 | **下周组会用的商务风 PPT（pptxgenjs 生成）** |
| `research-profile.md`                       | 研究画像时间戳快照，开得越多 AI 越了解你           |

> **对外 / 对内双输出**：汇报草稿是包装后的公开版；私密备忘是真实反思版。下次组会 AI 会从 `research-profile.md` 加载最近 3 次历史，自动接上行动项跟进，不从零开始。

---

## 让角色更像你身边的人

每个角色可以自定义。在 `.claude/skills/<角色>/character/` 放一个 md 文件：

```markdown
<!-- .claude/skills/phd-brother/character/my-senior.md -->

口头禅：
- "你这个 loss 不对"
- "看 XX 组的 repo，他们去年就做过了"

风格：说话极简，从不超过三句。回复完就戴耳机。
对你的态度：不讨厌你但也不会主动帮你，除非你问到了点子上。
```

Agent 会优先读取你的自定义文件，覆盖默认人设。你可以把真实导师、师兄的说话风格喂进去，模拟得更真实。

---

## 项目结构

```
人情事故group-meeting-skill/
├── .claude/
│   ├── skills/                     # 15 个 Skills
│   │   ├── group-meeting/          #   主编排器 ← /group-meeting 入口
│   │   ├── big-boss/               #   🐉 大老板人设（含 character/ 自定义）
│   │   ├── mixed-advisor/          #   🦊 小老板2
│   │   ├── expert-advisor/         #   🦅 小老板1
│   │   ├── phd-sister/             #   🌸 博士师姐
│   │   ├── phd-brother/            #   🐺 博士师兄
│   │   ├── reporter/               #   🎓 你自己
│   │   ├── curious-junior/         #   🐱 硕一师妹
│   │   ├── bold-freshman/          #   🦁 研一师弟
│   │   ├── social-recorder/        #   社交数据实时记录（四维 schema）
│   │   ├── social-dynamics/        #   社交复盘六段式输出
│   │   ├── report-synthesis/       #   双输出汇报合成（Part A / Part B）
│   │   ├── interjection-trigger/   #   R5 插话触发规则
│   │   ├── discussion-terminator/  #   R5 讨论终止规则
│   │   └── pptx/                   #   第四阶段 PPT 生成
│   ├── agents/                     # 8 个 SubAgents（隔离上下文 + 预加载 skill）
│   ├── scripts/                    # Python 编排脚本（机械操作走脚本，不手搓）
│   │   ├── init_meeting.py         #   第零阶段一键初始化
│   │   ├── build_prompt.py         #   构造 sub-agent XML prompt
│   │   ├── append_speech.py        #   落盘发言（sentinel 追加）
│   │   ├── append_social_record.py #   追加 JSON 到 social_records.jsonl
│   │   └── update_meta.py          #   meta 字段 increment / set
│   ├── hooks/                      # SubagentStop 校验 hook
│   ├── settings.json               # 全局设置（含 Bash / Python 权限）
│   └── settings.local.json
├── docs/
│   ├── social-patterns/            # 话术 / 权力博弈 / 冲突场景 研究素材库（人情世故知识底座）
│   ├── 原始汇报/                   # 🔒 用户原始版存档
│   ├── 组会过程/{slug}/            # 🔒 discussion + anti_pattern + social_records + meta
│   ├── 社交复盘/                   # 🔒 权力博弈 / 面子管理 / 话术分析
│   ├── 汇报草稿/                   # 🔒 Part A 对外版
│   └── 私密备忘/                   # 🔒 Part B 对内版
├── ppt/                            # pptxgenjs 生成的 .pptx + 源 .js
├── research-profile.md             # 研究画像（时间戳快照，历史自动加载）
└── README.md
```

**分层职责**：Skill 管内容（人设 + 评审规范），Agent 管执行（模型 + 工具权限 + 上下文隔离），Python 脚本管机械操作（文件 I/O + prompt 构造），主编排器管流程（四阶段 + TDD 六轮）。

---

## 环境要求

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- （可选）[Zotero MCP](https://github.com/anthropics/claude-code) — 博士师兄和小老板1 可以搜你的文献库

---

## 为什么做这个

在中国读研，组会是最重要的学术训练场。但大多数人从组会中学到的不到 30%——不是讨论不充分，是你不知道该听谁的、该忽略什么、什么是弦外之音。

这个工具做两件事：

1. **学术上**：帮你在真正的组会前预演一遍，把能踩的坑先踩了
2. **社交上**：把组会里看不见的权力博弈、面子管理、话术技巧显性化，变成你可以学习的知识

---

<p align="center">
  <i>"读研三年，论文是次要的，学会做人才是主要的"</i><br>
  <i>—— 某不愿透露姓名的研究生</i>
</p>
