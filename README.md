# Codex Local Cleanup Skill

`codex-local-cleanup` is a Codex skill for safely cleaning stale Codex Desktop project and thread metadata and repairing a specific active thread that the supported archive action cannot move.

It is intended for cases where old project entries, archived threads, deleted workspace paths, or mobile-visible sidebar clutter remain after projects were removed or reorganized.

The goal is for the mobile-visible project list to match the active local projects shown in Codex Desktop.

Current release: [v0.3.0](https://github.com/cku3987/codex-local-cleanup-skill/releases/tag/v0.3.0)

![Codex Local Cleanup flow](assets/codex-local-cleanup-flow.svg)

## Translations

- [한국어](docs/README.ko.md)
- [日本語](docs/README.ja.md)
- [简体中文](docs/README.zh-CN.md)
- [繁體中文](docs/README.zh-TW.md)
- [Русский](docs/README.ru.md)
- [Español](docs/README.es.md)
- [Français](docs/README.fr.md)
- [Deutsch](docs/README.de.md)

## What It Does

- Reads current project definitions from `local-projects` and thread mappings from `thread-project-assignments`.
- Supports multi-folder projects through each project's `rootPaths`; legacy saved roots are fallback data only.
- Keeps active projects, projectless chats, automation threads, generated workspaces, and the current thread by default.
- Uses the supported Codex App Server `thread/delete` lifecycle before direct JSONL or SQLite repair.
- Retries the supported archive action first, then offers a thread-ID-based repair helper for a verified non-current thread whose rollout still exists.
- Runs archive repair as a read-only dry run by default, backs up before `--apply`, preserves legacy Windows `\\?\` path style in SQLite, and verifies the archived conversation afterward.
- Treats `.codex/sqlite/codex-dev.db` as a derived Desktop catalog to verify after reconciliation, not the primary deletion source.
- Treats `session_index.jsonl` and legacy `.codex/sqlite/state_*.sqlite` as compatibility sources rather than authoritative inventories.
- Treats renamed projects as display-label sync issues, not stale deletion targets.
- Finds dangling project assignments and non-active project threads outside current project roots.
- Finds deleted `cwd` entries and stale archived threads.
- Backs up affected metadata before changing anything.
- Separates visibility cleanup, archive cleanup, storage cleanup, and last-resort repair.
- Cleans confirmed project state, assignments, session metadata, trust entries, and residual SQLite rows only within the selected scope.
- Verifies SQLite integrity and checks that removed targets no longer appear.

## Installation

Recommended: ask Codex to install this repository path with the built-in `skill-installer` skill:

```text
$skill-installer Install the skill from https://github.com/cku3987/codex-local-cleanup-skill/tree/main/codex-local-cleanup
```

Manual install: copy the skill folder into your Codex skills directory:

```powershell
Copy-Item -Recurse .\codex-local-cleanup "$env:USERPROFILE\.codex\skills\codex-local-cleanup"
```

Restart Codex Desktop after installation if the skill does not appear immediately.

## Example Prompts

```text
$codex-local-cleanup Keep my active local projects and projectless chats, then back up and clean non-active project metadata from local Codex.
```

```text
$codex-local-cleanup Find deleted cwd threads in my local Codex metadata, back them up, remove only those stale entries, and verify the result.
```

```text
$codex-local-cleanup Clean project traces outside my active local projects, but do not delete archived sessions or diagnostic logs.
```

```text
$codex-local-cleanup Thread 01a00000-0000-0000-0000-000000000000 still appears after archive failed. Diagnose it read-only, then back up and repair only that thread if it is safe.
```

## Safety Notes

This skill works with local Codex Desktop state. It should always back up before modifying metadata.

Important risk and permission notes:

- This is local application-state cleanup, not source-code cleanup.
- It can delete Codex thread metadata, session JSONL files, sidebar indexes, trust entries, and SQLite rows for selected targets.
- It prefers the Desktop **Remove** action and the supported App Server thread lifecycle before direct metadata repair.
- Archive repair is not deletion: it moves one verified rollout into `archived_sessions` and updates only that thread's archive fields after a backup and hash check.
- Visibility cleanup does not imply archive deletion, log cleanup, backup deletion, or database compaction.
- In full-access or no-approval environments, Codex may be able to write immediately. Ask for a read-only inventory first if you are unsure.
- Do not run broad cleanup from a vague prompt. Review the target list, backup path, and preservation rules before allowing writes.
- Backups may contain local paths, thread titles, prompts, and conversation content. Keep backups private.

It should not delete or rewrite:

- `auth.json`
- `installation_id`
- `skills/`
- `plugins/`
- `automations/`
- `.sandbox-secrets/`
- user source projects

The skill is intentionally conservative. It preserves current local projects, projectless chats, and the current thread unless explicitly instructed otherwise. It also refuses to remove unknown tombstone-like state without proving its purpose.

## Repository Layout

```text
codex-local-cleanup-skill/
├─ README.md
├─ LICENSE
├─ .gitignore
├─ tests/
│  └─ test_repair_thread_archive.py
└─ codex-local-cleanup/
   ├─ SKILL.md
   ├─ references/
   │  └─ archive-repair.md
   ├─ scripts/
   │  └─ repair_thread_archive.py
   └─ agents/
      └─ openai.yaml
```

## License

MIT
