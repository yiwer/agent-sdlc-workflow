# agent-sdlc-workflow

Agent 时代的软件工程六阶段工作流，以 Kimi Skill 形式封装。让 AI agent 按统一纪律完成从需求到交付的全过程：**宪章立法 → 需求与五维建模 → 环境闭环 → Phase 任务规划 → 长程执行（含回流）→ 验收沉淀**。

核心理念：agent 时代，人的工作从"写代码"上移到**定义问题、定义验证、定义边界**。本 skill 把这九个字变成可执行的规程、模板与门控。

## 特性

- **六阶段全流程**：覆盖一个软件项目从立项到复盘的完整生命周期，每阶段带明确的退出门控
- **copilot / auto 分工**：前四阶段人机协同（立法），执行阶段 agent 自治（低干预、高可见）
- **一键脚手架**：`init_project.py` 生成完整项目治理骨架（宪章、AGENTS.md、NOTES.md、specs/plans/adr 目录）
- **可执行验收**：验收标准采用 EARS 句式逐条编号，任务卡、playwright 测试全程可追溯
- **spec 回流机制**：执行中发现前期假设错误时的唯一合法变更路径（停→记→改→审→续），防漂移
- **沉淀飞轮**：阶段 5 复盘资产回写宪章与模板，skill 随使用迭代成"你自己的方法论"
- **fast-track 分流**：小变更走快轨但仍留 spec 记录，纪律不断

## 六阶段总览

| 阶段 | 名称 | 模式 | 核心产出物 | 模板 |
|:--:|------|:--:|------|------|
| 0 | 宪章 Constitution | copilot | 不可变原则、质量门槛、agent 自主边界、升级条件 | `phase0-constitution.md` |
| 1 | 需求与五维建模 | copilot | 需求规格、五维模型（对象/行为/事件/关系/规则）、EARS 验收标准、原型验证 | `phase1-spec-modeling.md` |
| 2 | 环境与闭环 | copilot | 自动化质量回路、agent 基础设施、部署流水线、干跑验证 | `phase2-env-gates.md` |
| 3 | 规划与切分 | copilot | Phase DAG、任务卡（含上下文预算）、退出门控、并行护栏 | `phase3-phase-planning.md` |
| 4 | 长程执行 | auto | 代码、checkpoint 证据、偏差与回流台账 | `phase4-execution-protocol.md` |
| 5 | 验收与沉淀 | copilot | 一致性审计、过程数字复盘、宪章/模板修订（飞轮） | `phase5-acceptance-retro.md` |

质量模型：**阶段 1、2 决定质量上限，阶段 3 决定上限的兑现率。**

## 安装

本 skill 遵循 Agent Skills 开放标准（`SKILL.md` + frontmatter），同一份文件可在 Kimi、Claude Code、Codex CLI、Kimi Code CLI 中原样使用——区别只在**放哪个目录**和**怎么显式唤起**。先解压：

```bash
unzip agent-sdlc-workflow.skill -d /tmp/agent-sdlc-workflow
# 解压后应能看到 agent-sdlc-workflow/SKILL.md
```

### Kimi（网页 / 客户端）

技能管理入口导入 `agent-sdlc-workflow.skill` 文件即可，无需解压、无需配置。唤起方式：直接提 skill 名称，或让请求命中描述中的触发词。

### Claude Code

```bash
# 个人级（所有项目可用）
mkdir -p ~/.claude/skills
cp -r /tmp/agent-sdlc-workflow ~/.claude/skills/

# 项目级（随仓库共享给团队）
mkdir -p .claude/skills
cp -r /tmp/agent-sdlc-workflow .claude/skills/
```

- 显式唤起：`/agent-sdlc-workflow`
- 自动触发：请求命中描述时自动加载
- 支持 live-reload：编辑 SKILL.md 当前会话内生效

### Codex CLI

```bash
# 个人级
mkdir -p ~/.codex/skills
cp -r /tmp/agent-sdlc-workflow ~/.codex/skills/

# 项目级（随仓库共享）
mkdir -p .codex/skills
cp -r /tmp/agent-sdlc-workflow .codex/skills/
```

- 显式唤起：`$agent-sdlc-workflow`（或 `/skills` 选择器浏览）
- 复制后**重启 Codex** 以加载新 skill

### Kimi Code CLI

```bash
# 个人级（所有项目可用；~/.config/agents/skills/ 为官方推荐通用路径）
mkdir -p ~/.kimi/skills
cp -r /tmp/agent-sdlc-workflow ~/.kimi/skills/

# 项目级（随仓库共享给团队）
mkdir -p .kimi/skills
cp -r /tmp/agent-sdlc-workflow .kimi/skills/
```

- 显式唤起：`/skill:agent-sdlc-workflow`（可追加任务描述，如 `/skill:agent-sdlc-workflow 启动报销系统项目`）
- 发现顺序：**项目 > 用户 > 内置**；品牌目录（`.kimi/` > `.claude/` > `.codex/`）与通用目录（`.agents/skills/`）均会被扫描合并
- 安装后 `/reload` 或 `/new` 生效

