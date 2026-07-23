# 恢复模型（Recovery Model）

> 支撑 `RULE-REC-001 / RULE-GUARD-001`。
> 核心命题：**源码、数据、外部副作用三类恢复必须分离建模**；Git 回退不得冒充数据或生产恢复；回退先保护用户成果。

## 三类恢复

| 类别 | 对象 | 机制 |
|---|---|---|
| 源码恢复 | 文件、commit、配置 | revert、显式文件恢复、受控分支 |
| 数据恢复 | schema、数据写入、migration | down migration、备份恢复、补偿脚本 |
| 外部副作用恢复 | 云资源、发布、API 调用、消息、流量 | provider rollback、补偿事务、人工处置 |

不能用「回到 Git 绿色点」概括后三者。报告恢复时必须分别说明每一类的状态与未覆盖项。

## 版本控制策略（先实例化）

Project Mode 初始化时选择并记录：

| 策略 | 含义 |
|---|---|
| `record-only` | Agent 只记录当前 commit/diff，不自行 commit/tag |
| `agent-commit` | 用户已授权 Agent 按任务/Phase 提交 |
| `branch-per-agent` | 多 Agent 各自在 branch/worktree 工作，由集成者合并 |

没有授权时，Skill 不默认创建 tag、branch 或 commit。

## 已知良好点

每个 Phase 门控通过可作为一个已知良好点，至少记录：

- commit 或受控 diff 标识；
- dirty worktree 状态；
- 对应 gate evidence（含保证等级与 revision）；
- 尚未覆盖的数据/外部副作用；
- 回退所需授权；
- 其他 Agent 的并行成果。

## 源码回退优先级

默认顺序：

1. revert 当前 Agent 自己拥有的独立 commit；
2. 恢复明确列出的文件/区块；
3. 在隔离 branch/worktree 中重新构建；
4. 只有用户明确授权且确认无他人成果时，才考虑整体回退。

禁止默认：`git reset --hard`、覆盖未提交用户修改、回退其他 Agent 的已验收成果、把源码恢复报告成数据/生产恢复完成。

## guarded 恢复门控

guarded Auto-ready 前必须有对应的恢复或补偿路径（数据 down migration / 备份、外部 provider rollback / 补偿事务），否则保持 copilot 或由人审批。无恢复机制时显式标注「未覆盖」，不假装完整恢复。
