#!/usr/bin/env python3
"""Repair one Codex thread whose supported archive operation failed."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence


THREAD_ID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
EXTENDED_PATH_PREFIX = chr(92) * 2 + "?" + chr(92)
EXTENDED_UNC_PREFIX = EXTENDED_PATH_PREFIX + "UNC" + chr(92)
REQUIRED_THREAD_COLUMNS = {
    "id",
    "rollout_path",
    "archived",
    "archived_at",
    "thread_source",
}


class ArchiveRepairError(RuntimeError):
    """A safety or consistency check prevented the repair."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, value: Any) -> None:
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))


def _filesystem_path(stored_path: str) -> Path:
    if stored_path.startswith(EXTENDED_UNC_PREFIX):
        stored_path = chr(92) * 2 + stored_path[len(EXTENDED_UNC_PREFIX) :]
    elif stored_path.startswith(EXTENDED_PATH_PREFIX):
        stored_path = stored_path[len(EXTENDED_PATH_PREFIX) :]
    return Path(stored_path)


def _stored_path(path: Path, preserve_extended_prefix: bool) -> str:
    value = str(path)
    if preserve_extended_prefix and os.name == "nt":
        return EXTENDED_PATH_PREFIX + value
    return value


def _is_below(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _readonly_connection(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def _thread_row(database: Path, thread_id: str) -> dict[str, Any] | None:
    connection = _readonly_connection(database)
    try:
        table = connection.execute(
            "select 1 from sqlite_master where type='table' and name='threads'"
        ).fetchone()
        if table is None:
            return None
        columns = {
            row[1] for row in connection.execute('pragma table_info("threads")')
        }
        if "id" not in columns:
            return None
        exists = connection.execute(
            "select 1 from threads where id=?", (thread_id,)
        ).fetchone()
        if exists is None:
            return None
        if not REQUIRED_THREAD_COLUMNS.issubset(columns):
            missing = sorted(REQUIRED_THREAD_COLUMNS - columns)
            raise ArchiveRepairError(
                f"Unsupported threads schema in {database}: missing {missing}"
            )
        row = connection.execute(
            "select id, rollout_path, archived, archived_at, thread_source "
            "from threads where id=?",
            (thread_id,),
        ).fetchone()
        return dict(row) if row is not None else None
    finally:
        connection.close()


def _select_database(
    codex_home: Path, thread_id: str, requested_database: Path | None
) -> tuple[Path, dict[str, Any]]:
    if requested_database is not None:
        database = requested_database.resolve(strict=True)
        if database.parent != codex_home or not database.match("state_*.sqlite"):
            raise ArchiveRepairError(
                "--state-db must name a top-level state_*.sqlite file under CODEX_HOME"
            )
        row = _thread_row(database, thread_id)
        if row is None:
            raise ArchiveRepairError(f"Thread {thread_id} is absent from {database}")
        return database, row

    matches: list[tuple[Path, dict[str, Any]]] = []
    for database in sorted(
        codex_home.glob("state_*.sqlite"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    ):
        row = _thread_row(database, thread_id)
        if row is not None:
            matches.append((database.resolve(), row))

    if not matches:
        raise ArchiveRepairError(
            f"Thread {thread_id} is absent from top-level state_*.sqlite databases"
        )
    if len(matches) != 1:
        databases = ", ".join(str(item[0]) for item in matches)
        raise ArchiveRepairError(
            "Thread exists in multiple top-level state databases; inspect migrations "
            f"and pass --state-db explicitly: {databases}"
        )
    return matches[0]


def _validate_plan(
    codex_home: Path,
    database: Path,
    row: dict[str, Any],
    thread_id: str,
) -> dict[str, Any]:
    if row["thread_source"] != "user":
        raise ArchiveRepairError(
            "Archive repair helper accepts only thread_source=user; handle other "
            "thread sources through their owning workflow"
        )
    if int(row["archived"]) != 0:
        existing = _filesystem_path(str(row["rollout_path"])).resolve(strict=False)
        archive_root = (codex_home / "archived_sessions").resolve(strict=False)
        if existing.exists() and _is_below(existing, archive_root):
            return {
                "status": "already_archived",
                "thread_id": thread_id,
                "database": str(database),
                "archive_path": str(existing),
            }
        raise ArchiveRepairError(
            "Database marks the thread archived, but its archived rollout is inconsistent"
        )

    sessions_root = (codex_home / "sessions").resolve(strict=True)
    archive_root = (codex_home / "archived_sessions").resolve(strict=False)
    stored_source = str(row["rollout_path"])
    source = _filesystem_path(stored_source)
    if not source.is_absolute():
        raise ArchiveRepairError(f"Rollout path is not absolute: {stored_source}")
    source = source.resolve(strict=True)
    if not _is_below(source, sessions_root):
        raise ArchiveRepairError(f"Rollout escaped sessions root: {source}")
    if thread_id.lower() not in source.name.lower():
        raise ArchiveRepairError("Rollout filename does not contain the target thread ID")

    destination = (archive_root / source.name).resolve(strict=False)
    if destination.parent != archive_root:
        raise ArchiveRepairError("Archive destination escaped archived_sessions")

    source_hash = _sha256(source)
    if destination.exists():
        if not destination.is_file():
            raise ArchiveRepairError(f"Archive destination is not a file: {destination}")
        if destination.stat().st_size != source.stat().st_size:
            raise ArchiveRepairError("Existing archive destination has a different size")
        if _sha256(destination) != source_hash:
            raise ArchiveRepairError("Existing archive destination has a different hash")

    return {
        "status": "ready",
        "thread_id": thread_id,
        "database": database,
        "source": source,
        "stored_source": stored_source,
        "destination": destination,
        "source_size": source.stat().st_size,
        "source_sha256": source_hash,
        "preserve_extended_prefix": stored_source.startswith(EXTENDED_PATH_PREFIX),
        "destination_preexisted": destination.exists(),
    }


def _backup(
    codex_home: Path,
    workspace: Path,
    plan: dict[str, Any],
    current_thread_id: str,
) -> tuple[Path, int]:
    if (
        plan["source"].stat().st_size != plan["source_size"]
        or _sha256(plan["source"]) != plan["source_sha256"]
    ):
        raise ArchiveRepairError("Source rollout changed before backup")
    work_root = (workspace / "work").resolve()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = (
        work_root
        / f"codex-local-cleanup-{stamp}-archive-repair-{plan['thread_id'][:8]}"
    ).resolve()
    if backup.parent != work_root:
        raise ArchiveRepairError("Backup path escaped the workspace work directory")
    backup.mkdir(parents=True, exist_ok=False)

    manifest: dict[str, Any] = {
        "created_at": datetime.now().astimezone().isoformat(),
        "operation": "thread archive repair",
        "target_thread_id": plan["thread_id"],
        "current_thread_id_excluded": current_thread_id,
        "files": [],
    }
    for source in (
        codex_home / ".codex-global-state.json",
        codex_home / ".codex-global-state.json.bak",
        codex_home / "session_index.jsonl",
        codex_home / "config.toml",
    ):
        if source.exists():
            destination = backup / source.name
            shutil.copy2(source, destination)
            manifest["files"].append(
                {
                    "source": str(source),
                    "backup": str(destination),
                    "size": source.stat().st_size,
                    "sha256": _sha256(source),
                }
            )

    rollout_backup = backup / plan["source"].name
    shutil.copy2(plan["source"], rollout_backup)
    if _sha256(rollout_backup) != plan["source_sha256"]:
        raise ArchiveRepairError("Rollout backup hash verification failed")
    manifest["files"].append(
        {
            "source": str(plan["source"]),
            "backup": str(rollout_backup),
            "size": plan["source_size"],
            "sha256": plan["source_sha256"],
        }
    )

    database_backup = backup / plan["database"].name
    source_connection = _readonly_connection(plan["database"])
    backup_connection = sqlite3.connect(str(database_backup))
    try:
        source_connection.backup(backup_connection)
        integrity = backup_connection.execute("pragma integrity_check").fetchone()[0]
        if integrity != "ok":
            raise ArchiveRepairError(
                f"Backup database integrity check failed: {integrity}"
            )
    finally:
        backup_connection.close()
        source_connection.close()
    manifest["files"].append(
        {
            "source": str(plan["database"]),
            "backup": str(database_backup),
            "size": plan["database"].stat().st_size,
            "backup_size": database_backup.stat().st_size,
            "sha256": _sha256(database_backup),
            "integrity_check": "ok",
        }
    )

    target_manifest = {
        "target_thread_id": plan["thread_id"],
        "current_thread_id_excluded": current_thread_id,
        "database": str(plan["database"]),
        "source_rollout": str(plan["source"]),
        "archive_rollout": str(plan["destination"]),
        "source_size": plan["source_size"],
        "source_sha256": plan["source_sha256"],
    }
    _write_json(backup / "target-list.json", target_manifest)
    _write_json(backup / "pre-repair-manifest.json", manifest)
    backup_size = sum(item.stat().st_size for item in backup.iterdir() if item.is_file())
    return backup, backup_size


def _update_database(plan: dict[str, Any]) -> str:
    stored_destination = _stored_path(
        plan["destination"], bool(plan["preserve_extended_prefix"])
    )
    connection = sqlite3.connect(str(plan["database"]), timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("pragma busy_timeout=10000")
        connection.execute("begin immediate")
        current = connection.execute(
            "select rollout_path, archived from threads where id=?",
            (plan["thread_id"],),
        ).fetchone()
        if (
            current is None
            or int(current["archived"]) != 0
            or current["rollout_path"] != plan["stored_source"]
        ):
            raise ArchiveRepairError("Thread state changed after the repair plan was built")
        cursor = connection.execute(
            "update threads set rollout_path=?, archived=1, archived_at=? "
            "where id=? and archived=0",
            (stored_destination, int(time.time()), plan["thread_id"]),
        )
        if cursor.rowcount != 1:
            raise ArchiveRepairError(
                f"Expected one updated thread row, got {cursor.rowcount}"
            )
        integrity = connection.execute("pragma integrity_check").fetchone()[0]
        if integrity != "ok":
            raise ArchiveRepairError(f"Database integrity check failed: {integrity}")
        connection.commit()
        return stored_destination
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def repair_archive(
    *,
    thread_id: str,
    current_thread_id: str | None,
    codex_home: Path,
    workspace: Path,
    state_database: Path | None,
    apply: bool,
) -> dict[str, Any]:
    if not THREAD_ID_PATTERN.fullmatch(thread_id):
        raise ArchiveRepairError(f"Invalid thread ID: {thread_id}")
    if current_thread_id is not None and not THREAD_ID_PATTERN.fullmatch(
        current_thread_id
    ):
        raise ArchiveRepairError(f"Invalid current thread ID: {current_thread_id}")
    if current_thread_id == thread_id:
        raise ArchiveRepairError("Refusing to archive the current thread")
    if apply and current_thread_id is None:
        raise ArchiveRepairError("--current-thread-id is required with --apply")

    codex_home = codex_home.expanduser().resolve(strict=True)
    workspace = workspace.expanduser().resolve(strict=True)
    database, row = _select_database(codex_home, thread_id, state_database)
    plan = _validate_plan(codex_home, database, row, thread_id)
    if plan["status"] == "already_archived":
        return plan
    if not apply:
        return {
            "status": "dry_run",
            "thread_id": thread_id,
            "database": str(plan["database"]),
            "source": str(plan["source"]),
            "destination": str(plan["destination"]),
            "source_size": plan["source_size"],
            "source_sha256": plan["source_sha256"],
            "thread_source": "user",
            "destination_preexisted": plan["destination_preexisted"],
            "would_preserve_extended_prefix": plan["preserve_extended_prefix"],
        }

    backup, _ = _backup(
        codex_home, workspace, plan, current_thread_id or ""
    )
    plan["destination"].parent.mkdir(parents=True, exist_ok=True)
    created_destination = False
    if not plan["destination"].exists():
        shutil.copy2(plan["source"], plan["destination"])
        created_destination = True
    if (
        plan["destination"].stat().st_size != plan["source_size"]
        or _sha256(plan["destination"]) != plan["source_sha256"]
    ):
        if created_destination:
            plan["destination"].unlink(missing_ok=True)
        raise ArchiveRepairError("Archive copy verification failed")

    try:
        stored_destination = _update_database(plan)
    except Exception:
        if created_destination:
            plan["destination"].unlink(missing_ok=True)
        raise

    source_removed = False
    try:
        plan["source"].unlink()
        source_removed = not plan["source"].exists()
    finally:
        post_manifest = {
            "completed_at": datetime.now().astimezone().isoformat(),
            "target_thread_id": thread_id,
            "database": str(plan["database"]),
            "database_integrity_check": "ok",
            "stored_archive_path": stored_destination,
            "archive_path": str(plan["destination"]),
            "archive_size": plan["destination"].stat().st_size,
            "archive_sha256": _sha256(plan["destination"]),
            "active_source_removed": source_removed,
        }
        _write_json(backup / "post-repair-manifest.json", post_manifest)
    if not source_removed:
        raise ArchiveRepairError(
            f"Database was updated but the active rollout remains; restore from {backup}"
        )

    backup_size = sum(item.stat().st_size for item in backup.iterdir() if item.is_file())

    return {
        "status": "archived",
        "thread_id": thread_id,
        "database": str(plan["database"]),
        "archive_path": str(plan["destination"]),
        "archive_size": plan["destination"].stat().st_size,
        "archive_sha256": plan["source_sha256"],
        "active_source_removed": True,
        "database_integrity_check": "ok",
        "backup_directory": str(backup),
        "backup_size": backup_size,
    }


def _default_codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured) if configured else Path.home() / ".codex"


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Repair one non-current Codex thread whose supported archive operation "
            "failed. The default mode is read-only."
        )
    )
    parser.add_argument("thread_id", help="Target Codex thread UUID")
    parser.add_argument(
        "--current-thread-id",
        help="Current Codex thread UUID; required with --apply",
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=_default_codex_home(),
        help="Codex state directory (default: CODEX_HOME or ~/.codex)",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="Workspace whose work/ directory receives the backup",
    )
    parser.add_argument(
        "--state-db",
        type=Path,
        help="Explicit top-level state_*.sqlite when more than one contains the ID",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Back up and apply the repair; omission performs a read-only dry run",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        result = repair_archive(
            thread_id=args.thread_id,
            current_thread_id=args.current_thread_id,
            codex_home=args.codex_home,
            workspace=args.workspace,
            state_database=args.state_db,
            apply=args.apply,
        )
    except (ArchiveRepairError, FileNotFoundError, OSError, sqlite3.Error) as error:
        print(
            json.dumps(
                {"status": "error", "error": str(error)}, ensure_ascii=False
            ),
            file=sys.stderr,
        )
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
