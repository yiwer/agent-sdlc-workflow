---
name: agent-sdlc-workflow
description: 用双模式 Agent SDLC 组织软件开发。小任务走零落盘 fast-track；完整产品项目由 Agent 主动引导四阶段 Project Mode。以四维正交配置（规模/自主/风险/并发）取代二元路由，用 Harness 能力契约决定可达自主程度，用 A0–A3/J0–J1 证据保证等级区分自证、机器捕获、独立复核与外部硬门控，并以生命周期状态机诚实报告进度。覆盖需求深挖、五维建模与原型、SDD/风险驱动测试/Review/ADR、Phase/Todo/退出门控、再锚定/熔断/分层恢复与 Goal/Auto 长程执行。用于新产品、长期跨会话、多里程碑或多 Agent 项目；普通一次性修复不自动触发完整流程。
---

# Agent SDLC

## 本 skill 的约束性质（先读这段）

这是**行为编排协议，不是硬控制系统**（`RULE-HARD-001`）。Skill 文字只能改变 Agent 行为倾向，不能提供权限隔离、CI 阻断、分支保护、生产审批、数据恢复、原子调度或独立证据作者——这些由 Harness、CI、权限系统与版本控制承担。凡能交给它们强制的，不靠本 skill 自律。

「门控」分三类，不得混淆：

- **hard**：由 CI/权限/分支保护/部署审批真实阻断，本 skill 只引用其结果（A3）；
- **evidence**：Agent 可执行，但必须留下绑定 revision 的原始结果，并按保证等级标注（A0–A2）；
- **judgment**：确需人签字（体验/业务/风险判断），显式标 J0/J1，不以自证代替。

## 核心命题

- **验证质量决定自主权**（`RULE-AUT-001`）：自主程度不由提示词长度决定，而由可用能力与证据保证等级决定。能力或证据不足时降级，不用散文伪装能力已存在。
- **`Plan-ready` ≠ `Auto-ready`**：有计划只代表可审阅；只有本地反馈闭环与工程 canary 实测、且证据捕获能力就位后，才代表可长程自治。

## 选择最轻的充分流程（四维判定，RULE-MODE-001 / RULE-FAST-001）

保留 fast-track / Project Mode 作为用户界面，内部用四个正交维度分别判定：

| 维度 | 取值 | 判据 |
|---|---|---|
| 交付规模 | `fast` / `project` | 单一可验证增量且单会话可完成→fast；多可发布增量、跨会话或需持续计划/DAG→project |
| 自主程度 | `copilot` / `auto` | 产品语义/风险/验证能力仍需人→copilot；spec、计划、canary、证据捕获与恢复入口均已验证→auto |
| 风险 | `standard` / `guarded` | 可逆局部无生产/真实数据/权限影响→standard；生产/真实数据/迁移/权限/安全/付费/难恢复→guarded |
| 协作 | `single` / `multi` | 一个写入者→single；两个及以上并发写入者→multi |

**AC 数量、用户要求 auto、使用多 Agent、单点高风险操作，均不单独决定 Project**——它们分别影响自主、并发、风险维度。先读已有 `CONSTITUTION.md`、`AGENTS.md`、`NOTES.md`、`specs/`、`plans/`；已有等价产物直接复用，不机械补流程。

## 读取顺序

- 路由与四阶段编排：本文件。
- 完整行为规则（唯一创作源）：`references/core-rules.md`。
- 证据保证等级与记录：`references/evidence-assurance.md`。
- 能力协商与降级：`references/capability-contract.md`。
- 分层恢复：`references/recovery-model.md`。
- 具体平台落地：`references/bindings/<harness>.md`（无对应 binding 时用 `generic.md` 并降级）。

持久项目可运行 `python <本 skill 目录>/scripts/init_project.py <项目根> --dry-run`，确认后去掉 `--dry-run`。阶段可迭代交织；默认在前三阶段形成足够清晰的产品、闭环与计划，再集中确认并切换 auto。

## Project Mode：四阶段

前三阶段 copilot：Agent 先调查、给草案与推荐，人确认产品语义与关键取舍，不让用户从空白模板填写。第四阶段切 auto：把已确认计划视为完整 goal，连续执行到门控全部通过。

1. **Preparation**（读 `assets/templates/phase1-spec-modeling.md`）：深挖用户/场景/价值/非目标/假设/边界；五维建模（对象/行为/事件/关系/规则，允许 N/A 但须经判断，`RULE-MIN-001`）；选最低成本原型回答当前不确定性；问题回填模型与编号 AC；阶段末集中确认。
2. **Environment**（读 `phase0-constitution.md` + `phase2-env-gates.md`）：推荐工程基线（SDD/测试先行/独立 Review/ADR/边界验收/本地闭环）；**能力协商**形成 capabilities 结论（`references/capability-contract.md`）；用最小 canary 干跑「改→验→本地运行→自证」。
3. **Planning**（读 `phase3-phase-planning.md`）：按端到端可验证增量分 Phase，高风险前置；细化任务卡（关联 AC/依赖/局部验证/升级条件/完成信号）；写自动退出门控与无环 DAG；声明 `Plan-ready`/`Auto-ready`——**Auto-ready 要求 `evidence_capture` 至少为 tool（A1）**。
4. **Goal Execution**（读 `phase4-execution-protocol.md` + `phase5-acceptance-retro.md`）：把 Todo/AC/门控作为一个 goal 连续执行；按层级扩大回归；**每个 Phase 门控后再锚定**（`RULE-ANCHOR-001`）；熔断入 `auto_paused`（`RULE-BREAK-001`）；三类恢复分离（`RULE-REC-001`）；完成后按生命周期状态机如实报告（`RULE-STATE-001`）。

## 验证节奏（RULE-VAL-001，行动点摘要）

局部→受影响→Phase→Goal 逐级扩大；连贯改动后跑最短局部检查，不每次编辑后全量回测；共享契约/schema/权限/安全/依赖/全局配置/并发/迁移/基础设施变化或影响面扩大时提前升级；输入未变复用最近绿色证据。完整语义见 `references/core-rules.md`；本项目各级命令见 `CONSTITUTION.md`。

## 用户介入边界（RULE-USER-001）

仅当目标/非目标/AC 必变、需新外部授权/付费/生产或真实数据、操作破坏性难恢复或越权，且无其他安全任务可继续时，才合并询问。普通失败、漏列文件（`RULE-SCOPE-001`）、等价重构、实现选择、首次诊断由 Agent 自判。

## 最小落盘（RULE-MIN-001）

spec 记意图、ADR 记关键取舍、NOTES 记进度、checkpoint 记结果与证据。不为合规生产流程资产；无新知识记「无变更」。fast-track 不创建任何流程文件，最终对话摘要即 A0 报告。

## 完成判据

按生命周期状态机（`RULE-STATE-001`）如实报告，对照每条 AC 收集对应保证等级的证据（`RULE-GOAL-001`）：承诺 AC 有可定位证据，hard gate 由 A3 满足，人工验收显式标 J0/J1；spec/实现/测试/关键 ADR 一致；未完成项明确处置。自动 gate 过而人工 pending 报 `automated_verified`，不报 `accepted`。详见 `assets/templates/phase5-acceptance-retro.md`。
