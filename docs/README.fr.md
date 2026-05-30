# Codex Local Cleanup Skill

`codex-local-cleanup` est une skill Codex destinée à nettoyer en toute sécurité les métadonnées locales obsolètes de Codex Desktop dans `~/.codex`.

Elle est utile lorsque d'anciens projets, des threads archivés, des chemins de travail supprimés ou des éléments visibles sur Codex mobile restent affichés après la suppression ou la réorganisation de projets.

## Fonctionnalités

- Lit les racines de projets enregistrées depuis `.codex-global-state.json`.
- Classe les threads de `state_*.sqlite` selon leur `cwd`.
- Conserve par défaut les projets enregistrés, les conversations sans projet et le thread actuel.
- Repère les threads de projet inactifs situés en dehors des racines enregistrées.
- Repère les entrées `cwd` supprimées et les anciens threads archivés.
- Sauvegarde les métadonnées concernées avant toute modification.
- Nettoie les fichiers session JSONL, les index de threads, le global state, `config.toml` et les lignes SQLite concernés.
- Vérifie l'intégrité SQLite et confirme que les cibles supprimées ne sont plus présentes.

## Installation

Copiez le dossier de la skill dans le répertoire des skills Codex :

```powershell
Copy-Item -Recurse .\codex-local-cleanup "$env:USERPROFILE\.codex\skills\codex-local-cleanup"
```

Redémarrez Codex Desktop si la skill n'apparaît pas immédiatement.

## Exemples de Prompts

```text
$codex-local-cleanup Keep my saved projects and projectless chats, then back up and clean non-active project metadata from local Codex.
```

```text
$codex-local-cleanup Find deleted cwd threads in my local Codex metadata, back them up, remove only those stale entries, and verify the result.
```

```text
$codex-local-cleanup Clean saved-project-outside project traces, but do not delete archived_sessions.
```

## Notes de Sécurité

Cette skill agit sur l'état local de Codex Desktop. Elle doit toujours effectuer une sauvegarde avant de modifier les métadonnées.

Elle ne doit pas supprimer ni réécrire :

- `auth.json`
- `installation_id`
- `skills/`
- `plugins/`
- `automations/`
- `.sandbox-secrets/`
- les projets source de l'utilisateur

La skill est volontairement conservatrice. Elle préserve les racines de projets enregistrées, les conversations sans projet et le thread actuel, sauf instruction explicite contraire.

## Licence

MIT
