# 对 Codex《项目审计与详细修复方案》的反思与评分

- **状态**：独立评审稿（对评审的评审）
- **日期**：2026-07-23
- **评审视角**：Agent Harness 专家 + 软件工程专家
- **关键前提**：本 skill 将运行于顶级 LLM 与真实 harness 之上
- **评审对象**：`项目审计与详细修复方案.md`（Codex 审计稿）
- **评审谱系**：原项目 v1.5 → `修复方案-v2.0.md`（Claude 稿）→ Codex 审计稿 → 本文

---

## 〇、一句话裁决

**Codex 这份审计明显强于 `修复方案-v2.0.md`，它抓到了后者至少 6 个真实缺陷，应当作为 v2.0 的主设计基线。** 但它与 Claude 稿共享一个盲点——**只升级了"证据的记录"，没升级"证据的作者身份与 harness 强制绑定"**——并且把一套刻意精简的行为协议，往企业级发布工程的方向推得偏重。

评分先行：

| 对象 | 加权综合 | 性质 |
|---|---:|---|
| 原项目 v1.5 | **6.5** | 好方法论，尚非可信产品（Codex 此分认同） |
| Claude `修复方案-v2.0` | **6.7**（评审稿 8.5 / 实施 spec 6.2） | Codex 此分公允，接受 |
| **Codex 本方案** | **8.1** | 更成熟的工程设计，一处结构性未解 + 范围膨胀 |
| 理想"和解版" v2.0 | ~8.8–9.0 | 取 Codex 概念胜利 + 砍镀金 + 补 harness 作者层 |

---

## 一、Codex 对 Claude 稿的批评：认账部分（逐条，不辩解）

这些是真错，不是立场之争：

1. **运行时恢复盲点（最重的一条）。** Claude 稿主张"模板锚点指向 SKILL.md，skill 重载即恢复"——这预设了**每个会碰这个项目的会话都恰好装着同版本 skill**。但一个已初始化项目跨会话、跨机器、甚至跨工具（Codex/Claude/Kimi）恢复时，外部 skill 不是可靠的运行时依赖。**项目自己的运行规则必须在项目内。** Claude 稿的三层分离里"实例层"落盘了，"规则层"没落盘。Codex 的"受管区块 + source_version + rule_set_hash 渲染进项目 AGENTS.md"是对的正解。此为结构性疏漏。
2. **"命令 ≠ 通过证据"。** Claude 稿给 checkpoint 加的"可复现指针"把"一条可重跑命令"当通用底线——但命令只是**配方**，不是"本次曾通过"的证据。证据必须绑定 revision + freshness。Codex 的证据 envelope 在此严格更优。
3. **二元路由混淆四维。** "任一命中即 Project"+ "AC≥3 升级"把规模/会话/自主/风险/并发揉成一个布尔。Codex 指正：单点生产配置修复是 `fast+guarded`（不该被迫走完整 Project），多 Agent 文档迁移是 `project+standard`（低风险）。AC 计数触发是武断代理量。四维分解是更好的模型。
4. **完成状态过于二元（矫枉过正）。** Claude 稿"任何 pending 人工 gate 禁止报告 goal 完成"会让 agent 要么永远挂起、要么用模糊措辞偷绕。正解是生命周期状态机：可如实报告 `implementation_complete + automated_verified，human_acceptance_pending`，既不冒充"已验收"，也不抹掉已完成的工程事实。
5. **NOTES claim 不是锁。** "在 NOTES 写一行 claim"不原子、会双领。NOTES 是广播板。exclusive-create + lease + base_revision + write_scope 才是协议；原稿只是个手势。
6. **`--force` 不是迁移器（Claude 稿引入的数据丢失风险）。** Claude 稿在迁移表里推荐存量项目用 `--force` 换新模板——但 `--force` 是备份后**用空模板覆盖**，不合并用户定制，会**摧毁项目已有内容**。Codex 的 symlink/reparse-point 拒绝 + baseline-hash 差分升级器（upgrade_project.py）是正确补法。

