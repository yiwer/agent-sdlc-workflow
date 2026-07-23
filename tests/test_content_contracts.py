import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "agent-sdlc-workflow"
CORE_RULES = SKILL_DIR / "references" / "core-rules.md"
INIT = SKILL_DIR / "scripts" / "init_project.py"

RULE_RE = re.compile(r"RULE-[A-Z]+-\d+")
DEFINED_RE = re.compile(r"\*\*(RULE-[A-Z]+-\d+)")


def defined_rule_ids() -> set[str]:
    return set(DEFINED_RE.findall(CORE_RULES.read_text(encoding="utf-8")))


def referenced_rule_ids() -> set[str]:
    ids: set[str] = set()
    for md in SKILL_DIR.rglob("*.md"):
        ids.update(RULE_RE.findall(md.read_text(encoding="utf-8")))
    return ids


def managed_subset_ids() -> set[str]:
    ids: set[str] = set()
    in_section = False
    for line in CORE_RULES.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_section = "运行时核心子集" in line
            continue
        if in_section and line.startswith("- RULE-"):
            ids.update(RULE_RE.findall(line))
    return ids


class ContentContractTest(unittest.TestCase):
    def test_referenced_rules_are_defined(self) -> None:
        defined = defined_rule_ids()
        self.assertGreater(len(defined), 10, "canonical 规则目录应非空")
        dangling = referenced_rule_ids() - defined
        self.assertEqual(dangling, set(), f"引用了未定义的 rule ID: {sorted(dangling)}")

    def test_managed_subset_nonempty_and_defined(self) -> None:
        subset = managed_subset_ids()
        self.assertGreaterEqual(len(subset), 4)
        self.assertTrue(subset <= defined_rule_ids(), "受管子集必须都已定义")

    def test_managed_block_matches_subset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "proj"
            result = subprocess.run(
                [sys.executable, str(INIT), str(root)], capture_output=True, check=False
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        match = re.search(
            r"agent-sdlc:managed:start[^\n]*-->\n(.*?)<!-- agent-sdlc:managed:end -->",
            agents,
            re.S,
        )
        self.assertIsNotNone(match)
        rendered = set(RULE_RE.findall(match.group(1)))
        self.assertEqual(rendered, managed_subset_ids())

    def test_checkpoint_template_has_assurance_fields(self) -> None:
        text = (SKILL_DIR / "assets" / "templates" / "TEMPLATE-checkpoint.md").read_text(
            encoding="utf-8"
        )
        for token in ("保证等级", "Revision", "captured_by", "self-reported"):
            self.assertIn(token, text)

    def test_fast_track_zero_persistence_asserted(self) -> None:
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("零落盘", text)
        self.assertIn("RULE-FAST-001", text)

    def test_templates_have_no_external_install_runtime_dependency(self) -> None:
        templates = list((SKILL_DIR / "assets" / "templates").glob("*.md"))
        self.assertGreater(len(templates), 0)
        for tpl in templates:
            text = tpl.read_text(encoding="utf-8")
            for token in ("~/.claude", "~/.codex", "~/.kimi"):
                self.assertNotIn(token, text, f"{tpl.name} 不应依赖外部安装路径")

    def test_force_not_recommended_as_migration(self) -> None:
        migration = REPO_ROOT / "MIGRATION-v1.5-to-v2.0.md"
        self.assertTrue(migration.exists(), "缺少迁移指南")
        text = migration.read_text(encoding="utf-8")
        self.assertIn("--force", text)
        self.assertTrue("不推荐" in text or "不是迁移" in text)

    def test_readme_mentions_v2(self) -> None:
        text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertTrue("v2.0" in text or "2.0" in text)


if __name__ == "__main__":
    unittest.main()
