import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path


TARGET = "11111111-1111-4111-8111-111111111111"
CURRENT = "22222222-2222-4222-8222-222222222222"
SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "codex-local-cleanup"
    / "scripts"
    / "repair_thread_archive.py"
)
EXTENDED_PREFIX = chr(92) * 2 + "?" + chr(92)


class RepairThreadArchiveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.codex_home = self.root / ".codex"
        self.workspace = self.root / "workspace"
        self.sessions = self.codex_home / "sessions" / "2026" / "08" / "19"
        self.archived = self.codex_home / "archived_sessions"
        self.sessions.mkdir(parents=True)
        self.archived.mkdir(parents=True)
        self.workspace.mkdir()
        self.rollout = self.sessions / f"rollout-2026-08-19-{TARGET}.jsonl"
        self.rollout.write_bytes(b'{"type":"session_meta"}\r\n')
        self.database = self.codex_home / "state_5.sqlite"
        with closing(sqlite3.connect(self.database)) as connection:
            connection.execute(
                "create table threads ("
                "id text primary key, rollout_path text not null, "
                "archived integer not null, archived_at integer, "
                "thread_source text not null)"
            )
            connection.execute(
                "insert into threads values (?, ?, 0, null, 'user')",
                (TARGET, EXTENDED_PREFIX + str(self.rollout)),
            )
            connection.commit()
        (self.codex_home / ".codex-global-state.json").write_bytes(b"{}\r\n")
        (self.codex_home / "session_index.jsonl").write_bytes(
            (json.dumps({"id": TARGET}) + "\r\n").encode("utf-8")
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_script(self, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                TARGET,
                "--codex-home",
                str(self.codex_home),
                "--workspace",
                str(self.workspace),
                *extra,
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_dry_run_is_read_only(self) -> None:
        result = self.run_script("--current-thread-id", CURRENT)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "dry_run")
        self.assertTrue(payload["would_preserve_extended_prefix"])
        self.assertTrue(self.rollout.exists())
        self.assertFalse((self.workspace / "work").exists())
        with closing(sqlite3.connect(self.database)) as connection:
            self.assertEqual(
                connection.execute(
                    "select archived from threads where id=?", (TARGET,)
                ).fetchone()[0],
                0,
            )

    def test_apply_archives_and_backs_up_without_rewriting_global_state(self) -> None:
        global_before = (self.codex_home / ".codex-global-state.json").read_bytes()
        index_before = (self.codex_home / "session_index.jsonl").read_bytes()
        result = self.run_script("--current-thread-id", CURRENT, "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        destination = Path(payload["archive_path"])
        backup = Path(payload["backup_directory"])
        self.assertEqual(payload["status"], "archived")
        self.assertFalse(self.rollout.exists())
        self.assertEqual(destination.read_bytes(), b'{"type":"session_meta"}\r\n')
        self.assertTrue((backup / self.rollout.name).exists())
        self.assertTrue((backup / "state_5.sqlite").exists())
        self.assertIn(b"\r\n", (backup / "post-repair-manifest.json").read_bytes())
        self.assertEqual(
            (self.codex_home / ".codex-global-state.json").read_bytes(), global_before
        )
        self.assertEqual(
            (self.codex_home / "session_index.jsonl").read_bytes(), index_before
        )
        with closing(sqlite3.connect(self.database)) as connection:
            row = connection.execute(
                "select rollout_path, archived, archived_at from threads where id=?",
                (TARGET,),
            ).fetchone()
            stored_path = row[0]
            if os.name == "nt":
                self.assertTrue(stored_path.startswith(EXTENDED_PREFIX))
                stored_path = stored_path[len(EXTENDED_PREFIX) :]
            self.assertEqual(Path(stored_path), destination)
            self.assertEqual(row[1], 1)
            self.assertIsNotNone(row[2])
            self.assertEqual(connection.execute("pragma integrity_check").fetchone()[0], "ok")

    def test_apply_refuses_current_thread(self) -> None:
        result = self.run_script("--current-thread-id", TARGET, "--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("current thread", result.stderr)
        self.assertTrue(self.rollout.exists())

    def test_apply_requires_current_thread_id(self) -> None:
        result = self.run_script("--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--current-thread-id is required", result.stderr)
        self.assertTrue(self.rollout.exists())

    def test_accepts_matching_preexisting_archive_copy(self) -> None:
        destination = self.archived / self.rollout.name
        destination.write_bytes(self.rollout.read_bytes())
        result = self.run_script("--current-thread-id", CURRENT, "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "archived")
        self.assertFalse(self.rollout.exists())
        self.assertTrue(destination.exists())

    def test_refuses_mismatched_archive_destination(self) -> None:
        destination = self.archived / self.rollout.name
        destination.write_bytes(b"different\r\n")
        result = self.run_script("--current-thread-id", CURRENT, "--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("different size", result.stderr)
        self.assertTrue(self.rollout.exists())

    def test_refuses_ambiguous_state_databases(self) -> None:
        shutil.copy2(self.database, self.codex_home / "state_4.sqlite")
        result = self.run_script("--current-thread-id", CURRENT)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("multiple top-level state databases", result.stderr)
        self.assertTrue(self.rollout.exists())

    def test_refuses_rollout_outside_sessions(self) -> None:
        outside = self.codex_home / f"rollout-{TARGET}.jsonl"
        outside.write_bytes(b"outside\r\n")
        with closing(sqlite3.connect(self.database)) as connection:
            connection.execute(
                "update threads set rollout_path=? where id=?", (str(outside), TARGET)
            )
            connection.commit()
        result = self.run_script("--current-thread-id", CURRENT)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("escaped sessions root", result.stderr)
        self.assertTrue(outside.exists())

    def test_refuses_non_user_thread_source(self) -> None:
        with closing(sqlite3.connect(self.database)) as connection:
            connection.execute(
                "update threads set thread_source='subagent' where id=?", (TARGET,)
            )
            connection.commit()
        result = self.run_script("--current-thread-id", CURRENT)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("thread_source=user", result.stderr)
        self.assertTrue(self.rollout.exists())


if __name__ == "__main__":
    unittest.main()
