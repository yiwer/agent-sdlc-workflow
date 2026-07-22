#!/usr/bin/env python3
"""Create a minimal Agent SDLC project skeleton.

Existing files are skipped. ``--force`` backs up files before overwriting;
``--dry-run`` previews changes.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


TEMPLATES = Path(__file__).resolve().parent.parent / "assets" / "templates"

COPY_MAP = {
    "phase0-constitution.md": "CONSTITUTION.md",
    "phase1-spec-modeling.md": "specs/TEMPLATE-spec.md",
    "TEMPLATE-spec-change.md": "specs/changes/TEMPLATE-change.md",
    "TEMPLATE-adr.md": "docs/adr/TEMPLATE.md",
    "phase2-env-gates.md": "plans/env-gates-checklist.md",
    "phase3-phase-planning.md": "plans/TEMPLATE-phase-plan.md",
    "phase4-execution-protocol.md": "plans/execution-protocol.md",
    "phase5-acceptance-retro.md": "plans/TEMPLATE-acceptance-retro.md",
    "TEMPLATE-checkpoint.md": "plans/logs/TEMPLATE-checkpoint.md",
}

DIRS = ("specs/changes", "docs/adr", "plans/logs", "tests")

NOTES_MD = """# NOTES.md

## 当前目标与进度
- __

## 下一步
- [ ] __

## 重要发现或局部阻塞
- __

## 最近 checkpoint
- __
"""

AGENTS_MD = """# AGENTS.md

## 项目命令
- 局部/快速检查：`__`
- 受影响回归：`__`
- 完整/发布级门控：`__`
- 构建/打包：`__`
- 关键路径 E2E：`__`

## 工作约定
- 治理原则见 `CONSTITUTION.md`，需求与 AC 见 `specs/`，计划与证据见 `plans/`
- 当前 goal 内需要的仓库文件可直接修改，不做逐文件审批或白名单登记
- 任务影响区域仅用于估算和并发协调；重要影响在 checkpoint 概括
- 迭代跑局部检查，任务/批次跑受影响回归，Phase 跑相关集成/E2E，Goal 确保有最后变更后的完整门控证据
- 最新任务/Phase 结果已等同或覆盖完整门控时直接复用，不重复运行
- 共享契约、schema、权限、安全、依赖、全局配置、并发或迁移变化时提前升级验证范围
- 局部阻塞时继续其他安全任务；只有无安全路径时才合并请求用户

## 项目特有禁区
- __
"""


def configure_utf8_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")


def preflight() -> None:
    missing = [name for name in COPY_MAP if not (TEMPLATES / name).is_file()]
    if missing:
        raise FileNotFoundError("缺少模板: " + ", ".join(missing))


def backup(root: Path, target: Path, backup_root: Path) -> None:
    destination = backup_root / target.relative_to(root)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target, destination)


def main() -> int:
    configure_utf8_output()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    preflight()
    root = Path(args.project_root).resolve()
    if root.exists() and not root.is_dir():
        parser.error(f"目标不是目录: {root}")

    generated = {"NOTES.md": NOTES_MD, "AGENTS.md": AGENTS_MD}
    sources = {destination: TEMPLATES / source for source, destination in COPY_MAP.items()}
    targets = [*sources, *generated]
    create = [name for name in targets if not (root / name).exists()]
    overwrite = [name for name in targets if (root / name).exists() and args.force]
    skip = [name for name in targets if (root / name).exists() and not args.force]

    if args.dry_run:
        print(f"Dry run: {root}")
        for name in create:
            print(f"  + {name}")
        for name in overwrite:
            print(f"  ! 覆盖并备份 {name}")
        for name in skip:
            print(f"  = 跳过 {name}")
        return 0

    root.mkdir(parents=True, exist_ok=True)
    for directory in DIRS:
        (root / directory).mkdir(parents=True, exist_ok=True)

    backup_root: Path | None = None
    if overwrite:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup_root = root / ".agent-sdlc-backups" / stamp
        for name in overwrite:
            backup(root, root / name, backup_root)

    for name, source in sources.items():
        target = root / name
        if target.exists() and not args.force:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    for name, content in generated.items():
        target = root / name
        if target.exists() and not args.force:
            continue
        target.write_text(content, encoding="utf-8")

    print(f"初始化完成: {root}")
    for name in create:
        print(f"  + {name}")
    for name in overwrite:
        print(f"  ! 已覆盖 {name}")
    for name in skip:
        print(f"  = 已跳过 {name}")
    if backup_root:
        print(f"备份: {backup_root}")
    print("下一步: 由 Agent 基于项目起草前三阶段产物，集中确认后进入 auto execution。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
