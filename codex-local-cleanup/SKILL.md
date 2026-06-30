---
name: codex-local-cleanup
description: Clean local Codex Desktop metadata under $CODEX_HOME or ~/.codex by safely identifying mobile-visible stale projects, non-active project threads outside saved project roots, archived threads, deleted workspace cwd entries, session JSONL files, thread indexes, global state, config trust entries, and SQLite rows; always back up first, keep saved projects/projectless chats/current thread unless explicitly requested, and verify with read-only checks before reporting.
---

# Codex Local Cleanup

Use this skill when the user wants to clean local Codex Desktop remnants in `~/.codex`, such as deleted project traces, stale archived threads, old project trust entries, or mobile-visible sidebar clutter.

## Safety Rules

- Treat `~/.codex` as live application state. Do not modify it until the target set is explicit and backed up.
- Never delete or rewrite `auth.json`, `installation_id`, `skills/`, `plugins/`, `automations/`, `.sandbox-secrets/`, or user source projects.
- Never clean the current active thread, even if its cwd is projectless or outside saved projects.
- Do not remove general chat threads unless the user explicitly asks for them.
- Prefer narrow cleanup scopes:
  - non-projectless project threads outside saved project roots
  - stale archived threads outside saved project roots
  - deleted cwd threads
  - dead `[projects.'...']` trust blocks in `config.toml`
- If a title or preview contains secrets, do not repeat the secret in chat output.
- Before deleting files or DB rows, verify resolved paths stay under `~/.codex/sessions` or `~/.codex/archived_sessions`.

## Data Sources

Use local Codex files only:

- `.codex-global-state.json`: saved project roots, project order, pinned projects, prompt history, thread permissions, `projectless-thread-ids`, `thread-projectless-output-directories`, `thread-workspace-root-hints`, `queued-follow-ups`, and nested `electron-persisted-atom-state` UI caches.
- `state_*.sqlite`: thread metadata, cwd, archived flag, rollout path, `source`, `thread_source`, and agent/subagent fields.
- `logs_*.sqlite`: diagnostic logs.
- `session_index.jsonl`: thread index.
- `sessions/**/rollout-*.jsonl`: active/non-archived conversation files.
- `archived_sessions/rollout-*.jsonl`: archived conversation files.
- `config.toml`: trusted project roots.

If both top-level `.codex/state_*.sqlite` and legacy `.codex/sqlite/state_*.sqlite` exist, compare migration count and modified time first. Prefer the current active DB for normal cleanup. If mobile still shows entries that are absent from the active DB, inspect legacy `.codex/sqlite/state_*.sqlite` and `.codex/sqlite/logs_*.sqlite` as an additional mobile-visible stale source before reporting that cleanup is complete.

## Classification

Saved project roots come from `.codex-global-state.json` key `electron-saved-workspace-roots`.

Maintain by default:

- Threads whose `cwd` equals or is under a saved project root.
- The current thread.
- Saved project roots listed in `electron-saved-workspace-roots`, `project-order`, `pinned-project-ids`, or `electron-workspace-root-labels`. If Desktop shows a renamed project but mobile shows the raw folder name, treat that as a label/display-sync issue, not stale metadata.
- Projectless/general chat threads unless the user explicitly asks to remove them.
- Threads listed in `projectless-thread-ids`, `thread-projectless-output-directories`, or `thread-workspace-root-hints` unless the user explicitly asks to remove projectless/general chat state.
- Subagent threads whose `thread_source` is `subagent`, unless their parent thread is also being removed and the user explicitly included spawned agent state.
- Archived threads under saved project roots unless the user asks to prune those archives too.

Cleanup candidates:

- Non-projectless, non-subagent threads whose `cwd` is outside saved project roots, when the user asks to keep only current saved/active projects.
- Threads with `cwd` paths that do not exist.
- Archived threads whose `cwd` is outside saved project roots, excluding projectless/general chat markers unless the user asked to prune those too.
- Legacy `.codex/sqlite/state_*.sqlite` rows that match the same cleanup criteria when mobile still shows entries already removed from the active top-level DB.
- `config.toml` `[projects.'...']` blocks for paths that do not exist.
- `config.toml` `[projects.'...']` blocks outside saved project roots, when cleaning non-active projects. Preserve current projectless workspace trust entries unless explicitly asked to remove general chat state.

