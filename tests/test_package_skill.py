import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PKG = REPO_ROOT / "scripts" / "package_skill.py"
SKILL_DIR = REPO_ROOT / "agent-sdlc-workflow"


def run(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run([sys.executable, str(PKG), *args], capture_output=True, check=False)


class PackageSkillTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="agent-sdlc-pkg-")
        base = Path(self.temp.name)
        self.skill = base / "skill"
        shutil.copytree(
            SKILL_DIR,
            self.skill,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.tmp"),
        )
        self.pkg = base / "out.skill"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def build(self) -> subprocess.CompletedProcess[bytes]:
        return run("--skill-dir", str(self.skill), "-o", str(self.pkg))

    def check(self) -> subprocess.CompletedProcess[bytes]:
        return run("--skill-dir", str(self.skill), "-o", str(self.pkg), "--check")

    def test_build_then_check_consistent(self) -> None:
        built = self.build()
        self.assertEqual(built.returncode, 0, built.stderr)
        checked = self.check()
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    def test_package_contains_required_and_no_disallowed(self) -> None:
        self.assertEqual(self.build().returncode, 0)
        with zipfile.ZipFile(self.pkg) as zf:
            names = set(zf.namelist())
        for required in (
            "agent-sdlc-workflow/SKILL.md",
            "agent-sdlc-workflow/VERSION",
            "agent-sdlc-workflow/references/core-rules.md",
        ):
            self.assertIn(required, names)
        for name in names:
            self.assertNotIn("__pycache__", name)
            self.assertFalse(name.endswith(".pyc"))
            self.assertNotIn("/tests/", name)
            self.assertNotIn("/evals/", name)
            self.assertNotIn("agent开发工作流模板包", name)

    def test_package_file_matches_source(self) -> None:
        import hashlib

        self.assertEqual(self.build().returncode, 0)
        source_hash = hashlib.sha256((self.skill / "SKILL.md").read_bytes()).hexdigest()
        with zipfile.ZipFile(self.pkg) as zf:
            packed_hash = hashlib.sha256(
                zf.read("agent-sdlc-workflow/SKILL.md")
            ).hexdigest()
        self.assertEqual(source_hash, packed_hash)

    def test_check_detects_source_tampering(self) -> None:
        self.assertEqual(self.build().returncode, 0)
        self.assertEqual(self.check().returncode, 0)
        skill_md = self.skill / "SKILL.md"
        skill_md.write_text(skill_md.read_text(encoding="utf-8") + "\n# tamper\n", encoding="utf-8")
        self.assertNotEqual(self.check().returncode, 0)

    def test_missing_required_fails_build(self) -> None:
        (self.skill / "VERSION").unlink()
        result = self.build()
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
