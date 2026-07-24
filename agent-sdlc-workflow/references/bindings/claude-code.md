# Binding：claude-code（Claude Code 能力绑定）

- 适用：Claude Code（CLI），含 hooks / 权限系统 / 子 Agent / worktree / skills
- 状态：设计完成并已在本仓库落地（`.claude/settings.json` + `.claude/hooks/`）；真实 dogfood 数据为 v2.0 稳定版发布门控
- 验证日期：2026-07-23（设计 + 本仓库接入）

> 诚实声明：以下映射基于 Claude Code 公开能力设计，**尚未经真实项目 dogfood 验证**。在 dogfood 通过前，按本 binding 运行的项目应自降一级保证并标注。

## 本仓库已落地配置（dogfood 进行中）

本仓库已将该 binding 实际接入：

- `.claude/settings.json`
  - `permissions.deny`：`git reset --hard`、`git push --force`/`-f`、`git clean -fd(x)`、绝对路径/家目录 `rm -rf` 等破坏性操作（blocking-permission）；
  - `permissions.ask`：`--force-with-lease`、`branch -D`、`checkout -- .`、`restore .`、`rebase` 等需确认操作；
  - `hooks.PostToolUse`（匹配 Bash，`async` 非阻断）：调用 `.claude/hooks/capture_evidence.py`。
- `.claude/hooks/capture_evidence.py`：仅对验证类命令（test/build/lint/typecheck/e2e）将 `{命令, revision, dirty_diff_hash, exit_code, result, 输出摘要, 时间, session}` 追加写入 `plans/logs/evidence.jsonl`，标 `assurance: A1 / provenance: tool-captured / captured_by: claude-code:PostToolUse`。恒退出 0，不阻断会话。

约束：本地由 Agent 触发的命令至多 A1，不是 A2/A3；A2 需 `code-review`/子 Agent/CI 在同一 revision 复跑，A3 需外部受保护系统真实阻断。证据日志为本地会话数据，已在 `.gitignore` 忽略；人工 checkpoint（`.md`）照常提交。项目可在 `deny` 中追加自身的 deploy/migrate/生产命令前缀（权限规则为前缀匹配）。

> 注：新建的 `.claude/` 需 `/hooks` 重载或重启后才被监视；重载后任意测试/构建命令即写入证据日志。

## 能力映射

| 能力 | Claude Code 原语 | 可达等级 | 诚实限制 |
|---|---|---|---|
| `evidence-capture` | Bash 工具捕获 stdout/stderr/exit code；`PostToolUse` hook 持久化记录 | **A1** | Agent 自行调用 Bash 属自触发，可误读/挑选，故至多 A1，不是 A2/A3 |
| `independent-verify` | `code-review` skill / 子 Agent（新上下文）/ 外部 CI | **A2** | 需在同一 revision 由新上下文重跑；子 Agent 与主 Agent 同模型，共享盲点，安全 gate 仍应交给 CI 或人 |
| `blocking-permission` | 权限系统（settings 的 allow/deny）、`PreToolUse` hook 阻断、sandbox 模式 | 本地 **harness**；生产/部署仍 **human/CI** | 能阻断本地危险命令；生产、真实数据、发布审批仍由人或外部系统把关 |
| `atomic-claim` | 子 Agent 由单一主会话协调（天然单调度）；跨会话多写入者用 issue tracker | `harness`（会话内）/ `tracker`（跨会话） | Claude Code 无跨会话原子文件锁；多会话并发优先用 tracker，文件 claim 仅 fallback |
| `isolated-workspace` | `git worktree`（EnterWorktree）/ 子 Agent `isolation: worktree` | available | 用于并行写入者隔离 |

## evidence-capture 落地建议

- 局部/受影响/Phase/Goal 各级命令通过 Bash 执行，读取真实 exit code 与输出，不在散文中臆断结果。
- 用 `PostToolUse` hook（匹配测试/构建命令）把 `{命令, exit_code, revision, 输出摘要, 时间}` 追加写入项目内证据日志（如 `plans/logs/evidence.jsonl`），形成 A1 记录；hook 配置由用户拥有，Agent 不改写。
- revision 用 `git rev-parse HEAD` 与 `git status --porcelain` 的 diff 标识获取，绑定到记录。
- Goal 关键 gate 用 `code-review` skill 或子 Agent 在同一 revision 复跑，升级为 A2，并在 checkpoint 记 `captured_by` 与复跑来源。
- hard gate（如部署审批、受保护 CI）引用其外部结果（A3），不由本地 Bash 冒充。

## blocking-permission 落地建议

- 在项目 `.claude/settings.json` 配置 deny 规则覆盖：生产环境命令、真实数据写入、`git reset --hard`、`push --force`、迁移/发布脚本等；guarded 操作落入 deny 或由 `PreToolUse` hook 拦截。
- 未在权限系统中阻断的 guarded 操作 → 视为 `blocking-permission: human`，禁止 auto，合并询问用户。

## atomic-claim / 并发落地建议

- 单会话内多子 Agent：由主会话作为单一集成者派发，天然无跨会话双领；合并后由主会话跑跨 Agent 回归。
- 多会话/多人：优先 issue tracker 的任务领取；无 tracker 时回退 `generic.md` 的文件 claim。
- 并行写入者用 worktree 隔离，集成者统一合并。

## 能力协商示例（Claude Code + CI）

```yaml
capabilities:
  evidence_capture: tool        # Bash + PostToolUse hook → A1
  atomic_claim: harness         # 会话内单调度；跨会话用 tracker
  blocking_permission: harness  # 本地 deny/hook；生产 human
  independent_verify: available # code-review skill / 子 Agent / CI → A2
  isolated_workspace: available # worktree
```

该配置支持 `project + auto + standard`；guarded Auto 仍需确认生产/数据操作的阻断与恢复路径已就位。
