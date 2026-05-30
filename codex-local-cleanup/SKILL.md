---
name: codex-local-cleanup
description: Clean local Codex Desktop metadata under $CODEX_HOME or ~/.codex by safely identifying mobile-visible stale projects, non-active project threads outside saved project roots, archived threads, deleted workspace cwd entries, session JSONL files, thread indexes, global state, config trust entries, and SQLite rows; always back up first, keep saved projects/projectless chats/current thread unless explicitly requested, and verify with read-only checks before reporting.
---

# Codex Local Cleanup

Use this skill when the user wants to clean local Codex Desktop remnants in `~/.codex`, such as deleted project traces, stale archived threads, old project trust entries, or mobile-visible sidebar clutter.

## Safety Rules

- Treat `~/.codex` as live application state. Do not modify it until the target set is explicit and backed up.
- Treat full-access, no-approval, or danger-level tool permissions as implementation capability, not user consent. If the cleanup scope is ambiguous, stop after read-only inventory and ask for confirmation before writes.
- Never delete or rewrite `auth.json`, `installation_id`, `skills/`, `plugins/`, `automations/`, `.sandbox-secrets/`, or user source projects.
- Never clean the current active thread, even if its cwd is projectless or outside saved projects.
- Do not remove general chat threads unless the user explicitly asks for them.
- Tell the user that backups may contain local paths, thread titles, prompts, and conversation content; do not print sensitive backup contents.
- Prefer narrow cleanup scopes:
  - non-projectless project threads outside saved project roots
  - stale archived threads outside saved project roots
  - deleted cwd threads
  - dead `[projects.'...']` trust blocks in `config.toml`
- If a title or preview contains secrets, do not repeat the secret in chat output.
- Before deleting files or DB rows, verify resolved paths stay under `~/.codex/sessions` or `~/.codex/archived_sessions`.

## Data Sources

Use local Codex files only:

- `.codex-global-state.json`: saved project roots, project order, pinned projects, prompt history, thread permissions.
- `state_*.sqlite`: thread metadata, cwd, archived flag, rollout path.
- `logs_*.sqlite`: diagnostic logs.
- `session_index.jsonl`: thread index.
- `sessions/**/rollout-*.jsonl`: active/non-archived conversation files.
- `archived_sessions/rollout-*.jsonl`: archived conversation files.
- `config.toml`: trusted project roots.

## Classification

Saved project roots come from `.codex-global-state.json` key `electron-saved-workspace-roots`.

Maintain by default:

- Threads whose `cwd` equals or is under a saved project root.
- The current thread.
- Projectless/general chat threads unless the user explicitly asks to remove them.
- Archived threads under saved project roots unless the user asks to prune those archives too.

Cleanup candidates:

- Non-projectless threads whose `cwd` is outside saved project roots, when the user asks to keep only current saved/active projects.
- Threads with `cwd` paths that do not exist.
- Archived threads whose `cwd` is outside saved project roots.
- `config.toml` `[projects.'...']` blocks for paths that do not exist.
- `config.toml` `[projects.'...']` blocks outside saved project roots, when cleaning non-active projects. Preserve current projectless workspace trust entries unless explicitly asked to remove general chat state.

For Windows paths, normalize `\\?\` prefixes, slash direction, trailing slashes, and case before comparing paths. Do not rely on `os.path.commonpath` alone if path forms are mixed; compare normalized strings with `root == cwd or cwd.startswith(root + "\\")`.

## Workflow

1. Read `.codex-global-state.json` and `state_*.sqlite` in read-only mode.
2. Print a concise candidate summary: count, cwd, archived count, whether each path exists, and whether it is under a saved project root.
3. Confirm the cleanup scope from the user's instruction. If the user says "active/saved projects only", target non-projectless threads outside `electron-saved-workspace-roots` while preserving projectless chats and the current thread.
4. Create a timestamped backup under the current workspace `work/` directory:
   - target list JSON
   - consistent SQLite backups using `sqlite3.Connection.backup`
   - raw copies of `.codex-global-state.json`, `.bak`, `session_index.jsonl`, and `config.toml`
   - target rollout JSONL files
5. Remove only validated target rollout files.
6. Remove matching `session_index.jsonl` lines.
7. Remove matching prompt-history and thread-permission keys from `.codex-global-state.json` and `.bak`.
8. Delete target rows from `state_*.sqlite` tables in dependency order:
   - `thread_dynamic_tools`
   - `thread_spawn_edges`
   - `agent_job_items`
   - `threads`
9. Delete matching `logs_*.sqlite` rows by `thread_id`. Avoid broad text deletes that would erase the current cleanup thread's diagnostic logs unless the user explicitly asks.
10. For `config.toml`, remove only the selected `[projects.'...']` blocks and their body lines.
11. Run SQLite checkpoint/VACUUM after writes when practical.
12. Verify before reporting success.

## Verification

Run checks that directly prove the result:

- `PRAGMA integrity_check` for modified SQLite DBs.
- Target thread IDs no longer exist in `state_*.sqlite`.
- Target rollout files no longer exist.
- Target IDs no longer appear in `session_index.jsonl`.
- Target IDs no longer appear in `.codex-global-state.json` or `.bak`, except when the current conversation naturally mentions them and that scope was intentionally preserved.
- Archived-outside-active count is zero when cleaning outside-project archives.
- Outside-active non-projectless thread count is zero when cleaning mobile-visible non-active projects.
- `config.toml` outside-active non-projectless trust block count is zero when cleaning non-active projects.
- Dead `config.toml` project blocks are zero when cleaning missing trust entries.
- `codex_app.list_threads` searches for removed titles or paths return no removed target threads when the app tool is available.

## Reporting

Report in Korean unless the user asks otherwise. Include:

- cleanup scope used
- number of threads removed
- files/DBs touched
- backup directory
- verification results
- any known residual traces, especially current-thread diagnostic logs that were intentionally preserved

Keep the final answer concise and avoid exposing secrets from historical titles or previews.
