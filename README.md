# agent-sdlc-workflow

双模式的 Agent 时代软件工程工作流：小任务走零落盘 fast-track；完整产品项目由 Agent 主动引导 **准备 → 环境闭环 → Phase/Todo 规划 → Goal/Auto 长程执行**。

v2.0 在 v1.5 的方法论之上建立一条完整链：**Harness 能力探测 → 四维执行配置 → 与能力匹配的自主程度 → 机器捕获并绑定 revision 的证据 → 独立复核或外部硬门控 → 精确生命周期状态 → 再锚定、熔断与分层恢复 → E1–E12 真实验证**。它提供方法和模板，不复制模型、版本控制、CI 或平台权限系统已经具备的能力。

> 当前版本 `2.0.0-rc.1`：语义与工件已就位；真实 Harness binding 的 dogfood 与 E1–E12 实测是稳定版 `2.0.0` 的发布门控，见 `evals/`。

## 约束性质（先读这段）

这是**行为编排协议，不是硬控制系统**。Skill 文字只能改变 Agent 行为倾向；权限隔离、CI 阻断、分支保护、生产审批、数据恢复、原子调度与独立证据作者由 Harness、CI、权限系统与版本控制承担。门控分三类：hard（A3 外部强制）/ evidence（A0–A2，绑定 revision）/ judgment（J0/J1 人签字）。

## 核心原则

1. **验证质量决定自主权**：自主程度由可用能力与证据保证等级决定，不由提示词长度决定；能力不足时降级，不用散文伪装能力。
2. **四维正交**：规模（fast/project）、自主（copilot/auto）、风险（standard/guarded）、协作（single/multi）分别判定；AC 数量、用户要求 auto、多 Agent、单点高风险均不单独决定 Project。
3. **证据分级**：A0 self-reported / A1 tool-captured / A2 independently-replayed / A3 externally-enforced；人工 J0/J1。Agent 自填字段标 self-reported，不能升级保证等级。
4. **状态诚实**：生命周期状态机区分实现完成、自动验证通过、人工待验收、已验收、已发布、已关闭；不混报。
5. **Spec 是执行契约**：目标、非目标、假设和编号 AC 驱动实现与验证。
6. **最小落盘**：spec 记意图、ADR 记关键决策、NOTES 记进度、checkpoint 记结果与证据；不为合规生产流程资产。
7. **少打扰**：只有目标/AC 变化、新外部权限、生产/真实数据或破坏性操作真正阻塞时才合并询问。
8. **Agent 先推荐**：前三阶段由 Agent 调研、起草和解释取舍，人确认关键产品语义。
9. **分层验证**：局部 → 受影响 → Phase → Goal；输入未变复用绿色证据。

## 两种模式

- **Fast-track**：单一可验证增量、单会话可完成。直接提炼 AC，做最小计划与局部验证；**零落盘**，最终对话摘要即 A0 报告。风险升高只切 guarded 维度，不膨胀为完整 Project。
- **Project Mode**：完整产品、多里程碑、长期跨会话、多 Agent 或用户要求长程 auto。按下述四阶段主动引导。

### Project Mode 四阶段

| 阶段 | 协作 | Agent 主动引导内容 |
|---|---|---|
| 1 准备 | copilot | 需求深挖、边界、产品定位、对象/行为/事件/关系/规则五维模型、原型迭代与体验确认 |
| 2 环境 | copilot | SDD、风险驱动测试、分层回归、Review、ADR、**能力协商**、关键路径验收与本地闭环 |
| 3 规划 | copilot | 可验证 Phase、完整 Todo、AC 映射、依赖 DAG、Phase 退出门控；声明 Plan-ready/Auto-ready |
| 4 执行 | auto | 将计划作为 goal 连续执行，Phase 门控后再锚定，熔断入 auto_paused，三类恢复分离，最后按生命周期状态验收 |

**Auto-ready 以能力为前提**：`evidence_capture` 至少为 tool（A1）；guarded 需 blocking-permission 与恢复 gate；multi 需 atomic-claim。能力不足时降级，不假装可长程自治。

### 验证节奏与保证等级

```text
连贯改动 → 局部检查        任务/批次 → 受影响回归
Phase → 相关集成/契约/E2E   Goal → 最后一次代码变更后的完整/发布级绿色证据
```

Goal 最低保证：fast+standard 可 A0（须明示 self-reported）；project+auto 关键 gate ≥ A1；guarded 关键行为 ≥ A2 外加 blocking permission；hard gate 须 A3；人工验收须 J1。

