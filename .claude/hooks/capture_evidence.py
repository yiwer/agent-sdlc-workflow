#!/usr/bin/env python3
"""Agent SDLC evidence capture hook (claude-code binding, A1 tool-captured).

Invoked as a PostToolUse hook on Bash. Reads the hook JSON payload from stdin,
and — only for verification-like commands (test/build/lint/typecheck/e2e) —
appends one revision-bound evidence record to ``plans/logs/evidence.jsonl``.

Design contract:
- Best-effort and NON-BLOCKING: it always exits 0 and swallows its own errors,
  so a failure here can never interrupt the session.
- Machine-authored: the record is written by this hook (captured_by), not by
  the model, which is what makes it A1 rather than A0 (RULE-EVD-002).
- Revision-bound: it records git HEAD and a dirty-diff hash so stale evidence
  can be detected later (RULE-EVD-003).
- It does NOT upgrade assurance: a command run locally by the agent is A1 at
  best, never A2/A3. Independent replay / external enforcement are separate.

The project root is resolved from this file's location, so the hook works
regardless of the shell or current working directory.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_LOG = PROJECT_ROOT / "plans" / "logs" / "evidence.jsonl"
CAPTURED_BY = "claude-code:PostToolUse"

# Verification-like commands worth recording as evidence.
VERIFY_RE = re.compile(
    r"(pytest|unittest|nose2|tox|"
    r"npm\s+(run\s+)?(test|build|lint|typecheck|e2e|check)|"
    r"pnpm\s+(run\s+)?(test|build|lint|check)|"
    r"yarn\s+(run\s+)?(test|build|lint|check)|"
    r"npx\s+(tsc|playwright|jest|vitest|eslint|prettier|mocha|cypress)|"
    r"playwright|jest|vitest|mocha|cypress|"
    r"cargo\s+(test|build|clippy)|go\s+(test|build|vet)|"
    r"mvn|gradle|phpunit|rspec|bundle\s+exec\s+(rspec|rake)|"
    r"\bmake(\s|$)|\btsc\b|eslint|mypy|\bruff\b|black\s+--check)",
    re.IGNORECASE,
)


def _run_git(*args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", *args],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return out.stdout


def _revision() -> str | None:
    out = _run_git("rev-parse", "HEAD")
    return out.strip() if out else None


def _dirty_diff_hash() -> str | None:
    out = _run_git("status", "--porcelain")
    if out is None:
        return None
    if out.strip() == "":
        return None  # clean tree
    return hashlib.sha256(out.encode("utf-8")).hexdigest()


def _extract_exit_code(response: dict) -> int | None:
    for key in ("exitCode", "exit_code", "returncode", "code", "status"):
        value = response.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.lstrip("-").isdigit():
            return int(value)
    return None


def _output_summary(response: dict) -> str:
    parts = []
    for key in ("stdout", "stderr", "output"):
        value = response.get(key)
        if isinstance(value, str) and value.strip():
            parts.append(value.strip())
    text = "\n".join(parts)
    return text[-800:] if len(text) > 800 else text


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except (ValueError, OSError):
        return 0

    try:
        if payload.get("tool_name") != "Bash":
            return 0
        command = (payload.get("tool_input") or {}).get("command")
        if not isinstance(command, str) or not VERIFY_RE.search(command):
            return 0  # not a verification command; record nothing

        response = payload.get("tool_response") or {}
        if not isinstance(response, dict):
            response = {}

        exit_code = _extract_exit_code(response)
        if exit_code == 0:
            result = "passed"
        elif exit_code is None:
            result = "unknown"
        else:
            result = "failed"

        revision = _revision()
        record = {
            "captured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "gate_type": "evidence",
            "assurance": "A1",
            "provenance": "tool-captured",
            "captured_by": CAPTURED_BY,
            "session_id": payload.get("session_id"),
            "source": command[:500],
            "revision": revision,
            "dirty_diff_hash": _dirty_diff_hash(),
            "exit_code": exit_code,
            "result": result,
            "freshness": "exact_revision" if revision else "unbound",
            "output_summary": _output_summary(response),
        }

        EVIDENCE_LOG.parent.mkdir(parents=True, exist_ok=True)
        with EVIDENCE_LOG.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        # Best-effort: never let evidence capture break the session.
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
