#!/usr/bin/env python3
"""Pack and verify the ``agent-sdlc-workflow.skill`` bundle.

Default mode builds the ``.skill`` (a ZIP) from an explicit allowlist of runtime
files. ``--check`` verifies an existing bundle matches the source allowlist
file-by-file (content sha256), failing on missing, extra, or differing files.

Byte-level reproducible builds are a nice-to-have, not a release gate; entry
order and timestamps are still normalized so builds are stable in practice.
The package/source consistency that ``--check`` enforces IS a gate (AC-15).
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SKILL_DIR = REPO_ROOT / "agent-sdlc-workflow"
DEFAULT_PACKAGE = REPO_ROOT / "agent-sdlc-workflow.skill"
FIXED_DATE = (1980, 1, 1, 0, 0, 0)
SKILL_NAME_RE = re.compile(r"^name:\s*([a-z0-9-]+)\s*$", re.MULTILINE)

# Allowlist globs relative to the skill dir. Anything not matched is excluded
# (no caches, IDE files, tests, evals, fixtures, or the legacy template pack).
ALLOWLIST = [
    "SKILL.md",
    "VERSION",
    "agents/openai.yaml",
    "references/*.md",
    "references/bindings/*.md",
    "assets/templates/*.md",
    "scripts/init_project.py",
]

REQUIRED = ["SKILL.md", "VERSION", "references/core-rules.md"]


def configure_utf8_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")


def collect_source_files(skill_dir: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for pattern in ALLOWLIST:
        for path in skill_dir.glob(pattern):
            if path.is_file():
                rel = path.relative_to(skill_dir).as_posix()
                files[rel] = path
    return dict(sorted(files.items()))


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def skill_name(skill_dir: Path) -> str:
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    frontmatter = text.split("---", 2)
    if len(frontmatter) < 3:
        raise RuntimeError(f"SKILL.md 缺少 YAML frontmatter: {skill_md}")
    match = SKILL_NAME_RE.search(frontmatter[1])
    if not match:
        raise RuntimeError(f"SKILL.md 缺少合法 name: {skill_md}")
    return match.group(1)


def build(
    skill_dir: Path, package_path: Path
) -> tuple[dict[str, Path], str, str]:
    files = collect_source_files(skill_dir)
    missing = [rel for rel in REQUIRED if rel not in files]
    if missing:
        raise RuntimeError("缺少必需文件: " + ", ".join(missing))
    prefix = skill_name(skill_dir)
    version = (skill_dir / "VERSION").read_text(encoding="utf-8").strip()
    if not version:
        raise RuntimeError("VERSION 为空")

    package_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for rel, path in files.items():
            info = zipfile.ZipInfo(f"{prefix}/{rel}", date_time=FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, path.read_bytes())
    return files, version, prefix


def package_entries(package_path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    with zipfile.ZipFile(package_path) as zf:
        for name in zf.namelist():
            if name.endswith("/"):
                continue
            entries[name] = _sha256_bytes(zf.read(name))
    return entries


def check(skill_dir: Path, package_path: Path) -> tuple[bool, list[str]]:
    if not package_path.exists():
        return False, [f"包不存在: {package_path}"]
    prefix = skill_name(skill_dir)
    expected = {
        f"{prefix}/{rel}": _sha256_file(path)
        for rel, path in collect_source_files(skill_dir).items()
    }
    actual = package_entries(package_path)
    problems: list[str] = []
    for name, digest in expected.items():
        if name not in actual:
            problems.append(f"包内缺失: {name}")
        elif actual[name] != digest:
            problems.append(f"内容不一致: {name}")
    for name in actual:
        if name not in expected:
            problems.append(f"包内多余: {name}")
    return (not problems), problems


def main() -> int:
    configure_utf8_output()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", default=str(DEFAULT_SKILL_DIR))
    parser.add_argument("-o", "--output", default=str(DEFAULT_PACKAGE))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    package_path = Path(args.output).resolve()

    try:
        if args.check:
            ok, problems = check(skill_dir, package_path)
            if ok:
                print(f"包与源码一致: {package_path}")
                return 0
            for line in problems:
                print(f"  ✗ {line}")
            print(f"包与源码不一致（{len(problems)} 项）")
            return 1

        files, version, prefix = build(skill_dir, package_path)
    except RuntimeError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 2
    print(f"已打包 v{version}: {package_path}（{len(files)} 个文件）")
    for rel in files:
        print(f"  + {prefix}/{rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
