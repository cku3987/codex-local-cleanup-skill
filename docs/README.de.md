# Codex Local Cleanup Skill

`codex-local-cleanup` ist ein Codex-Skill zum sicheren Bereinigen veralteter lokaler Codex-Desktop-Metadaten unter `~/.codex`.

Verwende ihn, wenn nach dem Löschen oder Umorganisieren von Projekten weiterhin alte Projekte, archivierte Threads, gelöschte Arbeitsverzeichnisse oder auf Codex Mobile sichtbare Reste angezeigt werden.

## Funktionen

- Liest gespeicherte Projektwurzeln aus `.codex-global-state.json`.
- Klassifiziert Threads in `state_*.sqlite` anhand von `cwd`.
- Behält standardmäßig gespeicherte Projekte, projektlose Chats und den aktuellen Thread.
- Findet inaktive projektbezogene Threads außerhalb gespeicherter Projektwurzeln.
- Findet gelöschte `cwd`-Einträge und veraltete archivierte Threads.
- Erstellt vor Änderungen eine Sicherung der betroffenen Metadaten.
- Bereinigt passende session-JSONL-Dateien, Thread-Indizes, global state, `config.toml` und SQLite-Zeilen.
- Prüft die SQLite-Integrität und bestätigt, dass entfernte Ziele nicht mehr vorhanden sind.

## Installation

Empfohlen: Bitte Codex, diesen GitHub-Pfad mit dem integrierten `skill-installer`-Skill zu installieren:

```text
$skill-installer Install the skill from https://github.com/cku3987/codex-local-cleanup-skill/tree/main/codex-local-cleanup
```

Manuelle Installation: Kopiere den Skill-Ordner in dein Codex-Skill-Verzeichnis:

```powershell
Copy-Item -Recurse .\codex-local-cleanup "$env:USERPROFILE\.codex\skills\codex-local-cleanup"
```

Starte Codex Desktop neu, falls der Skill nicht sofort angezeigt wird.

## Beispiel-Prompts

```text
$codex-local-cleanup Keep my saved projects and projectless chats, then back up and clean non-active project metadata from local Codex.
```

```text
$codex-local-cleanup Find deleted cwd threads in my local Codex metadata, back them up, remove only those stale entries, and verify the result.
```

```text
$codex-local-cleanup Clean saved-project-outside project traces, but do not delete archived_sessions.
```

## Sicherheitshinweise

Dieser Skill arbeitet mit dem lokalen Zustand von Codex Desktop. Vor Änderungen an Metadaten sollte immer eine Sicherung erstellt werden.

Folgende Elemente sollten nicht gelöscht oder überschrieben werden:

- `auth.json`
- `installation_id`
- `skills/`
- `plugins/`
- `automations/`
- `.sandbox-secrets/`
- Quellcode-Projekte des Benutzers

Der Skill ist bewusst konservativ. Er bewahrt gespeicherte Projektwurzeln, projektlose Chats und den aktuellen Thread, sofern nicht ausdrücklich etwas anderes verlangt wird.

## Lizenz

MIT
