#!/usr/bin/env python3
"""Scaffold an agent-SDLC project structure from the bundled templates.

Creates the directory layout, copies phase templates into place, and
generates NOTES.md / AGENTS.md stubs. Existing files are never
overwritten unless --force is given.

Usage:
    python3 init_project.py <project-root> [--force]
"""
import argparse
import shutil
import sys
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "assets" / "templates"

# template file -> destination relative to project root
COPY_MAP = {
    "phase0-constitution.md": "CONSTITUTION.md",
    "overview.md": "docs/agent-sdlc-overview.md",
    "phase1-spec-modeling.md": "specs/TEMPLATE-spec.md",
    "phase2-env-gates.md": "plans/env-gates-checklist.md",
    "phase3-phase-planning.md": "plans/TEMPLATE-phase-plan.md",
    "phase4-execution-protocol.md": "plans/execution-protocol.md",
    "phase5-acceptance-retro.md": "plans/TEMPLATE-acceptance-retro.md",
}

DIRS = ["specs/changes", "docs/adr", "plans/logs", "tests/e2e"]

NOTES_MD = """# NOTES.md — agent 跨会话结构化笔记

> 本文件是 agent 跨上下文的唯一记忆通道。重要发现必须落盘，留在对话里等于丢失。

## 进度
- [ ] （按 plans/ 中任务卡逐项打勾，附一句话结果）

## 决策索引
- （指向 docs/adr/ 的条目 + 一句话摘要）

## 坑与遗留
- （执行中发现的环境问题、被证伪的假设、待办）
"""

AGENTS_MD = """# AGENTS.md — agent 操作手册

## 治理
- 最高治理文档：见根目录 CONSTITUTION.md（不可变原则、质量门槛、自主边界、spec 回流流程）
- 执行规程：见 plans/execution-protocol.md（checkpoint、升级策略、上下文卫生）

## 常用命令（按项目实际填写）
- lint/typecheck：`__`
- 单元测试：`__`
- e2e 验收：`__`
- 本地部署：`__`

## 目录地图
- specs/ 需求规格（唯一事实源）；specs/changes/ 进行中的变更
- plans/ phase 规划、任务卡、执行日志（plans/logs/）
- docs/adr/ 架构决策记录

## 禁区
- 禁止：__（破坏性命令、白名单外目录、未批准依赖）

## 并行护栏（多 agent 时填写）
- 串行区：__（如 DB migration、package.json、lock 文件——只允许单点修改）
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", help="目标项目根目录")
    parser.add_argument("--force", action="store_true", help="覆盖已存在的文件")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    if not root.exists():
        root.mkdir(parents=True)
        print(f"创建项目根目录: {root}")

    created, skipped = [], []

    for d in DIRS:
        (root / d).mkdir(parents=True, exist_ok=True)

    for tpl, dest in COPY_MAP.items():
        target = root / dest
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and not args.force:
            skipped.append(dest)
            continue
        shutil.copy(TEMPLATES / tpl, target)
        created.append(dest)

    for name, content in [("NOTES.md", NOTES_MD), ("AGENTS.md", AGENTS_MD)]:
        target = root / name
        if target.exists() and not args.force:
            skipped.append(name)
            continue
        target.write_text(content, encoding="utf-8")
        created.append(name)

    print("\n已创建:")
    for f in created:
        print(f"  + {f}")
    if skipped:
        print("\n已跳过（存在，使用 --force 覆盖）:")
        for f in skipped:
            print(f"  = {f}")

    print(
        "\n下一步:\n"
        "  1. 与人协同填写 CONSTITUTION.md（阶段 0 立法）\n"
        "  2. 按 specs/TEMPLATE-spec.md 完成需求与五维建模（阶段 1）\n"
        "  3. 跑通 plans/env-gates-checklist.md 的闭环门控（阶段 2）\n"
        "  4. 用 plans/TEMPLATE-phase-plan.md 切分任务并签字（阶段 3）\n"
        "  5. 按 plans/execution-protocol.md 进入 auto 长程执行（阶段 4）"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