另有两条**呈现层面**的 fair hit（认，但属表述瑕疵而非设计错误）：

- Claude 稿落地 DAG 声称 P1/P3/P4 并行，但它们同写 SKILL.md/phase3/phase4，多 agent 真并行会制造自身 skill 所警告的共享写冲突（逻辑独立 ≠ 写入独立）。
- `grep -rc` 当语义一致性验收确实脆弱（"绿色"11 次原始命中即为反例）。

Codex 对 Claude 稿"作为评审稿 8.5、不宜直接当 spec 6.2"的分判诚实准确——该方案本来就是设计方向，不是可领取任务的 spec。

---

## 二、Codex 真正超越 Claude 稿的概念胜利

公允地讲，这些是它的原创增量，应直接进入 v2.0：

- **四维正交模式 + 动态迁移表**（§7）：把判断**分解**成更窄的问题。
- **生命周期状态机**（§8.5）：消灭二元完成的谎言空间。
- **三类恢复分离**（源码/数据/外部副作用，§10）+ 版本控制策略先实例化（`record-only / agent-commit / branch-per-agent`）：堵住"git 回退冒充数据恢复"。
- **再锚定的锚点优先级**（§9.1：先锚当前批准 spec/delta，再锚原始意图）：修掉了 Claude 稿一个潜在 bug——只对照"用户最初一句话"会把**已批准的合法需求演化误判为漂移**。此点 Codex 更细。
- **E1–E12 故障注入评测矩阵 + 量化指标**（路由正确率 / stale-evidence 拒绝率 / 漂移发现时点 / 双领率 / 升级保真率）：验证行为协议的正确方法，远胜"dogfood 一个小项目"——且 Claude 稿的 dogfood 确实与 fast-track 精神自相矛盾。
- **受管区块 + lock + 内容契约测试**取代"每句话只出现一次"：这是对 Claude 稿三层分离的**补完**（补上缺失的"生成关系/版本关系"），不是推翻。

---

## 三、作为 Harness/SE 专家的实质反推

以下不是找平衡，而是该方案在"将运行于顶级 LLM + 真实 harness"前提下**真实存在的弱点**：

### 反推 1（最重）：升级了证据 schema，却没升级证据的**作者身份**——而自证恰恰活在作者身份里

Codex 的 12 字段 evidence envelope 很漂亮，**前提是它由机器（CI / harness hook / verify 工具）写入**。但谁来填 `dependency_lock_hash`、`artifact sha256`、`exit_code`，当一个会话在本地跑 `pytest` 时？——**还是那个 LLM agent，手工誊写。** 于是：字段越多，agent 需自填的自证面越大，恰恰重新制造了它要治的病。§8.3"本地无 CI 底线"仍要 agent 自己保存 revision/时间戳/transcript hash——仍是 agent-authored。

它加了 `verifier: {kind: ci}` 字段，但**没有设计让 envelope 由机器生成的那条 harness 集成路径**。严谨性因此一半是幻觉：一个会产生"幻觉式完成"的模型，会把 12 字段填得像模像样。**真正的杠杆不是更多字段，而是"谁写这条记录"**——设计那个自动捕获证据的 hook/CI，或接受一个更小但机器作者诚实的 envelope。Codex 在原则层知道这点（verifier、无记忆复核），但没让它承重。

> frontier-LLM 语境下更微妙：顶级模型确实能从真实工具输出正确填表（读 exit code、抓 commit），agent-authored envelope 比弱模型时代可靠；但它仍**不独立**。独立性必须来自作者路径，不是 schema。

### 反推 2：它在为"读 markdown、无 harness 能力的裸 agent"设计

