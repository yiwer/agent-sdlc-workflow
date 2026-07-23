# 核心规则（Canonical Authoring Source）

> 本文件是 Agent SDLC 全部行为规则的**唯一创作源**。`SKILL.md`、阶段模板、项目内 `AGENTS.md` 受管区块都是它的受控投影。
> 规则只在此处定义一次；投影只保留稳定 **rule ID** 与该行动点所需的短摘要。

## Rule ID 约定

- 形如 `RULE-<域>-<编号>`，一经发布不复用、不改语义；语义变化换新 ID。
- 投影现场（模板/受管区块）写法：`RULE-VAL-001：按局部→受影响→Phase→Goal 扩大验证`。
- 内容契约测试保证：投影引用的每个 ID 都存在于本文件；受管子集非空且可由 `init_project.py` 渲染。

---

## 运行时核心子集（受管投影）

> 下列条目由 `init_project.py` 渲染进项目 `AGENTS.md` 的受管区块，供跨会话/跨工具恢复。
> 这是**投影**，不是第二份规则：完整语义见下方目录，二者以 rule ID 对齐。

- RULE-AUT-001：验证质量决定自主权；能力或证据不足时降低自主或并发，不用散文伪装能力已存在。
- RULE-VAL-001：按局部→受影响→Phase→Goal 逐级扩大验证；输入未变可复用最近绿色证据。
- RULE-EVD-001：证据分 A0 self-reported / A1 tool-captured / A2 independently-replayed / A3 externally-enforced；人工分 J1 approved / J0 pending-or-rejected。
- RULE-USER-001：只有产品语义必变、新外部授权/付费、生产或真实数据、破坏性难恢复且无其他安全任务可继续时，才合并询问。
- RULE-SCOPE-001：影响区域用于估算与写冲突协调，不是权限白名单；漏列文件直接改，差异由 git 提供。
- RULE-STATE-001：生命周期如实报告；自动 gate 过而人工 pending 报 automated_verified，不报 accepted。
- RULE-FAST-001：fast-track 零落盘；风险升高只切 guarded 维度，不膨胀为完整 Project。

---

## 完整规则目录

### 治理与自主

- **RULE-AUT-001 验证质量决定自主权**：自主程度不由提示词长度决定，而由可用能力与证据保证等级决定。能力或证据不足时降低自主/并发程度，不用更多散文伪装能力已经存在。投影：SKILL.md、受管区块。
- **RULE-MODE-001 四维正交判定**：交付规模（fast/project）、自主程度（copilot/auto）、风险（standard/guarded）、协作（single/multi）分别判定。AC 数量、用户要求 auto、使用多 Agent、单点高风险操作**均不单独决定** Project；它们分别影响自主、并发、风险维度。四维模型仍含 LLM 判断，其价值是把整体判断拆成更窄、更可验证的问题。投影：SKILL.md、phase3。
- **RULE-FAST-001 fast-track 零落盘**：单一可验证增量、单会话可完成、持久计划不产生实际价值时走 fast-track。不强制初始化、不创建规则快照、不创建 NOTES/spec/plan/checkpoint；最终对话摘要即可作为 A0 报告。风险升高只切换 guarded 维度，不自动膨胀为完整 Project。投影：SKILL.md、受管区块。
- **RULE-USER-001 用户介入边界**：仅当「目标/非目标/AC 必须改变」「需新外部权限/付费服务/生产或真实数据」「操作破坏性、难恢复或超出已授权工作区」且没有其他安全任务可继续时，才合并询问。普通失败、漏列文件、等价重构、实现选择、首次诊断由 Agent 自判。投影：SKILL.md、phase4、受管区块。
- **RULE-SCOPE-001 影响区域语义**：任务卡「影响区域」仅用于估算工作量与协调多 Agent 写冲突，不是权限白名单。发现漏列文件直接修改，在 checkpoint 概括重要影响；逐文件差异由 git 提供。投影：phase3、phase4、受管区块。
- **RULE-MIN-001 最小落盘与反表演**：spec 记意图、ADR 记关键取舍、NOTES 记进度、checkpoint 记结果与证据。不为证明遵守流程而生产流程资产；无新知识时记「无变更」；N/A 写理由而非静默跳过。投影：SKILL.md、phase1、phase5。
- **RULE-SESSION-001 运行时真相源**：已初始化项目不能依赖当前会话记忆、每台机器恰好安装同版本 skill、或新 Agent 恰好重新触发 skill。核心运行规则必须存在于项目内 `AGENTS.md` 受管区块，或由 `AGENTS.md` 明确引用的项目内文件。投影：SKILL.md、init_project.py。

### 验证节奏

- **RULE-VAL-001 分层验证节奏**：连贯改动后跑最短局部检查，不每次编辑后全量回测；任务/批次结束跑受影响回归；Phase 退出跑相关集成、共享契约与关键路径 E2E；Goal 完成确保最后一次代码变更后有完整/发布级绿色证据，上层已等同或覆盖则复用。修改共享契约、schema、权限、安全、依赖、全局配置、并发、迁移或基础设施，或局部失败显示影响面扩大时，提前升级验证范围。代码与验证输入未变化时可复用最近绿色证据；相同失败不再提供新信息时先换假设。投影：SKILL.md、phase0、phase2、phase4、受管区块。

