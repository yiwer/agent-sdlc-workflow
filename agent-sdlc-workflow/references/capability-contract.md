# Harness 能力契约（Capability Contract）

> 支撑 `RULE-AUT-001 / RULE-CLAIM-001 / RULE-GUARD-001 / RULE-GOAL-001`。
> 核心命题：**先定义能力接口，再绑定具体 Harness；文件机制只能是 fallback。** Skill 是行为编排器，不自造虚假能力——缺失能力时降级。

## 必需能力

| 能力 | 目的 |
|---|---|
| `evidence-capture` | 自动捕获 gate 执行、revision、结果与原始输出（A1 及以上的前提） |
| `atomic-claim` | 原子领取任务，防止多 Agent 双领 |
| `blocking-permission` | 对生产、真实数据、难恢复与越权操作提供真实阻断（guarded auto 的前提） |

## 推荐能力（非所有项目必需）

| 能力 | 目的 |
|---|---|
| `independent-verify` | 新上下文、独立 Agent 或 CI 重跑关键 gate（A2 的来源） |
| `isolated-workspace` | 为并行写入者提供 branch/worktree/沙箱隔离 |

## 能力协商

进入 Project Mode 时，Agent 先检查现有 Harness、issue tracker、CI 与权限系统，形成结论（不是让用户填表；只有产品语义、授权或风险选择必须由人决定时才询问）：

```yaml
capabilities:
  evidence_capture: self | tool | independent | enforced
  atomic_claim: harness | tracker | file | none
  blocking_permission: harness | human | none
  independent_verify: available | unavailable
  isolated_workspace: available | unavailable
```

- `evidence_capture: self` = 仅 A0；`tool` = A1；`independent` = A2；`enforced` = A3。
- 能力写入项目环境清单（`plans/env-gates-checklist.md`），作为 Auto-ready 判据。

## 能力与执行模式的关系

| 条件 | 裁定 |
|---|---|
| `evidence_capture = self` | 可以 fast-track；Project 只能保持 copilot / Plan-ready |
| Project Auto | `evidence_capture` 至少为 `tool`（A1） |
| guarded Auto | 必须有 `blocking_permission` 与对应恢复 gate |
| multi Auto | 必须有 `atomic_claim`；否则串行化或降级 |
| 关键 Goal / 发布 | 优先要求 `independent-verify`（A2） |

## 缺失能力时降级（不自造虚假能力）

| 缺失 | 降级动作 |
|---|---|
| 无机器证据捕获 | 不进入 Project Auto，保持 copilot/Plan-ready |
| 多 Agent 无原子 claim | 改单写入者或协调者串行派发，不宣称 multi Auto-ready |
| guarded 无阻断权限 | 不允许 auto，由人审批，不用文本代替权限 |
| 无数据恢复机制 | 不把源码回退称为完整恢复，显式标注未覆盖项 |

## Harness binding 要求

主规则只定义能力接口，**不把具体平台 API 写死**。具体实现放入按需读取的 `references/bindings/`（`generic.md` 与已实测 harness 各一份）：

- binding 标明适用版本或验证日期；
- 优先复用 Harness 原生工具、任务系统、hooks、权限与 CI；
- binding 不可用时回退到能力降级，而不是假装成功；
- v2.0 稳定版发布前至少一个真实 binding 完成 dogfood（RC 阶段标注未实测）。
