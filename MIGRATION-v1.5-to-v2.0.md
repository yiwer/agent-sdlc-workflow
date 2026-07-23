# 迁移指南：v1.5 → v2.0

- 状态：人工迁移指南（v2.0 不提供通用自动迁移器）
- 日期：2026-07-23

## 结论先行

- **v1.5 项目可以继续使用**，不会被破坏，也不需要立即迁移。
- v2.0 **不自动改写**历史 spec、plan、checkpoint。
- 任何用户定制文件一律视为**用户所有**，迁移不覆盖。
- **不推荐用 `--force` 作为迁移方式**：`--force` 是「备份后覆盖」工具，会用空模板覆盖文件、丢失定制内容；它**不是迁移器**。

## 语义变化（先读懂再动手）

| 主题 | v1.5 | v2.0 |
|---|---|---|
| 模式 | 二元 fast-track / Project | 用户界面保留二元；内部四维正交（规模/自主/风险/并发），AC 数量等不硬路由 |
| 证据 | 「有证据路径」 | 保证等级 A0 self-reported / A1 tool-captured / A2 independently-replayed / A3 externally-enforced；人工 J0/J1 |
| 门控 | 退出门控（自报） | 三分：hard（A3 外部强制）/ evidence（A0–A2）/ judgment（J0/J1） |
| 完成 | 未完成 → goal 完成 | 生命周期状态机：planned → implementation_complete → automated_verified → human_acceptance_pending → accepted → released → closed |
| 自治前提 | 计划确认 | 能力契约：Auto-ready 要求 evidence_capture ≥ tool（A1）；guarded 需 blocking-permission；multi 需 atomic-claim |
| 长程防御 | 最终复盘 | 在途再锚定（先锚当前批准 spec）+ 熔断 auto_paused + 三类恢复分离 |
| 运行时规则 | 依赖 skill 文本 | 项目内 AGENTS.md 受管区块（ruleset/hash，从 references/core-rules.md 投影） |

## 建议的人工迁移步骤

1. **备份**项目（版本控制或副本）。
2. 阅读 v2.0 的 `references/core-rules.md`、`evidence-assurance.md`、`capability-contract.md`、`recovery-model.md`，理解新语义。
3. **可选**：在项目 `AGENTS.md` 加入受管区块——从 `references/core-rules.md` 的「运行时核心子集」复制对应 rule 行，包裹在
   `<!-- agent-sdlc:managed:start ruleset=2.0 hash=… -->` / `<!-- agent-sdlc:managed:end -->` 之间。若你的 AGENTS.md 已存在，初始化器不会覆盖它，只会生成 `AGENTS.agent-sdlc.md` 供你合并。
4. **新任务起**采用 v2 checkpoint schema（保证等级、Revision、captured_by、新鲜度）与生命周期状态报告；旧 checkpoint 保持原样。
5. 旧 spec/plan/ADR **保持不动**；如需调整，走正常的 spec delta / ADR superseded 流程。
6. 在宪章中补一次「能力协商结论」与「版本控制策略」，作为后续 Auto-ready 的依据。

## v2.0 之后的规则同步

v2.0 及以后只同步 `AGENTS.md` 的**受管区块**：

- 当前区块 hash 等于旧 baseline → 可更新；
- 当前 hash 不同（用户已改）→ 生成冲突报告/新候选区块，**不覆盖**用户修改；
- 受管区块以外的内容永远是用户所有；
- 不扩展为通用模板迁移器。

## 关于 `--force`（再次强调）

`--force` 会先备份再用模板覆盖 skill 拥有的文件。它适合「我确认要重置这些模板」的场景，**不适合迁移**：它不合并定制内容。迁移请使用上面的人工步骤。
