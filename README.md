# Codex Local Cleanup Skill

`codex-local-cleanup` is a Codex skill for safely cleaning stale local Codex Desktop metadata under `~/.codex`.

It is intended for cases where old project entries, archived threads, deleted workspace paths, or mobile-visible sidebar clutter remain after projects were removed or reorganized.

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

- Reads saved project roots from `.codex-global-state.json`.
- Classifies threads in `state_*.sqlite` by `cwd`.
- Keeps saved projects, projectless chats, and the current thread by default.
- Finds non-active project threads outside saved project roots.
- Finds deleted `cwd` entries and stale archived threads.
- Backs up affected metadata before changing anything.
- Cleans matching session JSONL files, thread indexes, global state, `config.toml`, and SQLite rows.
- Verifies SQLite integrity and checks that removed targets no longer appear.

## Installation

Copy the skill folder into your Codex skills directory:

```powershell
Copy-Item -Recurse .\codex-local-cleanup "$env:USERPROFILE\.codex\skills\codex-local-cleanup"
```

Restart Codex Desktop after installation if the skill does not appear immediately.

## Example Prompts

```text
$codex-local-cleanup Keep my saved projects and projectless chats, then back up and clean non-active project metadata from local Codex.
```

```text
$codex-local-cleanup Find deleted cwd threads in my local Codex metadata, back them up, remove only those stale entries, and verify the result.
```

```text
$codex-local-cleanup Clean saved-project-outside project traces, but do not delete archived_sessions.
```

## Safety Notes

This skill works with local Codex Desktop state. It should always back up before modifying metadata.

It should not delete or rewrite:

- `auth.json`
- `installation_id`
- `skills/`
- `plugins/`
- `automations/`
- `.sandbox-secrets/`
- user source projects

The skill is intentionally conservative. It preserves saved project roots, projectless chats, and the current thread unless explicitly instructed otherwise.

## Repository Layout

```text
codex-local-cleanup-skill/
├─ README.md
├─ LICENSE
├─ .gitignore
└─ codex-local-cleanup/
   ├─ SKILL.md
   └─ agents/
      └─ openai.yaml
```

## License

MIT