## Harness 能力接口

v2.0 定义三个必需能力：`evidence-capture`、`atomic-claim`、`blocking-permission`，两个推荐能力：`independent-verify`、`isolated-workspace`。主规则只定义能力接口，不写死平台 API；具体落地见 `agent-sdlc-workflow/references/bindings/`（`generic.md` 为降级 fallback，`claude-code.md` 为已设计 binding）。binding 不可用时按能力降级，不假装成功。

## 文件范围与用户打扰

任务卡「影响区域」用于估算工作量与协调多 Agent 写冲突，**不是权限白名单**。Agent 发现漏列文件时直接修改，并在 checkpoint 概括重要影响；Git 已保留完整差异。平台权限、仓库保护、CI 和部署系统继续承担硬安全边界。

只有以下情况既需要用户决定、又没有其他安全工作可继续时才合并询问：不同解释会改变用户价值/非目标/AC；需要新外部权限、付费服务、生产或真实数据操作；操作破坏性、难恢复或超出已授权工作区。

## 初始化

```bash
python <本 skill 目录>/scripts/init_project.py ./my-project --dry-run
python <本 skill 目录>/scripts/init_project.py ./my-project
```

脚本幂等：已有文件默认跳过；会在项目 `AGENTS.md` 渲染从 `references/core-rules.md` 投影的受管规则区块（ruleset/hash）。若项目已有未受管的 `AGENTS.md`，**不覆盖、不追加**，改为生成 `AGENTS.agent-sdlc.md` 供合并，且此前项目只能是 Plan-ready。`--force` 会先备份到 `.agent-sdlc-backups/` 再覆盖 skill 拥有的文件——它**不是迁移器**，见 `MIGRATION-v1.5-to-v2.0.md`。

## 安装

`agent-sdlc-workflow.skill` 是中文版可导入包；`agent-sdlc-workflow-en.skill` 是规则 ID、行为语义和目录结构对齐的全英文适配版。两者都由 `scripts/package_skill.py` 生成并支持 allowlist + `--check` 一致性校验。也可把对应目录复制到工具的用户或项目 skills 目录：

```bash
python scripts/package_skill.py
python scripts/package_skill.py --skill-dir agent-sdlc-workflow-en -o agent-sdlc-workflow-en.skill
```

打包内文本统一为 UTF-8（无 BOM）。Windows PowerShell 5.1 读取时须显式使用 `Get-Content -Raw -Encoding UTF8`；PowerShell 7 不需要这一兼容参数。

| 工具 | 常用目录 | 中文版调用 | 英文版调用 |
|---|---|---|---|
| Codex | `~/.codex/skills/` 或 `~/.agents/skills/` | `$agent-sdlc-workflow` | `$agent-sdlc-workflow-en` |
| Claude Code | `~/.claude/skills/` 或 `.agents/skills/` | `/agent-sdlc-workflow` | `/agent-sdlc-workflow-en` |
| Kimi Code | `~/.kimi/skills/` 或 `.agents/skills/` | `/skill:agent-sdlc-workflow` | `/skill:agent-sdlc-workflow-en` |

普通单次修复、代码解释或单项 TDD 不应自动触发完整工作流。

## Skill 本体

```text
agent-sdlc-workflow/
├── SKILL.md                 # 触发、四维路由、读取顺序（常驻入口，保持短）
├── VERSION
├── agents/openai.yaml
├── references/              # canonical 创作源（按需读取）
│   ├── core-rules.md        # 全部规则唯一创作源（rule ID）
│   ├── evidence-assurance.md
│   ├── capability-contract.md
│   ├── recovery-model.md
│   └── bindings/
│       ├── generic.md
│       └── claude-code.md
├── assets/templates/        # 九个阶段/资产模板（rule ID 锚点 + 行动点摘要）
└── scripts/init_project.py
```

`agent-sdlc-workflow-en/` 保持相同运行时布局；其 `SKILL.md`、references、bindings、九个模板、初始化脚本输出和 UI 元数据均为英文。两个版本共享稳定 rule ID，便于跨语言审计和对照。

## 评测与迁移

- `evals/`：E1–E12 场景矩阵与关键指标；真实 fast-track、跨会话 Project Mode、Harness binding dogfood 与故障注入是稳定版发布门控。
- `MIGRATION-v1.5-to-v2.0.md`：人工迁移指南（不使用 `--force`，不自动改写历史产物）。

版本：v2.0（`2.0.0-rc.1`）
