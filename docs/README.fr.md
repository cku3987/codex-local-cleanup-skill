# Codex Local Cleanup Skill

`codex-local-cleanup` est une skill Codex destinée à nettoyer en toute sécurité les métadonnées locales obsolètes de Codex Desktop dans `~/.codex`.

Elle est utile lorsque d'anciens projets, des threads archivés, des chemins de travail supprimés ou des éléments visibles sur Codex mobile restent affichés après la suppression ou la réorganisation de projets.

## Fonctionnalités

- Lit les définitions de projet actuelles dans `local-projects` et les affectations de threads dans `thread-project-assignments`.
- Prend en charge les projets multi-dossiers via `rootPaths` ; les anciennes racines enregistrées ne servent que de repli.
- Conserve par défaut les projets actifs, les conversations sans projet, les threads d'automation, les espaces de travail générés et le thread actuel.
- Privilégie la méthode officielle `thread/delete` de Codex App Server avant toute réparation directe de JSONL ou SQLite.
- Traite `.codex/sqlite/codex-dev.db` comme un catalogue dérivé à vérifier après réconciliation, et non comme la source principale de suppression.
- Traite `session_index.jsonl` et les bases legacy comme des données de compatibilité, et non comme des inventaires faisant autorité.
- Traite les projets renommés comme des problèmes de synchronisation du nom affiché, pas comme des cibles à supprimer.
- Repère les affectations de projet orphelines et les threads situés hors des projets actifs.
- Repère les entrées `cwd` supprimées et les anciens threads archivés.
- Sauvegarde les métadonnées concernées avant toute modification.
- Sépare le nettoyage de visibilité, des archives, de l'espace disque et la réparation directe finale, et ne traite que les cibles confirmées.
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
$codex-local-cleanup Keep my active local projects and projectless chats, then back up and clean non-active project metadata from local Codex.
```

```text
$codex-local-cleanup Find deleted cwd threads in my local Codex metadata, back them up, remove only those stale entries, and verify the result.
```

```text
$codex-local-cleanup Clean project traces outside my active local projects, but do not delete archived sessions or diagnostic logs.
```

## Notes de Sécurité

Cette skill agit sur l'état local de Codex Desktop. Elle doit toujours effectuer une sauvegarde avant de modifier les métadonnées.

Notes importantes sur les risques et les permissions :

- Il s'agit d'un nettoyage d'état local de l'application, pas d'un nettoyage du code source.
- Elle peut supprimer les métadonnées de threads Codex, les fichiers session JSONL, les index de barre latérale, les entrées de confiance et les lignes SQLite des cibles sélectionnées.
- Elle privilégie **Remove** dans Desktop et le cycle officiel des threads App Server ; la réparation directe est réservée aux résidus vérifiés.
- Le nettoyage de visibilité n'implique pas la suppression des archives, des logs de diagnostic, des sauvegardes ni la compaction de la base.
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

La skill est volontairement conservatrice. Elle préserve les projets locaux actuels, les conversations sans projet et le thread actuel sauf instruction explicite, et ne supprime pas un état de type tombstone dont le rôle n'est pas confirmé.

## Licence

MIT
