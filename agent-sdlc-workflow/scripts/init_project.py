#!/usr/bin/env python3
"""Create a minimal Agent SDLC project skeleton (v2.0).

Existing files are skipped (idempotent). ``--force`` backs up skill-owned files
before overwriting. ``--dry-run`` previews changes without writing.

Safety (v2.0):
- refuses to write through a symlink / reparse point (junction / mount point);
- validates every target stays inside the project root;
- fails clearly when a file target is occupied by a directory;
- writes atomically (temp file + ``os.replace``);
- never overwrites or silently appends to an ``AGENTS.md`` that has no managed
  block (it generates ``AGENTS.agent-sdlc.md`` instead, and the project stays
  Plan-ready until the block is merged);
- renders the managed rules block in ``AGENTS.md`` as a projection of
  ``references/core-rules.md`` (single authoring source) with a ruleset/hash.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import stat
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_ROOT / "assets" / "templates"
CORE_RULES = SKILL_ROOT / "references" / "core-rules.md"
RULESET = "2.0"
MANAGED_START = "agent-sdlc:managed:start"
MANAGED_END = "agent-sdlc:managed:end"

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

AGENTS_HEADER = """# AGENTS.md

## 项目命令
- 局部/快速检查：`__`
- 受影响回归：`__`
- 完整/发布级门控：`__`
- 构建/打包：`__`
- 关键路径 E2E：`__`

## 工作约定
- 治理与需求见 CONSTITUTION.md 与 specs/；计划与证据见 plans/
- 核心规则见下方受管区块；完整语义见 skill 内 references/core-rules.md（rule ID 对齐）
- fast-track 零落盘；Project Mode 才创建流程文件（RULE-FAST-001）
- 局部阻塞时继续其他安全任务；只有无安全路径时才合并请求用户（RULE-USER-001）

## 项目特有禁区
- __

"""

AGENTS_SIDECAR_NOTE = """# AGENTS.agent-sdlc.md

> 项目已存在未受管的 `AGENTS.md`，初始化器**未覆盖也未追加**它。
> 下面是 Agent SDLC 的受管规则区块。请把它合并进你的 `AGENTS.md`
> （或以 include 引用），再删除本文件。
>
> **在受管区块合并进项目规则入口之前，本项目只能是 Plan-ready，不得声称 Auto-ready。**