`claim_task.py` 的 exclusive-create 租约协议，是**假设没有任何 harness 原语**时才会造的东西——这正是原始 skill 跨三工具可移植性所设的最低公约数陷阱。harness 专家会说：并发控制的正确原语是**issue tracker / harness 任务系统 / git worktree**，文件 claim 是个更差的自造调度器。Codex 自己也半承认（§16.4："已有 tracker 就复用，别造文件 claim"）——**却随后仍把整套文件 claim 协议写进主设计**。这是"详述一套自己劝你别用的机器"的味道。

正确做法：把协议定义在**能力接口**层（`atomic-claim` / `machine-evidence` / `blocking-permission`），让每个 harness 绑定自己的实现，文件方案只作 fallback。v2.0 的最高杠杆在**能力接口 + harness 绑定**，而两份方案都仍在设计"markdown 层"。这是共同缺失、本方案尤其该补的中心。

### 反推 3：范围膨胀，与这个 skill 的灵魂紧张

该 skill 最深处承诺是"最小落盘 / 反表演 / 选最轻充分 / 不为合规生产流程资产"。Codex 新增：lock.json、受管区块标记、upgrade_project.py（baseline-hash 差分迁移器）、claim_task.py（租约）、package_skill.py + verify_package.py（确定性构建）、VERSION、references/ 拆分、内容契约测试、evals/、7 态生命周期、4 维配置、12 字段 envelope、claims/ 目录……

一部分必要（lock/upgrade 修真实数据丢失洞；evidence-binding 修真实严谨洞）。但两处明显**优先级倒置/镀金**：

- **确定性打包（两次构建同 SHA-256）被列为 Phase 1 门控，先于"证明路由有效"。** 可复现构建是给"分发给不信任消费者的二进制"做供应链审计用的。一个作者打包分享的 markdown prompt-pack，这是镀金。不算错，但排在"行为协议到底管不管用"之前，是把 SE 本能（先建基建）错配到真实风险所在——再多的确定性打包也回答不了"LLM 照这套指令做会不会避免漂移/自证"。
- **通用迁移器 upgrade_project.py 偏重。** 修"`--force` 会毁用户定制"这个真问题，最轻解是"受管区块只存在于 AGENTS.md 那一小块规则快照，其余一律用户所有、永不触碰；升级只动受管区块"——拿到绝大部分安全性，机器量是通用迁移器的一小部分。Codex 落点已接近此（受管区块仅在 AGENTS.md），却仍把 upgrade_project.py 造成通用迁移器。轻度过度建设。

一份 ~1380 行的设计去修一个以"最小"为魂的 skill——**v2.0 成品必须比这份方案短得多**，否则即背叛。

### 反推 4（轻微，为 Claude 稿辩护一句）："naive DRY"的定性略重

Codex 头号指控是"把代码 DRY 过度套用到 LLM 指令"。方向对：LLM 消费的指令不是代码，**在行动点策略性重述规则能提升合规**，"每处只出现一次"是会伤 prompt 效果的代码美学。但略有稻草人——Claude 稿在每个现场保留的是"一行语义锚点"，非纯删除，并非 naive DRY。公允版本：正确单位是"canonical 创作源 + 有目的的投影 + 受管生成关系"，即 Codex 原则 B——**本质是 Claude 三层分离加上其漏掉的生成关系**。机制上 Codex 对（投影要受管生成），但"naive DRY"的定性偏重。

### 反推 5：四维模型没有逃出判断，只是分解了判断——而这恰是它在 frontier 模型上有效的原因

Codex 拒 Claude 路由清单为"伪精确"。但其四维 + 迁移表**同样是 LLM 从散文做的判断**，只是轴更多。`standard` vs `guarded` 的分界（"涉及生产/真实数据/迁移/权限/安全/付费/难恢复"）仍是散文。所以它不是消除判断，是**把整体判断拆成多个更窄判断**。关键洞见：**顶级模型做分解判断（"这碰生产数据吗？"）远比做整体判断（"这是 Project 吗？"）可靠。** 故 Codex 方向对、且在 frontier 语境下更对——只是不该宣称逃出了"伪精确"，它做的是更优的判断分解。

