# Failed Thread Archive Repair

Use this fallback only when a user supplies a specific thread ID and the supported Codex archive operation fails while the thread still appears in the active list.

## Eligibility

All of these conditions must hold:

- The target is not the current thread.
- The target has `thread_source = user`. Automation and subagent threads must use their owning workflows.
- The top-level active `state_*.sqlite` contains exactly one matching `threads` row with `archived = 0`.
- The row's rollout file exists below `~/.codex/sessions`.
- The archived destination is absent or has the same size and SHA-256 as the source.
- The user authorized repair after the supported archive method failed.

Do not use archive repair when the rollout is missing, the target exists only in a legacy DB, multiple current DBs contain the target, the thread is already archived inconsistently, or the target path escapes the Codex session directories. Diagnose those as separate cleanup or migration cases.

## Supported Method First

1. Resolve the target with the app thread list and confirm it is active.
2. Call the available Codex archive method, such as `set_thread_archived` with `archived: true`.
3. Re-list active and archived threads.
4. Continue to the helper only if the supported call fails or leaves a proven orphan.

An error such as `os error 2` is not enough by itself: verify the database row and rollout file before repairing anything.

## Helper Workflow

Resolve the helper relative to this skill directory. Run the read-only pass first:

```powershell
python scripts/repair_thread_archive.py <target-thread-id> `
  --current-thread-id <current-thread-id> `
  --workspace <current-workspace>
```

Review the selected database, source, destination, size, hash, and extended-path decision. Apply only to the confirmed target:

```powershell
python scripts/repair_thread_archive.py <target-thread-id> `
  --current-thread-id <current-thread-id> `
  --workspace <current-workspace> `
  --apply
```

The helper:

1. Refuses the current thread and ambiguous or unsupported state databases.
2. Normalizes a legacy Windows `\\?\` prefix for filesystem access while preserving the stored path style in SQLite.
3. Creates a timestamped backup under `<workspace>/work/` using `sqlite3.Connection.backup` and copies the target rollout plus relevant metadata.
4. Copies and hashes the rollout in `archived_sessions` before changing SQLite.
5. Updates only the target `threads` row: `rollout_path`, `archived`, and `archived_at`.
6. Removes the original active rollout only after the database commit and archive-copy verification.
7. Writes a post-repair manifest and runs `PRAGMA integrity_check`.

It intentionally leaves `.codex-global-state.json`, `.bak`, `session_index.jsonl`, logs, goals, memories, project assignments, and derived catalogs unchanged. Normal archiving is not thread deletion.

## Verification

After a successful helper result:

- Confirm the target is absent from the active app thread list.
- Confirm it appears exactly once in the archived thread list.
- Read recent turns from the archived thread to prove the conversation is intact.
- Confirm no target rollout remains below `sessions` and exactly one matching rollout exists below `archived_sessions`.
- Confirm the active state DB row has `archived = 1`, a non-null `archived_at`, and the archived rollout path.
- Confirm `PRAGMA integrity_check` returns `ok`.
- Report the backup directory and size. Archive repair moves data and normally reclaims no space.

If the app list is correct but the visible sidebar is stale, ask the user to refresh, collapse and expand the project, or restart Codex Desktop. Do not edit unrelated UI cache entries merely to force a repaint.
