# 证据保证模型（Evidence Assurance）

> 支撑 `RULE-EVD-001 / RULE-EVD-002 / RULE-EVD-003 / RULE-HARD-001 / RULE-GOAL-001`。
> 核心命题：**证据可信度是多维保证，不由单个字段决定**，也不由「有没有证据路径」决定。

## 保证度取决于多维乘积

```text
作者路径 × revision/输入绑定 × 执行是否强制 × 验证范围完整性 × 结果防篡改性 × 新鲜度
```

任一项缺失都会拉低整体可信度；没有任何单字段能把低保证升为高保证。

## 四级保证（自动证据）

| 等级 | 作者与执行路径 | 可承担的语义 |
|---|---|---|
| `A0 self-reported` | Agent 散文或手工誊写 | 线索、过程摘要、fast-track 明示性报告 |
| `A1 tool-captured` | Harness 自动记录工具执行、revision、exit 与输出 | 普通 Project evidence gate |
| `A2 independently-replayed` | 新上下文、独立 verifier 或 CI 在同一 revision 重跑 | Project Goal、关键 AC、guarded 关键验证 |
| `A3 externally-enforced` | 受保护 CI、权限、分支保护或部署系统真实阻断 | hard gate |

## 人工判断

| 等级 | 含义 |
|---|---|
| `J1 human-approved` | 可定位到具体人、时间、对象与结论的批准 |
| `J0 pending/rejected` | 尚未批准或已否决 |

## 「机器作者」不自动等于高可信

机器捕获还必须检查，否则 A1 也可能虚假：

- 是否绑定当前 commit 或 dirty diff；
- gate 定义是否在运行前已确定；
- Agent 是否可修改捕获器或 CI 配置；
- 命令是否覆盖承诺的 AC；
- 结果是否仍新鲜；
- 是否存在选择性跳过；
- 原始输出是否可定位。

因此，**Harness 自动捕获本地命令通常是 A1，不是 A2/A3**。A2 需要独立上下文/verifier 在同一 revision 重跑；A3 需要外部系统真实阻断且 Agent 不能改写其配置。

## 紧凑证据记录

记录优先由 Harness 生成，Agent 只补充解释，不要求手工填写全部字段。

```yaml
gate_id: G-P1-E2E
assurance: A1            # A0/A1/A2/A3
requirement: AC-3
revision: abc123
dirty_diff_hash: null
source: "playwright test checkout"
result: passed
exit_code: 0
artifact_pointer: "run://..."
captured_by: "harness-id"
captured_at: "2026-07-23T18:21:12Z"
freshness: exact_revision   # exact_revision | impact_analyzed | stale
```

若某字段由 Agent 补写，必须标记：

```yaml
provenance: self-reported
```

**Agent 自填字段不能把 A0 升级为 A1。** 自填的 `assurance: A1` 在没有 `captured_by` 机器作者时按 A0 处理。

Markdown checkpoint 可展示精简列，但底层语义须覆盖：
`Gate | 保证等级 | Revision | 命令/来源 | Exit/结论 | 原始证据 | 验证者 | 新鲜度`。

## 本地无机器捕获时的底线

本地命令只是**复现配方**，不是通过证据。要证明「本次曾通过」，还需保存：revision 或 dirty diff hash、开始/结束时间、exit code、原始输出 transcript、关键产物标识、工具链/lockfile 标识。未满足者按 A0 报告。敏感日志不直接入仓：保存脱敏摘要与标识、使用忽略目录、记录外部安全存储指针、设置保留期限。

## 证据复用规则（RULE-EVD-003）

证据仅在以下全部成立时可复用：

1. 当前 revision 与证据 revision 相同；或中间变化经影响分析证明不涉及该 gate 的代码/配置/测试输入/环境；
2. gate 定义未变化；
3. 证据产物仍可访问。

不能仅凭「我认为没关系」复用；checkpoint 至少记录复用理由与新鲜度判定。

## Goal 最低保证（RULE-GOAL-001）

| 场景 | 最低要求 |
|---|---|
| fast + standard | A0 可用，但最终报告必须明确 `self-reported` |
| project + standard + auto | 关键 evidence gate 至少 A1 |
| guarded 关键行为 | A2，外加 blocking permission |
| hard gate | A3 |
| 人工体验/业务验收 | J1 |