"""


class InitError(RuntimeError):
    pass


def configure_utf8_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")


def preflight() -> None:
    missing = [name for name in COPY_MAP if not (TEMPLATES / name).is_file()]
    if missing:
        raise InitError("缺少模板: " + ", ".join(missing))
    if not CORE_RULES.is_file():
        raise InitError("缺少 canonical 规则源: " + str(CORE_RULES))


def load_managed_rules() -> list[str]:
    rules: list[str] = []
    in_section = False
    for line in CORE_RULES.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_section = "运行时核心子集" in line
            continue
        if in_section and line.startswith("- RULE-"):
            rules.append(line.strip())
    if not rules:
        raise InitError("core-rules.md 未提供受管投影子集")
    return rules


def render_managed_block(rules: list[str]) -> str:
    body_lines = ["## Agent SDLC 核心规则（受管区块）", ""]
    body_lines.extend(rules)
    body_lines.extend(
        [
            "",
            "项目命令和实例值见 CONSTITUTION.md 与 plans/env-gates-checklist.md。",
            "完整规则见 skill 内 references/core-rules.md（以 rule ID 对齐）。",
        ]
    )
    body = "\n".join(body_lines) + "\n"
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return (
        f"<!-- {MANAGED_START} ruleset={RULESET} hash={digest} -->\n"
        f"{body}"
        f"<!-- {MANAGED_END} -->\n"
    )


def is_reparse(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        st = path.lstat()
    except OSError:
        return False
    attrs = getattr(st, "st_file_attributes", 0)
    reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(attrs & reparse)


def _within(base: Path, target: Path) -> bool:
    try:
        target.relative_to(base)
        return True
    except ValueError:
        return False


def validate_target(root: Path, rel: str) -> Path:
    target = root / rel
    cursor = root
    for part in Path(rel).parts:
        cursor = cursor / part
        if cursor.is_symlink() or (cursor.exists() and is_reparse(cursor)):
            raise InitError(f"拒绝通过符号链接/reparse point 写出项目根: {cursor}")
    root_res = root.resolve()
    parent_res = target.parent.resolve()
    if parent_res != root_res and not _within(root_res, parent_res):
        raise InitError(f"目标逸出项目根: {target}")
    if target.exists() and target.is_dir():
        raise InitError(f"文件目标被目录占据: {target}")
    return target


def atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def atomic_write_text(path: Path, content: str) -> None:
    atomic_write_bytes(path, content.encode("utf-8"))


def atomic_copy(src: Path, dst: Path) -> None:
    atomic_write_bytes(dst, src.read_bytes())


def backup(root: Path, target: Path, backup_root: Path) -> None:
    destination = backup_root / target.relative_to(root)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target, destination)


def has_managed_block(path: Path) -> bool:
    return path.is_file() and MANAGED_START in path.read_text(encoding="utf-8")


def main() -> int:
    configure_utf8_output()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    try:
        preflight()
        rules = load_managed_rules()
        block = render_managed_block(rules)
    except InitError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 2

    root = Path(args.project_root).resolve()
    if root.exists() and not root.is_dir():
        parser.error(f"目标不是目录: {root}")

    agents_md = root / "AGENTS.md"
    agents_unmanaged = agents_md.is_file() and not has_managed_block(agents_md)

    generated = {"NOTES.md": NOTES_MD}
    sources = {destination: TEMPLATES / source for source, destination in COPY_MAP.items()}
    plain_targets = [*sources, *generated]

    create = [name for name in plain_targets if not (root / name).exists()]
    overwrite = [name for name in plain_targets if (root / name).exists() and args.force]
    skip = [name for name in plain_targets if (root / name).exists() and not args.force]

    # AGENTS.md is handled separately from the plain generated files.
    if agents_unmanaged:
        agents_action = "sidecar"  # generate AGENTS.agent-sdlc.md, do not touch AGENTS.md
    elif agents_md.is_file():
        agents_action = "skip" if not args.force else "refresh"
    else:
        agents_action = "create"

    if args.dry_run:
        print(f"Dry run: {root}")
        for name in create:
            print(f"  + {name}")
        if agents_action == "create":
            print("  + AGENTS.md（含受管区块）")
        elif agents_action == "refresh":
            print("  ! 刷新 AGENTS.md 受管区块（备份后）")
        elif agents_action == "sidecar":
            print("  + AGENTS.agent-sdlc.md（已有未受管 AGENTS.md，不覆盖；仅 Plan-ready）")
        elif agents_action == "skip":
            print("  = 跳过 AGENTS.md")
        for name in overwrite:
            print(f"  ! 覆盖并备份 {name}")
        for name in skip:
            print(f"  = 跳过 {name}")
        return 0

    root.mkdir(parents=True, exist_ok=True)
    for directory in DIRS:
        (root / directory).mkdir(parents=True, exist_ok=True)

    backup_root: Path | None = None
    need_backup = bool(overwrite) or (agents_action == "refresh" and agents_md.is_file())
    if need_backup:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup_root = root / ".agent-sdlc-backups" / stamp
        for name in overwrite:
            backup(root, root / name, backup_root)
        if agents_action == "refresh":
            backup(root, agents_md, backup_root)

    # Validate all plain targets first so a failure leaves no partial state.
    for name in plain_targets:
        validate_target(root, name)
    if agents_action in ("create", "refresh"):
        validate_target(root, "AGENTS.md")
    if agents_action == "sidecar":
        validate_target(root, "AGENTS.agent-sdlc.md")

    for name, source in sources.items():
        target = root / name
        if target.exists() and not args.force:
            continue
        atomic_copy(source, target)

    for name, content in generated.items():
        target = root / name
        if target.exists() and not args.force:
            continue
        atomic_write_text(target, content)

    if agents_action == "create":
        atomic_write_text(agents_md, AGENTS_HEADER + block)
    elif agents_action == "refresh":
        atomic_write_text(agents_md, AGENTS_HEADER + block)
    elif agents_action == "sidecar":
        atomic_write_text(root / "AGENTS.agent-sdlc.md", AGENTS_SIDECAR_NOTE + block)

    print(f"初始化完成: {root}")
    for name in create:
        print(f"  + {name}")
    if agents_action == "create":
        print("  + AGENTS.md（含受管区块）")
    elif agents_action == "refresh":
        print("  ! 已刷新 AGENTS.md 受管区块")
    elif agents_action == "sidecar":
        print("  + AGENTS.agent-sdlc.md（已有未受管 AGENTS.md，未覆盖）")
        print("  ⚠ 受管区块合并进 AGENTS.md 之前，本项目仅 Plan-ready")
    elif agents_action == "skip":
        print("  = 已跳过 AGENTS.md")
    for name in overwrite:
        print(f"  ! 已覆盖 {name}")
    for name in skip:
        print(f"  = 已跳过 {name}")
    if backup_root:
        print(f"备份: {backup_root}")
    print("下一步: 由 Agent 基于项目起草前三阶段产物，能力协商达标并集中确认后进入 auto execution。")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except InitError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        sys.exit(2)