### 证据与门控

- **RULE-EVD-001 证据保证分级**：`A0 self-reported`（Agent 散文/手工誊写）/ `A1 tool-captured`（Harness 自动记录工具执行、revision、exit 与输出）/ `A2 independently-replayed`（新上下文/独立 verifier/CI 在同一 revision 重跑）/ `A3 externally-enforced`（受保护 CI、权限、分支保护或部署系统真实阻断）。人工判断另记 `J1 human-approved` / `J0 pending-or-rejected`。详见 `evidence-assurance.md`。投影：phase2、checkpoint、受管区块。
- **RULE-EVD-002 自填不升级**：Agent 补写字段必须标 `provenance: self-reported`；A0 不得冒充 A1。机器捕获本地命令通常是 A1，不是 A2/A3。投影：checkpoint、phase2、受管区块。
- **RULE-EVD-003 证据绑定与新鲜度**：evidence 必须绑定 commit 或 dirty diff 与验证输入；revision 或输入已变的 stale 结果降级或拒绝；复用须证明中间变化不涉及该 gate 的代码/配置/测试输入/环境，且 gate 定义未变、产物仍可访问。投影：checkpoint、phase4、phase5。
- **RULE-HARD-001 硬门控专属性**：hard gate 只能由 A3 外部强制结果满足。Skill 文本不得把权限隔离、CI 阻断、分支保护、部署审批伪装成已强制；只能引用其结果。投影：SKILL.md、phase2、phase5。
- **RULE-GOAL-001 Goal 最低保证**：fast+standard 可 A0，但最终报告须明示 self-reported；project+standard+auto 关键 evidence gate 至少 A1；guarded 关键行为至少 A2 外加 blocking permission；hard gate 须 A3；人工体验/业务验收须 J1。投影：phase2、phase5。

### 生命周期状态

- **RULE-STATE-001 生命周期诚实**：状态机 `planned → implementation_complete → automated_verified → human_acceptance_pending → accepted → released → closed`，辅助 `auto_paused / rejected / deferred`。自动 gate 通过而人工 gate pending 时可报 `automated_verified`，不得报 `accepted`；不得因人工 gate pending 隐瞒实现与自动验证已完成；`deferred` 必须来自已批准的 spec delta，不能偷绕 AC；熔断进入 `auto_paused`，不抹掉仍有效的已完成增量。投影：phase4、phase5、受管区块。

### 再锚定与熔断

- **RULE-ANCHOR-001 再锚定**：对照顺序为「当前批准 spec → 已批准 spec delta → 当前 goal/AC/非目标 → 用户原始意图」；已批准的合法需求演化不误判为漂移。触发点：Phase 边界、上下文压缩、新会话恢复、Agent 交接、spec delta 合并、影响面显著扩大、最终验收前。发现疑似漂移先做影响分析与可逆修正，须改变产品语义时才提交 spec delta 或询问用户；不变成新的高频打扰源。投影：phase4、phase5。
- **RULE-BREAK-001 熔断**：出现「同一失败再次发生且无新假设/新证据」「多个独立假设被证伪达已配置探索上限」「已实例化预算的消耗与有效增量显著失衡」「须撤销多个已验证任务才能继续」「再锚定连续发现同类目标偏差」「进入未获授权的 guarded 范围」之一时，进入 `auto_paused`，保留仍有效的增量并给出恢复入口。平台无法提供预算时不启用「预算过半」一类伪指标。投影：phase4。

### 恢复

- **RULE-REC-001 三类恢复分离**：源码恢复（文件/commit/配置）、数据恢复（schema/migration/数据写入）、外部副作用恢复（云资源/发布/API/消息/流量）分别建模与报告。不默认创建 tag/branch/commit；不默认 destructive reset；不覆盖用户或其他 Agent 的未提交成果；Git 恢复不得冒充数据或生产恢复；guarded Auto-ready 前必须有对应恢复或补偿路径。详见 `recovery-model.md`。投影：phase4、phase5。

### 并发与权限

- **RULE-CLAIM-001 并发控制**：多 Agent 主路径为「Harness 任务系统/issue tracker 原子 claim → branch/worktree/沙箱隔离 → 单一集成者 → 合并后跨 Agent 回归」。无 `atomic-claim` 能力时：优先单写入者，或由协调者串行派发，保持 copilot，不宣称 multi-agent Auto-ready。文件型 claim 只是独立 fallback binding，不默认创建、不在核心模板详述；NOTES 是广播板，不承担锁职责。详见 `capability-contract.md`。投影：phase4。
- **RULE-GUARD-001 guarded 权限**：guarded 操作在无 `blocking-permission` 能力时禁止 auto，不用文本规则代替真实权限阻断。投影：phase2、phase4。
