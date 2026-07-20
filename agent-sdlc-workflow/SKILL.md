---
name: agent-sdlc-workflow
description: Agent 时代的软件工程六阶段工作流（宪章立法 → 需求与五维建模 → 环境闭环 → Phase 任务规划 → 长程执行+回流 → 验收沉淀），前四阶段人机协同、执行阶段 agent 自治。当用户启动新软件项目、要求以 SDD/spec-driven/TDD 方式组织开发、需要划分 phase 与任务清单、建立验收门控/ADR/退出门控机制、规划 copilot 与 auto 的人机分工、让 agent 长程执行项目、或为 AI 编程搭建工程闭环时触发。Use for spec-driven development, long-running agent execution, task decomposition with exit gates, agent coding governance, and human-agent collaboration workflows.
---

# Agent SDLC 六阶段工作流

## 核心原则

1. **Spec 即源码**：需求是 agent 执行、验证、汇报的契约，不是参考文档。验收标准必须可执行（EARS 句式，逐条编号）。
2. **Agent 自主性上限 = 反馈回路自动化程度**：先建闭环，再谈 auto。
3. **Auto ≠ 无人值守**：长程执行 = 低干预、高可见（checkpoint 证据 + 升级策略 + spec 回流）。
4. **决策落盘**：ADR、NOTES.md、checkpoint 是对抗 agent 跨会话失忆的唯一手段——留在对话里等于丢失。

## 六阶段总览

| 阶段 | 名称 | 模式 | 产出物 | 模板（assets/templates/） |
|------|------|------|--------|---------------------------|
| 0 | 宪章 Constitution | copilot | 不可变原则、质量门槛、自主边界 | phase0-constitution.md |
| 1 | 需求与五维建模 | copilot | 规格、五维模型（对象/行为/事件/关系/规则）、EARS 验收标准、原型验证 | phase1-spec-modeling.md |
| 2 | 环境与闭环 | copilot | 自动化质量回路、agent 基础设施、部署流水线 | phase2-env-gates.md |
| 3 | 规划与切分 | copilot | phase DAG、任务卡、上下文预算、退出门控 | phase3-phase-planning.md |
| 4 | 长程执行 | auto | 代码、checkpoint 证据、偏差与回流记录 | phase4-execution-protocol.md |
| 5 | 验收与沉淀 | copilot | 一致性审计、复盘、宪章/模板更新（飞轮） | phase5-acceptance-retro.md |

## 启动新项目

运行脚手架脚本，生成目录结构并铺入全部模板：

```bash
python3 scripts/init_project.py <项目根目录>
```

生成：`CONSTITUTION.md`、`AGENTS.md`、`NOTES.md`、`specs/`（含变更目录）、`docs/adr/`、`plans/`（含日志目录）、`tests/e2e/` 及各阶段模板。已存在文件默认跳过，`--force` 覆盖。

## 逐阶段操作要点

### 阶段 0：立法先行
- 与人协同填写 CONSTITUTION.md；只写不可变项（原则、定量门槛、自主边界、升级条件）。
- 凡不能由命令自动测量的质量门槛，要么改成可测量，要么删除——无法验证的规则比没有更糟。
- 宪章跨项目复用，只经阶段 5 复盘修订。

### 阶段 1：需求必须可执行
- 用五维建模（对象/行为/事件/关系/规则）结构化需求；规则即不变量，是测试与 DB 约束的直接来源。
- 每条验收标准用 EARS 句式（WHEN \<条件\>，THE SYSTEM SHALL \<行为\>）并编号（AC-x），保证阶段 4 门控可自动化。
- 显式写**非目标清单**与**前置假设清单**——前者防 scope creep，后者是执行期偏差的预警雷达。
- 原型与建模迭代交织：低成本原型是检验建模错误最快的探针，暴露的问题回填模型。

### 阶段 2：闭环即自主权
- 目标不是装工具，而是让 agent 无需人类即可完成 编码→验证→部署→自证 闭环。
- 逐项实测模板清单并记录耗时；本地完整验证总耗时设硬预算，超预算先优化回路再进阶段 3。
- 用最小真实任务做**干跑验证**：全程零人工介入才可放行。

### 阶段 3：切分决定兑现率
- 任务卡粒度 = 一次专注上下文可容纳量（经验：涉及文件 ≤ 5–8 个）；超预算必须再拆。
- 拆不动的高耦合设计任务显式标记为 copilot 任务，不放行到 auto 阶段。
- 任务构成 DAG；可并行任务的文件白名单两两无交集；声明串行区（DB migration、lock 文件等单点修改）。
- 每条 AC 至少被一张任务卡引用，每张任务卡至少引用一条 AC（双向可追溯）。
- 任务清单经人签字——这是 auto 前最后一个人工关卡。

### 阶段 4：低干预、高可见
- 任务边界即上下文边界：新任务冷启动，执行"开机三读"（宪章 → 任务卡 → NOTES.md）。
- 每任务产出 checkpoint（结果/门控证据/偏差/耗时），落盘 plans/logs/。
- 升级条件触发时（spec 冲突、门控连跪 3 次、假设证伪、越权、AC 本身有误）必须停止问人，禁止"灵活发挥"。
- spec 回流唯一合法路径：停 → 记 → 改 spec → 人审 → 续。登记回流台账。
- 上下文逼近上限时做任务内压缩；重要发现立即写 NOTES.md。

### 阶段 5：沉淀飞轮
- 一致性审计：spec ↔ 代码 ↔ ADR 三方对齐，漂移清零。
- 过程数字即前期质量信号：升级次数→阶段 1 质量；回流次数→建模遗漏；门控打回率→切分/环境问题。
- 资产回流：修订宪章、补充 AGENTS.md、校准切分基线。没有沉淀的项目只交付了代码，没交付能力。

## Fast-track 分流

小变更走快轨：`宪章 → 简版 spec → plan → implement`，但仍必须留 spec 记录。无 spec 的捷径是 spec 驱动纪律崩塌的起点。

## 质量判据

- 阶段 1、2 决定质量上限，阶段 3 决定上限在执行中的兑现率。
- 人的工作已上移到：定义问题、定义验证、定义边界。凡重复两次以上的人工纠正，转化为文档/门控/宪章条款，而非再次口头纠正。
