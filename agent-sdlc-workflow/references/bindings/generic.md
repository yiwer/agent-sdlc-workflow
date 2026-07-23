# Binding：generic（无 Harness 原语时的降级 fallback）

- 适用：任何不提供 hooks / 任务系统 / 权限阻断 / 隔离工作区的 Agent 环境
- 状态：fallback 基线；v2.0-rc.1 起可用
- 验证日期：2026-07-23

本 binding 只描述**能力降级后的行为**，不假装具备机器证据或原子调度。

## 能力映射

| 能力 | generic 下的取值 | 后果 |
|---|---|---|
| `evidence-capture` | `self`（A0） | 只能 fast-track；Project 保持 copilot/Plan-ready，不进 Auto |
| `atomic-claim` | `file` 或 `none` | 优先 `none`→单写入者/串行；文件 claim 仅在确需多写入者时作为 fallback |
| `blocking-permission` | `human` | guarded 操作一律人工审批，禁止 auto |
| `independent-verify` | `unavailable` | 关键 Goal 标注「未独立复核」，不冒充 A2 |
| `isolated-workspace` | `unavailable` | 并行写入者串行化 |

## A0 证据底线

无机器捕获时，每条 evidence 仍尽量手工记录：revision、命令、exit、时间、原始输出位置，并显式标 `assurance: A0` 与 `provenance: self-reported`。最终报告必须写明「self-reported，未机器捕获」。

## 文件型 claim（仅 fallback，不默认创建）

仅在确有多个写入者、且无 tracker/调度器可用时使用；否则单写入者。若使用：

- 路径：`plans/claims/<task-id>.json`（目录按需创建，不随 init 默认生成）；
- 领取必须 **exclusive-create**：文件已存在即领取失败，不允许后写覆盖先领；
- 字段至少：`task_id / owner / base_revision / write_scope / shared_write_lane / claimed_at / lease_expires_at / status`；
- 租约到期后不能由普通 Agent 直接覆盖，须由协调者记录回收原因后释放；
- 恢复任务必须读取原 owner 的 checkpoint 与 diff；
- 共享写点（migration / 公共 schema / lockfile / 全局配置 / 发布清单）默认进入单 owner 串行 lane。

**NOTES.md 是广播板，永远不承担锁职责。**

## 升级路径

一旦所在 Harness 提供原生能力，应切换到对应 harness binding（如 `claude-code.md`），并相应提升可承担的保证等级与并发程度。
