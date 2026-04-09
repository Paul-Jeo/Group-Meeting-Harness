---
name: discussion-terminator
description: "[INTERNAL: group-meeting only] R5 自由讨论 5 条终止判定（重复/客套/偏题/超轮/无新问题）。仅供 group-meeting 在 R5 每轮发言后通过 Skill('discussion-terminator') 调用。"
disable-model-invocation: false
user-invocable: false
---

# 讨论终止检测

R5 自由讨论中每轮发言后执行，满足**任一**条件则终止。

## 终止条件

1. **内容重复** — 当前发言 50%+ 观点已在前面出现过（语义相似度判断）
2. **客套话过多** — "对对对""说得对""有道理"等附和性表达占比 > 60%
3. **偏离主题** — 讨论内容与原始研究汇报相关度 < 30%
4. **最大轮次** — 已达 5 轮（每轮 = 汇报者 + 师妹 + 师弟各一次）
5. **无新问题** — 连续两轮无新问题或新角度

## 执行

- 终止 → 输出终止原因 → 进入 R6
