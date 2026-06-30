# Codex Local Cleanup Skill

`codex-local-cleanup` est une skill Codex destinée à nettoyer en toute sécurité les métadonnées locales obsolètes de Codex Desktop dans `~/.codex`.

Elle est utile lorsque d'anciens projets, des threads archivés, des chemins de travail supprimés ou des éléments visibles sur Codex mobile restent affichés après la suppression ou la réorganisation de projets.

## Fonctionnalités

- Lit les racines de projets enregistrées depuis `.codex-global-state.json`.
- Classe les threads de `state_*.sqlite` selon leur `cwd`.
- Conserve par défaut les projets enregistrés, les conversations sans projet et le thread actuel.
- Si Codex mobile affiche encore des entrées déjà absentes de la base active, elle inspecte aussi les fichiers legacy `.codex/sqlite/state_*.sqlite` et `.codex/sqlite/logs_*.sqlite`.
- Elle traite les projets enregistrés renommés comme des problèmes de synchronisation du nom affiché, pas comme des cibles obsolètes à supprimer.
- Repère les threads de projet inactifs situés en dehors des racines enregistrées.
- Repère les entrées `cwd` supprimées et les anciens threads archivés.
- Sauvegarde les métadonnées concernées avant toute modification.
- Nettoie les fichiers session JSONL, les index de threads, le global state, `config.toml` et les lignes SQLite concernés.
- Vérifie l'intégrité SQLite et confirme que les cibles supprimées ne sont plus présentes.

## Installation

Recommandé : demandez à Codex d'installer ce chemin GitHub avec la skill intégrée `skill-installer` :

```text
$skill-installer Install the skill from https://github.com/cku3987/codex-local-cleanup-skill/tree/main/codex-local-cleanup
```

Installation manuelle : copiez le dossier de la skill dans le répertoire des skills Codex :

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

Notes importantes sur les risques et les permissions :

- Il s'agit d'un nettoyage d'état local de l'application, pas d'un nettoyage du code source.
- Elle peut supprimer les métadonnées de threads Codex, les fichiers session JSONL, les index de barre latérale, les entrées de confiance et les lignes SQLite des cibles sélectionnées.
- Dans les environnements avec accès complet ou sans approbation, Codex peut écrire immédiatement. En cas de doute, demandez d'abord un inventaire en lecture seule.
- N'exécutez pas un nettoyage large à partir d'un prompt vague. Vérifiez la liste des cibles, le chemin de sauvegarde et les règles de conservation avant d'autoriser l'écriture.
- Les sauvegardes peuvent contenir des chemins locaux, des titres de threads, des prompts et du contenu de conversations. Gardez les sauvegardes privées.

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
