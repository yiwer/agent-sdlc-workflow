# 项目宪章

> Agent 根据项目先给出推荐与理由，人选择采用、调整或不适用。这里只保存跨阶段稳定、无法从代码可靠推断的纪律。
> 行为规则的唯一创作源是 skill 内 `references/core-rules.md`；本文件按 rule ID 引用，不复述全文。

## 工程基线建议

| 实践 | Agent 推荐与理由 | 决定：采用/调整/N/A |
|---|---|---|
| SDD/spec-first | 生产行为先有目标、非目标和编号 AC | |
| 测试先行 | 按风险选择 TDD、局部失败证据或等价方式 | |
| 独立 Review | 合入前至少一轮不同上下文的人或 Agent review | |
| ADR | 有真实取舍的决策记录推荐、备选和后果 | |
| 自动验收 | 关键路径使用 Playwright 或等价边界验收 | |
| 本地运行/部署 | 一条可重复命令完成启动或部署与自证 | |

已有等价能力时直接复用，不机械新增流程；不适用时简述理由。一次性实现细节不进入宪章或 ADR（`RULE-MIN-001`）。

## 能力协商结论（RULE-AUT-001，详见 references/capability-contract.md）

> Agent 检查现有 Harness/tracker/CI/权限后填写，不是让用户填表。Auto-ready 以此为据。

```yaml
capabilities:
  evidence_capture: self | tool | independent | enforced   # → A0/A1/A2/A3
  atomic_claim: harness | tracker | file | none
  blocking_permission: harness | human | none
  independent_verify: available | unavailable
  isolated_workspace: available | unavailable
```

- `evidence_capture = self`（A0）时本项目只能 copilot/Plan-ready，不进 Project Auto。
- guarded 操作在 `blocking_permission` 就位前禁止 auto（`RULE-GUARD-001`）。

## 版本控制策略（RULE-REC-001，详见 references/recovery-model.md）

| 策略 | 含义 | 本项目选择 |
|---|---|---|
| `record-only` | Agent 只记录 commit/diff，不自行 commit/tag | |
| `agent-commit` | 用户已授权按任务/Phase 提交 | |
| `branch-per-agent` | 多写入者各在 branch/worktree，集成者合并 | |

未授权时不默认创建 tag/branch/commit。

## 项目验证命令

| 用途 | 命令 | 通过标准 | 保证等级上限 |
|---|---|---|---|
| 局部/快速检查 | `__` | __ | __ |
| 受影响回归 | `__` | __ | __ |
| 完整/发布级门控 | `__` | __ | __ |
| 构建/打包 | `__` | __ | __ |
| 关键路径 E2E | `__` | __ | __ |
| 本地运行/部署 | `__` | __ | __ |

安全、性能、迁移和恢复属于真实风险时，再增加对应门控。本地命令的保证等级上限由捕获方式决定，见 `references/evidence-assurance.md`。

## 验证节奏

按 `RULE-VAL-001`（局部→受影响→Phase→Goal，共享面变化提前升级，输入未变复用绿色证据）执行；完整语义见 `references/core-rules.md`，各级命令见上表。

## Agent 自主与人工边界

- 自主范围与降级：`RULE-AUT-001`、`RULE-SCOPE-001`（影响区域不是权限白名单）。
- 改变目标/AC、增加外部权限或付费、生产/真实数据、破坏性难恢复操作需要人决定（`RULE-USER-001`）。
- 局部阻塞时继续其他安全任务；只有没有安全路径时才合并询问。

## 修订

宪章变化记录动机和日期，由人确认；不要把一次性例外永久写入。

---
版本：v2.0 ｜ 日期：__
