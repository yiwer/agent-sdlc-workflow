import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INIT = REPO_ROOT / "agent-sdlc-workflow" / "scripts" / "init_project.py"


def run(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run([sys.executable, *args], capture_output=True, check=False)


class InitProjectTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="agent-sdlc-test-")
        self.root = Path(self.temp.name) / "project"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def init(self, *extra: str) -> subprocess.CompletedProcess[bytes]:
        return run(str(INIT), str(self.root), *extra)

    def test_dry_run_is_read_only_and_utf8(self) -> None:
        result = self.init("--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Dry run", result.stdout.decode("utf-8"))
        self.assertFalse(self.root.exists())

    def test_scaffold_is_minimal_and_idempotent(self) -> None:
        first = self.init()
        self.assertEqual(first.returncode, 0, first.stderr)
        expected = {
            "CONSTITUTION.md",
            "AGENTS.md",
            "NOTES.md",
            "specs/TEMPLATE-spec.md",
            "specs/changes/TEMPLATE-change.md",
            "docs/adr/TEMPLATE.md",
            "plans/env-gates-checklist.md",
            "plans/TEMPLATE-phase-plan.md",
            "plans/execution-protocol.md",
            "plans/TEMPLATE-acceptance-retro.md",
            "plans/logs/TEMPLATE-checkpoint.md",
        }
        actual = {
            path.relative_to(self.root).as_posix()
            for path in self.root.rglob("*")
            if path.is_file()
        }
        self.assertEqual(actual, expected)
        self.assertFalse((self.root / ".agent-sdlc").exists())
        self.assertFalse((self.root / "plans" / "whitelist-ledger.md").exists())

        notes_before = (self.root / "NOTES.md").read_bytes()
        second = self.init()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(notes_before, (self.root / "NOTES.md").read_bytes())

    def test_force_is_recoverable(self) -> None:
        self.assertEqual(self.init().returncode, 0)
        notes = self.root / "NOTES.md"
        notes.write_text("user content\n", encoding="utf-8")

        result = self.init("--force")
        self.assertEqual(result.returncode, 0, result.stderr)
        backups = list((self.root / ".agent-sdlc-backups").glob("*/NOTES.md"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "user content\n")


if __name__ == "__main__":
    unittest.main()
