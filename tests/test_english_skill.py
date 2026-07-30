import hashlib
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_SKILL = REPO_ROOT / "agent-sdlc-workflow"
ENGLISH_SKILL = REPO_ROOT / "agent-sdlc-workflow-en"
PACKAGER = REPO_ROOT / "scripts" / "package_skill.py"

CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
RULE_RE = re.compile(r"RULE-[A-Z]+-\d+")
DEFINED_RE = re.compile(r"\*\*(RULE-[A-Z]+-\d+)")


def runtime_files(root: Path) -> dict[str, Path]:
    return {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file()
    }


class EnglishSkillTest(unittest.TestCase):
    def test_runtime_layout_matches_source_skill(self) -> None:
        self.assertEqual(
            set(runtime_files(ENGLISH_SKILL)),
            set(runtime_files(SOURCE_SKILL)),
        )

    def test_runtime_text_is_english_only_and_has_no_scaffold_todos(self) -> None:
        for relative, path in runtime_files(ENGLISH_SKILL).items():
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(
                CJK_RE.search(text),
                f"{relative} still contains CJK text",
            )
            self.assertNotIn("[TODO:", text, f"{relative} still contains scaffold TODOs")

    def test_rule_ids_match_source_skill(self) -> None:
        source_core = (
            SOURCE_SKILL / "references" / "core-rules.md"
        ).read_text(encoding="utf-8")
        english_core = (
            ENGLISH_SKILL / "references" / "core-rules.md"
        ).read_text(encoding="utf-8")
        self.assertEqual(
            set(DEFINED_RE.findall(english_core)),
            set(DEFINED_RE.findall(source_core)),
        )

        source_refs: set[str] = set()
        english_refs: set[str] = set()
        for path in SOURCE_SKILL.rglob("*.md"):
            source_refs.update(RULE_RE.findall(path.read_text(encoding="utf-8")))
        for path in ENGLISH_SKILL.rglob("*.md"):
            english_refs.update(RULE_RE.findall(path.read_text(encoding="utf-8")))
        self.assertEqual(english_refs, source_refs)

    def test_metadata_uses_english_skill_name(self) -> None:
        skill = (ENGLISH_SKILL / "SKILL.md").read_text(encoding="utf-8")
        openai = (ENGLISH_SKILL / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("name: agent-sdlc-workflow-en", skill)
        self.assertIn("$agent-sdlc-workflow-en", openai)
        self.assertNotIn("$agent-sdlc-workflow\"", openai)

    def test_english_initializer_generates_english_project(self) -> None:
        initializer = ENGLISH_SKILL / "scripts" / "init_project.py"
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            result = subprocess.run(
                [sys.executable, str(initializer), str(project)],
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            stdout = result.stdout.decode("utf-8")
            self.assertIn("Initialization complete", stdout)
            for relative in ("AGENTS.md", "NOTES.md", "CONSTITUTION.md"):
                text = (project / relative).read_text(encoding="utf-8")
                self.assertIsNone(CJK_RE.search(text), relative)

    def test_packager_uses_english_skill_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "agent-sdlc-workflow-en.skill"
            built = subprocess.run(
                [
                    sys.executable,
                    str(PACKAGER),
                    "--skill-dir",
                    str(ENGLISH_SKILL),
                    "-o",
                    str(package),
                ],
                capture_output=True,
                check=False,
            )
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            with zipfile.ZipFile(package) as archive:
                names = archive.namelist()
            self.assertGreater(len(names), 0)
            self.assertTrue(
                all(name.startswith("agent-sdlc-workflow-en/") for name in names)
            )

            checked = subprocess.run(
                [
                    sys.executable,
                    str(PACKAGER),
                    "--skill-dir",
                    str(ENGLISH_SKILL),
                    "-o",
                    str(package),
                    "--check",
                ],
                capture_output=True,
                check=False,
            )
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)


class EnglishInitializerSafetyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="agent-sdlc-en-safe-")
        self.root = Path(self.temp.name) / "project"
        self.initializer = ENGLISH_SKILL / "scripts" / "init_project.py"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def init(self, *extra: str) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            [sys.executable, str(self.initializer), str(self.root), *extra],
            capture_output=True,
            check=False,
        )

    def test_dry_run_is_read_only_and_idempotent(self) -> None:
        preview = self.init("--dry-run")
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertIn("Dry run", preview.stdout.decode("utf-8"))
        self.assertFalse(self.root.exists())

        first = self.init()
        self.assertEqual(first.returncode, 0, first.stderr)
        before = {
            path.relative_to(self.root).as_posix(): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file()
        }
        second = self.init()
        self.assertEqual(second.returncode, 0, second.stderr)
        after = {
            path.relative_to(self.root).as_posix(): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file()
        }
        self.assertEqual(after, before)

    def test_managed_block_has_valid_hash(self) -> None:
        self.assertEqual(self.init().returncode, 0)
        agents = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        marker = re.search(
            r"managed:start ruleset=2.0 hash=([0-9a-f]{64})",
            agents,
        )
        self.assertIsNotNone(marker)
        block = re.search(
            r"agent-sdlc:managed:start[^\n]*-->\n"
            r"(.*?)<!-- agent-sdlc:managed:end -->",
            agents,
            re.S,
        )
        self.assertIsNotNone(block)
        self.assertEqual(
            hashlib.sha256(block.group(1).encode("utf-8")).hexdigest(),
            marker.group(1),
        )

    def test_unmanaged_agents_is_preserved_with_sidecar(self) -> None:
        self.root.mkdir(parents=True)
        agents = self.root / "AGENTS.md"
        agents.write_text("# user rules\n", encoding="utf-8")
        result = self.init()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(agents.read_text(encoding="utf-8"), "# user rules\n")
        sidecar = self.root / "AGENTS.agent-sdlc.md"
        self.assertTrue(sidecar.is_file())
        self.assertIn(
            "agent-sdlc:managed:start",
            sidecar.read_text(encoding="utf-8"),
        )
        self.assertIn("Plan-ready", result.stdout.decode("utf-8"))

    def test_force_backs_up_owned_files(self) -> None:
        self.assertEqual(self.init().returncode, 0)
        notes = self.root / "NOTES.md"
        notes.write_text("user content\n", encoding="utf-8")
        forced = self.init("--force")
        self.assertEqual(forced.returncode, 0, forced.stderr)
        backups = list(
            (self.root / ".agent-sdlc-backups").glob("*/NOTES.md")
        )
        self.assertEqual(len(backups), 1)
        self.assertEqual(
            backups[0].read_text(encoding="utf-8"),
            "user content\n",
        )

    def test_directory_at_file_target_fails_clearly(self) -> None:
        self.root.mkdir(parents=True)
        (self.root / "CONSTITUTION.md").mkdir()
        result = self.init()
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "occupied by a directory",
            result.stderr.decode("utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