### 跨工具兼容说明

| 工具 | 个人目录 | 项目目录 | 显式唤起 |
|------|----------|----------|----------|
| Kimi 客户端 | 技能管理导入 | — | 点名 / 自动触发 |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` | `/agent-sdlc-workflow` |
| Codex CLI | `~/.codex/skills/` | `.codex/skills/` | `$agent-sdlc-workflow` |
| Kimi Code CLI | `~/.kimi/skills/` | `.kimi/skills/` | `/skill:agent-sdlc-workflow` |
| 通用（多数兼容工具） | `~/.agents/skills/` | `.agents/skills/` | 视工具而定 |

团队共享建议：把 skill 提交到仓库的 `.agents/skills/`（通用路径，四个工具都会扫描），一次维护、处处可用。

## 使用

### 触发

显式点名（推荐）：

```
我要做一个 XX 系统，用 agent-sdlc-workflow 流程启动。
```

或自动触发：提及 spec-driven 开发、TDD、phase 划分、验收门控、agent 长程执行等关键词时自动命中。

### 一个项目的完整剧本

```
你说："用 agent-sdlc-workflow 启动"   →  agent 跑脚手架，铺好项目治理骨架
你说："先立宪章"                     →  协同确定原则/门槛/自主边界（阶段 0）
你说："挖需求"                       →  边界追问 + 五维建模 + EARS 验收标准 + 原型（阶段 1）
你说："搭闭环"                       →  逐项跑通质量回路 + 零人工干跑（阶段 2）
你说："切任务"                       →  产出任务卡 DAG，你签字（阶段 3，auto 前最后人工关卡）
你说："开始执行"                     →  长程 auto 执行，checkpoint 证据落盘（阶段 4）
你说："收尾复盘"                     →  一致性审计 + 资产回流（阶段 5）
```

### 变体用法

| 场景 | 说法 |
|------|------|
| 已有项目引入治理 | "用 agent-sdlc 补齐治理：立宪章 + 为核心模块补 spec 和门控" |
| 小改动 | "走 fast-track：简版 spec + plan + 实现" |
| 跨会话续作 | "读 CONSTITUTION.md、NOTES.md 和 plans/，从上次进度继续" |

### 脚手架生成的项目骨架

```
项目根/
├── CONSTITUTION.md          # 最高治理文档（不可变原则、质量门槛、自主边界）
├── AGENTS.md                # agent 操作手册（常用命令、目录地图、禁区）
├── NOTES.md                 # 跨会话唯一记忆通道
├── specs/                   # 需求规格（唯一事实源）
│   ├── TEMPLATE-spec.md
│   └── changes/             # 进行中的变更提案（delta）
├── plans/
│   ├── env-gates-checklist.md    # 环境闭环门控清单
│   ├── TEMPLATE-phase-plan.md    # phase 规划模板
│   ├── execution-protocol.md     # 执行监控与回流协议
│   ├── TEMPLATE-acceptance-retro.md
│   └── logs/                # checkpoint 证据落盘
├── docs/adr/                # 架构决策记录
└── tests/e2e/               # playwright 验收测试
```

## 目录结构（skill 本体）

```
agent-sdlc-workflow/
├── SKILL.md                     # 触发描述 + 六阶段规程（渐进披露：只放规程）
├── scripts/
│   └── init_project.py          # 项目脚手架（幂等，--force 覆盖）
└── assets/templates/            # 七个阶段模板，按需取用
    ├── overview.md
    ├── phase0-constitution.md
    ├── phase1-spec-modeling.md
    ├── phase2-env-gates.md
    ├── phase3-phase-planning.md
    ├── phase4-execution-protocol.md
    └── phase5-acceptance-retro.md
```

## 设计原则

1. **Spec 即源码**：需求是 agent 执行、验证、汇报的契约，不是参考文档
2. **Agent 自主性上限 = 反馈回路自动化程度**：先建闭环，再谈 auto
3. **Auto ≠ 无人值守**：长程执行 = checkpoint 证据 + 升级策略 + spec 回流
4. **决策落盘**：ADR、NOTES.md、checkpoint 是对抗 agent 跨会话失忆的唯一手段
5. **凡不能自动测量的门控，要么改成可测量，要么删除**——无法验证的规则比没有更糟

## 演进路线

当前为纯 skill（规程 + 模板）。以下信号出现时值得升级为 plugin：

- 门控需**强制拦截**（如提交前 hook 物理拦截，而非建议遵守）
- 回流台账 / ADR 需落外部系统（Linear、Notion、数据库）
- 需与 TDD、review 等其他 skill 打包为统一分发单元（如 Superpowers 形态）

## 边界说明

Skill 是**规程**而非**强制拦截**：agent 会按门控纪律执行并自证，但不像 CI hook 那样物理拦截违规。对绝大多数项目足够；强约束场景走 plugin 化路线。

---

*版本：v1.1 ｜ 兼容：Agent Skills 开放标准（Kimi / Claude Code / Codex CLI / Kimi Code CLI）*
