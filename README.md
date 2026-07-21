# agent-sdlc-workflow

双模式的 Agent 时代软件工程工作流：小任务 fast-track；完整项目由 Agent 主动引导 **准备 → 环境闭环 → Phase/Todo 规划 → Goal/Auto 长程执行**。

它提供方法和模板，不复制模型、版本控制、CI 或平台权限系统已经具备的能力。核心假设是：模型能够判断普通实现细节；文档只保存跨会话不可替代的意图、决策和证据。

## 核心原则

1. **Spec 是执行契约**：目标、非目标、假设和编号 AC 驱动实现与验证。
2. **验证决定自主权**：反馈回路越可靠，Agent 越能自主执行。
3. **目标内自主**：完成当前 goal 所需的仓库文件可直接修改，不逐文件审批、不维护白名单。
4. **最小落盘**：spec 记意图，ADR 记关键决策，NOTES 记进度，checkpoint 记结果和证据。
5. **少打扰**：只有目标/AC 变化、新外部权限、生产/真实数据或破坏性操作真正阻塞时才询问用户。
6. **Agent 先推荐**：前三阶段由 Agent 调研、起草和解释取舍，人确认关键产品语义；不是让人从空白模板开始填。

## 两种模式

- **Fast-track**：从用户请求提炼 AC，做最小计划、实现并验证；适合单次修复、小功能和临时原型。
- **Project Mode**：适合完整产品、多里程碑、长期跨会话、多 Agent 或需要先 copilot 再 auto 的项目。

### Project Mode 四阶段

| 阶段 | 协作模式 | Agent 主动引导内容 |
|---|---|---|
| 1 准备 | copilot | 需求深挖、边界、产品定位、对象/行为/事件/关系/规则五维模型、原型迭代与体验确认 |
| 2 环境 | copilot | 推荐并落实 SDD、TDD/测试先行、独立 Review、ADR、端到端验收、本地运行/部署闭环 |
| 3 规划 | copilot | 可验证 Phase、完整 Todo、AC 映射、依赖 DAG、Phase 退出门控；人确认后移交 auto |
| 4 执行 | auto | 将整个计划作为 goal 连续执行，通过门控后自动推进，最后完成 AC 验收与沉淀 |

工程实践不是一刀切硬编码。Agent 应逐项给出推荐；用户可以采用、调整或标为不适用。已有等价能力直接复用，不机械补流程；不适用项简述理由。

原型选择能回答当前不确定性的最低成本形态，不默认开发可运行 UI。规划完成但环境尚未实测时标记 `Plan-ready`；只有反馈闭环与工程 canary 已跑通才标记 `Auto-ready`，避免过早移交长程执行。

内部模板仍使用六个细分视角：原始阶段 1 对应规格；阶段 2 对应宪章+环境闭环；阶段 3 对应规划；阶段 4 对应执行+验收。

单会话小任务和临时原型不运行脚手架、不强制创建 spec/plan/checkpoint 文件；用户请求、代码与最终验证摘要已经足够。不要为了证明遵守流程而生产流程资产。

## 文件范围与用户打扰

任务卡可写“影响区域”，帮助估算工作量和避免多 Agent 写冲突，但它不是权限白名单。Agent 发现漏列文件时直接修改，并在 checkpoint 概括重要影响；Git 已经保留完整文件差异，无需再维护逐文件台账。

只有以下情况既需要用户决定、又没有其他安全工作可继续时才询问：

- 不同解释会改变用户价值、非目标或 AC；
- 需要新外部权限、付费服务、生产或真实数据操作；
- 操作破坏性、难恢复或超出已授权工作区。

平台权限、仓库保护、CI 和部署系统继续承担硬安全边界。本 skill 不尝试用文件名规则复制它们。

## 初始化

```bash
python agent-sdlc-workflow/scripts/init_project.py ./my-project --dry-run
python agent-sdlc-workflow/scripts/init_project.py ./my-project
```

脚本幂等：已有文件默认跳过。`--force` 会先备份到项目内 `.agent-sdlc-backups/` 再覆盖。

生成结构：

```text
项目根/
├── CONSTITUTION.md
├── AGENTS.md
├── NOTES.md
├── specs/
│   ├── TEMPLATE-spec.md
│   └── changes/TEMPLATE-change.md
├── plans/
│   ├── env-gates-checklist.md
│   ├── TEMPLATE-phase-plan.md
│   ├── execution-protocol.md
│   ├── TEMPLATE-acceptance-retro.md
│   └── logs/TEMPLATE-checkpoint.md
├── docs/adr/TEMPLATE.md
└── tests/
```

## 安装

`agent-sdlc-workflow.skill` 是可直接导入的打包文件。也可把 `agent-sdlc-workflow/` 复制到工具的用户或项目 skills 目录：

| 工具 | 常用目录 | 显式调用 |
|---|---|---|
| Codex | `~/.codex/skills/` 或 `~/.agents/skills/` | `$agent-sdlc-workflow` |
| Claude Code | `~/.claude/skills/` 或 `.agents/skills/` | `/agent-sdlc-workflow` |
| Kimi Code | `~/.kimi/skills/` 或 `.agents/skills/` | `/skill:agent-sdlc-workflow` |

普通单次修复、代码解释或单项 TDD 不应自动触发完整工作流。

## Skill 本体

```text
agent-sdlc-workflow/
├── SKILL.md
├── agents/openai.yaml
├── scripts/init_project.py
└── assets/templates/
    ├── phase0-constitution.md
    ├── phase1-spec-modeling.md
    ├── phase2-env-gates.md
    ├── phase3-phase-planning.md
    ├── phase4-execution-protocol.md
    ├── phase5-acceptance-retro.md
    ├── TEMPLATE-spec-change.md
    ├── TEMPLATE-adr.md
    └── TEMPLATE-checkpoint.md
```

版本：v1.4
