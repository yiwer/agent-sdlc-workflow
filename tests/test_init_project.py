import os
import re
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


class InitProjectSafetyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="agent-sdlc-safe-")
        self.root = Path(self.temp.name) / "project"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def init(self, *extra: str) -> subprocess.CompletedProcess[bytes]:
        return run(str(INIT), str(self.root), *extra)

    def _managed_block(self, text: str) -> str:
        match = re.search(
            r"agent-sdlc:managed:start[^\n]*-->\n(.*?)<!-- agent-sdlc:managed:end -->",
            text,
            re.S,
        )
        self.assertIsNotNone(match, "AGENTS.md 缺少受管区块")
        return match.group(1)

    def test_managed_block_rendered_with_valid_hash(self) -> None:
        self.assertEqual(self.init().returncode, 0)
        agents = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        marker = re.search(r"managed:start ruleset=2.0 hash=([0-9a-f]{64})", agents)
        self.assertIsNotNone(marker, "受管区块缺少 ruleset/hash 标记")
        import hashlib

        body = self._managed_block(agents)
        self.assertEqual(hashlib.sha256(body.encode("utf-8")).hexdigest(), marker.group(1))
        ids = set(re.findall(r"RULE-[A-Z]+-\d+", body))
        self.assertGreaterEqual(len(ids), 4, "受管子集应包含核心 rule ID")

    def test_managed_agents_idempotent(self) -> None:
        self.assertEqual(self.init().returncode, 0)
        before = (self.root / "AGENTS.md").read_bytes()
        self.assertEqual(self.init().returncode, 0)
        self.assertEqual(before, (self.root / "AGENTS.md").read_bytes())

    def test_existing_unmanaged_agents_not_clobbered(self) -> None:
        self.root.mkdir(parents=True)
        agents = self.root / "AGENTS.md"
        agents.write_text("# my own agents file\nuser content\n", encoding="utf-8")

        result = self.init()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            agents.read_text(encoding="utf-8"), "# my own agents file\nuser content\n"
        )
        sidecar = self.root / "AGENTS.agent-sdlc.md"
        self.assertTrue(sidecar.exists())
        self.assertIn("agent-sdlc:managed:start", sidecar.read_text(encoding="utf-8"))
        out = result.stdout.decode("utf-8")
        self.assertIn("Plan-ready", out)

    def test_dry_run_writes_nothing_with_preexisting_agents(self) -> None:
        self.root.mkdir(parents=True)
        (self.root / "AGENTS.md").write_text("# mine\n", encoding="utf-8")
        result = self.init("--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.root / "AGENTS.agent-sdlc.md").exists())
        self.assertFalse((self.root / "NOTES.md").exists())

    def test_file_target_occupied_by_directory_fails(self) -> None:
        self.root.mkdir(parents=True)
        (self.root / "CONSTITUTION.md").mkdir()
        result = self.init()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("被目录占据", result.stderr.decode("utf-8"))

    def test_symlink_target_is_rejected(self) -> None:
        self.root.mkdir(parents=True)
        outside = Path(self.temp.name) / "outside.md"
        outside.write_text("outside\n", encoding="utf-8")
        link = self.root / "CONSTITUTION.md"
        try:
            os.symlink(outside, link)
        except (OSError, NotImplementedError, AttributeError) as exc:
            self.skipTest(f"环境不支持创建符号链接: {exc}")
        result = self.init()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reparse", result.stderr.decode("utf-8").lower())
        self.assertEqual(outside.read_text(encoding="utf-8"), "outside\n")

    def test_no_leftover_temp_files(self) -> None:
        self.assertEqual(self.init().returncode, 0)
        temps = [p for p in self.root.rglob("*") if p.name.endswith(".tmp")]
        self.assertEqual(temps, [])


if __name__ == "__main__":
    unittest.main()
