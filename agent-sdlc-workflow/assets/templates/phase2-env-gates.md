# 模板 2：环境、能力与完整反馈闭环

> 把宪章采用的工程纪律变成 Agent 能独立执行的命令、能力与证据。阶段允许创建最小骨架、测试或 tracer bullet。
> 保证等级与门控分类见 `references/evidence-assurance.md`；能力见 `references/capability-contract.md`。

## 能力协商（RULE-AUT-001）

填写本项目实测能力（Agent 先检查 Harness/tracker/CI/权限并给结论）：

```yaml
capabilities:
  evidence_capture: self | tool | independent | enforced
  atomic_claim: harness | tracker | file | none
  blocking_permission: harness | human | none
  independent_verify: available | unavailable
  isolated_workspace: available | unavailable
binding: references/bindings/<harness>.md   # 无对应 binding 用 generic.md 并降级
```

无对应 binding 时用 `references/bindings/generic.md`，并据 `RULE-AUT-001` 降级：无机器证据捕获不进 Project Auto；guarded 无阻断权限禁止 auto。

## 自动反馈命令

| 回路 | 命令 | 使用时机 | 通过标准 | 门控类型 | 保证等级上限 | 实测耗时 |
|---|---|---|---|---|---|---|
| 局部检查 | | 每轮连贯改动后 | | evidence | | |
| 受影响回归 | | 任务/批次完成 | | evidence | | |
| 相关集成/契约 | | Phase 退出 | | evidence | | |
| 关键路径 E2E | | Phase 或风险触发 | | evidence | | |
| 完整/发布级门控 | | Goal 完成；必要时提前 | | evidence/hard | | |
| build/package | | Phase/Goal 按需 | | evidence | | |
| 本地运行/部署 | | canary 与验收 | | evidence | | |

- 门控类型：hard（外部强制，A3）/ evidence（可执行并留证，A0–A2）/ judgment（人签字，J0/J1）。advisory 建议不是 gate。
- Web 项目优先验证 Playwright 能覆盖关键路径；非 Web 项目选择能从用户或系统边界证明行为的等价验收器。
- 验证节奏按 `RULE-VAL-001`：升级触发条件（共享契约/schema/权限/安全/依赖/全局配置/并发/迁移/基础设施变化，或局部失败暴露影响面扩大）与绿色证据复用见 `references/core-rules.md`。
- 证据复用须满足 `RULE-EVD-003`（revision/输入绑定、gate 未变、产物可访问）；命令本身只是复现配方，不是通过证据（`RULE-EVD-002`）。

## Goal 最低保证（RULE-GOAL-001）

| 场景 | 本项目要求 |
|---|---|
| project + standard + auto | 关键 evidence gate ≥ A1（evidence_capture ≥ tool） |
| guarded 关键行为 | ≥ A2，外加 blocking permission 与恢复 gate |
| hard gate | A3（引用外部强制结果） |
| 人工体验/业务验收 | J1 |

## 协作与决策闭环

- [ ] `AGENTS.md` 含常用命令、目录地图、项目特有禁区与受管规则区块
- [ ] 采用的测试先行方式可执行
- [ ] 独立 Review 的执行者和触发点明确
- [ ] ADR 模板可用，Agent 会先给推荐、备选和理由
- [ ] 失败输出足以让 Agent 自主定位问题
- [ ] guarded 操作有恢复或补偿路径（`RULE-REC-001`）

## 项目特有风险（按需）

- 安全/敏感数据：__
- API/数据/migration 兼容：__
- 性能或成本预算：__
- 部署、监控和恢复：__

## 闭环干跑

用最小工程 canary 执行（骨架/探针/极薄 tracer bullet，证明工具链闭环，不要求提前实现产品功能）：

```text
读取 spec/AC → 建立失败/基线证据 → 实现 → 局部验证
→ 受影响回归 → 独立 review → 本地运行/部署
→ 关键路径自证（记录保证等级与 captured_by）→ checkpoint
```

记录人工介入点；能通过合理默认值、文档或自动化消除的介入应在进入阶段 3 前消除。

## 退出门控

- [ ] 宪章采用的工程实践均有可执行办法，调整/N/A 有理由
- [ ] 能力协商已填写，binding 已选定；无 binding 时已按能力降级
- [ ] 局部、受影响、Phase 和最终门控命令均可执行并标注门控类型与保证等级上限，canary 选择了最小充分组合
- [ ] 最小工程 canary 完成完整闭环
- [ ] Agent 无需人类代跑命令或解释普通失败
- [ ] 若要 Auto-ready：`evidence_capture` 至少为 tool（A1）；guarded 已具备 blocking permission 与恢复 gate