For Windows paths, normalize `\\?\` prefixes, slash direction, trailing slashes, and case before comparing paths. Do not rely on `os.path.commonpath` alone if path forms are mixed; compare normalized strings with `root == cwd or cwd.startswith(root + "\\")`.

## Workflow

1. Read `.codex-global-state.json` and `state_*.sqlite` in read-only mode.
2. Print a concise candidate summary: count, cwd, archived count, whether each path exists, and whether it is under a saved project root.
3. Confirm the cleanup scope from the user's instruction. If the user says "active/saved projects only", target non-projectless, non-subagent threads outside `electron-saved-workspace-roots` while preserving projectless chats, generated Codex workspaces, and the current thread.
4. Create a timestamped backup under the current workspace `work/` directory:
   - target list JSON
   - consistent SQLite backups using `sqlite3.Connection.backup`
   - raw copies of `.codex-global-state.json`, `.bak`, `session_index.jsonl`, and `config.toml`
   - target rollout JSONL files
   - pre-cleanup size manifest for target rollout files, metadata files, and modified SQLite DB files
5. Remove only validated target rollout files.
6. Remove matching `session_index.jsonl` lines.
7. Remove matching prompt-history, thread-permission, unread-thread, thread-client-id, projectless, workspace-hint, and follow-up keys from `.codex-global-state.json` and `.bak`.
8. Delete target rows from active `state_*.sqlite` tables, and legacy `.codex/sqlite/state_*.sqlite` tables when included, in dependency order:
   - `thread_dynamic_tools`
   - `thread_spawn_edges`
   - `agent_job_items`
   - `threads`
9. Delete matching active and included legacy `logs_*.sqlite` rows by `thread_id`. Avoid broad text deletes that would erase the current cleanup thread's diagnostic logs unless the user explicitly asks.
10. For `config.toml`, remove only the selected `[projects.'...']` blocks and their body lines.
11. Run SQLite checkpoint/VACUUM after writes when practical.
12. Record post-cleanup sizes for modified files and DBs.
13. Verify before reporting success.

## Verification

Run checks that directly prove the result:

- `PRAGMA integrity_check` for modified SQLite DBs.
- Target thread IDs no longer exist in `state_*.sqlite`.
- Target rollout files no longer exist.
- Target IDs no longer appear in `session_index.jsonl`.
- Target IDs no longer appear in `.codex-global-state.json` or `.bak`, except when the current conversation naturally mentions them and that scope was intentionally preserved. Check nested `electron-persisted-atom-state` keys such as heartbeat permissions, unread thread IDs, and thread client IDs.
- Archived-outside-active count is zero when cleaning outside-project archives.
- Outside-active non-projectless thread count is zero when cleaning mobile-visible non-active projects.
- `config.toml` outside-active non-projectless trust block count is zero when cleaning non-active projects.
- Dead `config.toml` project blocks are zero when cleaning missing trust entries.
- `codex_app.list_threads` searches for removed titles or paths return no removed target threads when the app tool is available.

## Size Accounting

Report cleanup size conservatively:

- Directly reclaimed bytes: sum of deleted rollout JSONL files and other deleted files that no longer exist after cleanup.
- SQLite reclaimed bytes: report DB file size delta before/after only when measured. If rows were deleted but the DB file did not shrink because pages/WAL are reused, report the deleted row counts separately instead of claiming reclaimed bytes.
- Backup size: total bytes written under the backup directory.
- Net disk change: direct reclaimed bytes minus backup size, when both are known. Make clear that backups intentionally increase disk usage until the user deletes them.
- Human-readable units: include bytes and KiB/MiB for non-trivial values.

## Reporting

Report in Korean unless the user asks otherwise. Include:

- cleanup scope used
- number of threads removed
- files/DBs touched
- backup directory
- directly reclaimed size, backup size, and DB row/file-size notes
- verification results
- any known residual traces, especially current-thread diagnostic logs that were intentionally preserved

Keep the final answer concise and avoid exposing secrets from historical titles or previews.
