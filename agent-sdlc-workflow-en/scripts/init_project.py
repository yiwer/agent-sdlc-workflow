#!/usr/bin/env python3
"""Create a minimal Agent SDLC project skeleton (v2.0).

Existing files are skipped (idempotent). ``--force`` backs up skill-owned files
before overwriting. ``--dry-run`` previews changes without writing.

Safety (v2.0):
- refuses to write through a symlink or reparse point such as a junction or
  mount point;
- validates every target stays inside the project root;
- fails clearly when a file target is occupied by a directory;
- writes atomically with a temporary file and ``os.replace``;
- never overwrites or silently appends to an ``AGENTS.md`` without a managed
  block; it generates ``AGENTS.agent-sdlc.md`` instead, and the project remains
  Plan-ready until the block is merged;
- renders the managed rules block in ``AGENTS.md`` as a projection of
  ``references/core-rules.md`` with a ruleset and content hash.
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

## Current Goal and Progress
- __

## Next Steps
- [ ] __

## Material Findings or Local Blockers
- __

## Latest Checkpoint
- __
"""

AGENTS_HEADER = """# AGENTS.md

## Project Commands
- Local / fast check: `__`
- Affected regression: `__`
- Complete / release gate: `__`
- Build / package: `__`
- Critical-path E2E: `__`

## Working Agreements
- Governance and requirements live in CONSTITUTION.md and specs/; plans and evidence live in plans/.
- Core rules appear in the managed block below. Full semantics live in the skill's references/core-rules.md and align by rule ID.
- Fast-track creates no workflow files. Only Project Mode creates persistent process artifacts (`RULE-FAST-001`).
- Continue other safe tasks when locally blocked. Ask the user only when no safe path remains (`RULE-USER-001`).

## Project-Specific Prohibited Areas
- __

"""

AGENTS_SIDECAR_NOTE = """# AGENTS.agent-sdlc.md

> The project already contains an unmanaged `AGENTS.md`. The initializer did
> **not overwrite or append to it**. The managed Agent SDLC rules block appears
> below. Merge it into `AGENTS.md`, or reference it through an include, then
> delete this sidecar.
>
> **Until the managed block is merged into the project's rule entry point, the
> project is only Plan-ready and must not claim Auto-ready.**

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
        raise InitError("Missing templates: " + ", ".join(missing))
    if not CORE_RULES.is_file():
        raise InitError("Missing canonical rule source: " + str(CORE_RULES))


def load_managed_rules() -> list[str]:
    rules: list[str] = []
    in_section = False
    for line in CORE_RULES.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_section = "Runtime Core Subset" in line
            continue
        if in_section and line.startswith("- RULE-"):
            rules.append(line.strip())
    if not rules:
        raise InitError("core-rules.md does not provide a managed projection subset")
    return rules


def render_managed_block(rules: list[str]) -> str:
    body_lines = ["## Agent SDLC Core Rules (Managed Block)", ""]
    body_lines.extend(rules)
    body_lines.extend(
        [
            "",
            "See CONSTITUTION.md and plans/env-gates-checklist.md for project commands and instantiated values.",
            "See the skill's references/core-rules.md for full rules aligned by rule ID.",
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
            raise InitError(
                f"Refusing to write outside the project root through a symlink "
                f"or reparse point: {cursor}"
            )
    root_res = root.resolve()
    parent_res = target.parent.resolve()
    if parent_res != root_res and not _within(root_res, parent_res):
        raise InitError(f"Target escapes the project root: {target}")
    if target.exists() and target.is_dir():
        raise InitError(f"File target is occupied by a directory: {target}")
    return target


def atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=path.name + ".",
        suffix=".tmp",
    )
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
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    root = Path(args.project_root).resolve()
    if root.exists() and not root.is_dir():
        parser.error(f"Target is not a directory: {root}")

    agents_md = root / "AGENTS.md"
    agents_unmanaged = agents_md.is_file() and not has_managed_block(agents_md)

    generated = {"NOTES.md": NOTES_MD}
    sources = {
        destination: TEMPLATES / source
        for source, destination in COPY_MAP.items()
    }
    plain_targets = [*sources, *generated]

    create = [name for name in plain_targets if not (root / name).exists()]
    overwrite = [
        name for name in plain_targets if (root / name).exists() and args.force
    ]
    skip = [
        name
        for name in plain_targets
        if (root / name).exists() and not args.force
    ]

    # Handle AGENTS.md separately from plain generated files.
    if agents_unmanaged:
        agents_action = "sidecar"
    elif agents_md.is_file():
        agents_action = "skip" if not args.force else "refresh"
    else:
        agents_action = "create"

    if args.dry_run:
        print(f"Dry run: {root}")
        for name in create:
            print(f"  + {name}")
        if agents_action == "create":
            print("  + AGENTS.md (with managed block)")
        elif agents_action == "refresh":
            print("  ! Refresh AGENTS.md managed block after backup")
        elif agents_action == "sidecar":
            print(
                "  + AGENTS.agent-sdlc.md "
                "(unmanaged AGENTS.md exists; no overwrite; Plan-ready only)"
            )
        elif agents_action == "skip":
            print("  = Skip AGENTS.md")
        for name in overwrite:
            print(f"  ! Overwrite and back up {name}")
        for name in skip:
            print(f"  = Skip {name}")
        return 0

    root.mkdir(parents=True, exist_ok=True)
    for directory in DIRS:
        (root / directory).mkdir(parents=True, exist_ok=True)

    backup_root: Path | None = None
    need_backup = bool(overwrite) or (
        agents_action == "refresh" and agents_md.is_file()
    )
    if need_backup:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup_root = root / ".agent-sdlc-backups" / stamp
        for name in overwrite:
            backup(root, root / name, backup_root)
        if agents_action == "refresh":
            backup(root, agents_md, backup_root)

    # Validate every target before writing so a failure leaves no partial state.
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
        atomic_write_text(
            root / "AGENTS.agent-sdlc.md",
            AGENTS_SIDECAR_NOTE + block,
        )

    print(f"Initialization complete: {root}")
    for name in create:
        print(f"  + {name}")
    if agents_action == "create":
        print("  + AGENTS.md (with managed block)")
    elif agents_action == "refresh":
        print("  ! Refreshed AGENTS.md managed block")
    elif agents_action == "sidecar":
        print(
            "  + AGENTS.agent-sdlc.md "
            "(unmanaged AGENTS.md exists and was not overwritten)"
        )
        print(
            "  WARNING: The project remains Plan-ready until the managed block "
            "is merged into AGENTS.md"
        )
    elif agents_action == "skip":
        print("  = Skipped AGENTS.md")
    for name in overwrite:
        print(f"  ! Overwrote {name}")
    for name in skip:
        print(f"  = Skipped {name}")
    if backup_root:
        print(f"Backup: {backup_root}")
    print(
        "Next: have the Agent draft the first three stages from project context, "
        "then enter auto execution only after capability negotiation passes and "
        "the goal and material tradeoffs are confirmed together."
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except InitError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)