---

## 四、对 Codex 方案的分维度评分

| 维度 | 分 | 评语 |
|---|---:|---|
| 诊断准确性 | 9.0 | 对项目与 Claude 稿根因命中率高，抓到 6 个真错 |
| 概念模型（四维/生命周期/三门控/三恢复） | 9.2 | 全篇最强，真正的版本跃迁内核 |
| 证据与状态严谨度 | 8.0 | schema 一流；authorship 缺口使其只解决一半 |
| **harness 契合（frontier-LLM 语境）** | 6.5 | 为最低公约数裸 agent 设计，未定义能力接口/harness 绑定 |
| 轻量性 / 与 skill 灵魂一致 | 6.0 | 必要机器与镀金并存，确定性打包优先级倒置 |
| 安全与迁移 | 9.0 | 对 Claude 稿最实质的实践改进（symlink/--force/upgrade/三恢复） |
| 落地计划与并行分区 | 8.5 | 写入分区 + 单一 Integrator 修掉了 DAG bug |
| 实证/评测设计 | 9.0 | E1–E12 + 指标矩阵是正确方法论 |
| 范围纪律 | 6.5 | 捆扎可分离关注点，详述自劝勿用的机器 |
| **加权综合** | **8.1** | 更成熟的设计，一处结构性未解 + 轻度过度建设 |

---

## 五、真正的 v2.0 应该长什么样（和解方案）

取两者之长、砍镀金、补共同盲点：

1. **概念内核全取 Codex**：四维模式、生命周期状态机、三门控分类、三类恢复、锚点优先级再锚定、受管区块 + 项目内规则快照（修恢复盲点）、E1–E12 评测。
2. **砍镀金**：确定性打包降级为"发布前可选门控"而非 Phase 1 前置；通用迁移器收窄为"只升级 AGENTS.md 受管区块 + 生成冲突报告"；文件 claim 明确标注为"无 tracker 时的 fallback"，主路径指向 harness/issue 系统。
3. **补两者共同缺的承重墙——证据作者身份与能力接口**：
   - 定义三个 **harness 能力接口**：`evidence-capture`（机器写 envelope）、`atomic-claim`、`blocking-permission`；各给 harness 绑定示例（Claude Code 的 PreToolUse/PostToolUse/Stop hook、`verify`/`run`/`code-review` skill 作为无记忆复核的具体化身、权限 allowlist）+ 文件/人工 fallback。
   - 规则：**evidence gate 的可信度 = 其作者路径的可信度**。能机器作者的字段才计入硬证据；agent 自填字段一律标记 `self-reported`，不得单独作为 Goal 门控。这一条直接把"自证"从修辞问题变成可判定的结构问题。
4. **守住灵魂**：fast-track 仍零落盘；所有新增机器只在 Project Mode 且对应维度触发时启用；v2.0 成品文档长度必须是这份方案的一个零头。

---

## 六、收束

Codex 的审计该赢的地方赢了：它在**记录、状态、并发、迁移、实证**五个工程语义上把 Claude 稿补成了 spec，其中运行时恢复和 `--force` 两条是 Claude 稿真错，认。它该被反推的地方也清楚：**证据的严谨停在 schema 层，没到作者层；协议设计停在 markdown 层，没到 harness 能力层**——而这两层恰恰是"跑在顶级 LLM/harness 上"这个前提下回报最高的地方。

一句话：**把 Codex 的概念内核当骨架，把确定性打包和通用迁移器的镀金削掉，再浇上"机器作者证据 + harness 能力接口"这堵承重墙——这才是配得上顶级模型运行的 v2.0。** 在那堵墙立起来之前，Codex 的方案和 Claude 稿一样，都还停在"更精致的自证"，只是它精致得多。
