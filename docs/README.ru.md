# Codex Local Cleanup Skill

`codex-local-cleanup` — это навык Codex для безопасной очистки устаревших локальных метаданных Codex Desktop в `~/.codex`.

Он полезен, когда после удаления или реорганизации проектов в Codex Desktop или мобильном Codex все еще видны старые проекты, архивные треды или удаленные рабочие пути.

## Возможности

- Читает сохраненные корни проектов из `.codex-global-state.json`.
- Классифицирует треды в `state_*.sqlite` по полю `cwd`.
- По умолчанию сохраняет текущие сохраненные проекты, projectless-чаты и текущий тред.
- Находит неактивные проектные треды вне сохраненных корней проектов.
- Находит удаленные `cwd` и устаревшие архивные треды.
- Создает резервную копию затронутых метаданных перед изменениями.
- Очищает целевые session JSONL, индекс тредов, global state, `config.toml` и строки SQLite.
- Проверяет целостность SQLite и отсутствие удаленных целей.

## Установка

Рекомендуемый способ: попросите Codex установить этот путь GitHub с помощью встроенного навыка `skill-installer`.

```text
$skill-installer Install the skill from https://github.com/cku3987/codex-local-cleanup-skill/tree/main/codex-local-cleanup
```

Ручная установка: скопируйте папку навыка в директорию навыков Codex.

```powershell
Copy-Item -Recurse .\codex-local-cleanup "$env:USERPROFILE\.codex\skills\codex-local-cleanup"
```

Если навык не появился сразу, перезапустите Codex Desktop.

## Примеры запросов

```text
$codex-local-cleanup Keep my saved projects and projectless chats, then back up and clean non-active project metadata from local Codex.
```

```text
$codex-local-cleanup Find deleted cwd threads in my local Codex metadata, back them up, remove only those stale entries, and verify the result.
```

```text
$codex-local-cleanup Clean saved-project-outside project traces, but do not delete archived_sessions.
```

## Безопасность

Этот навык работает с локальным состоянием Codex Desktop. Перед изменением метаданных всегда нужно создавать резервную копию.

Важные замечания о рисках и правах доступа:

- Это очистка локального состояния приложения, а не очистка исходного кода.
- Навык может удалять выбранные метаданные тредов Codex, session JSONL, индексы боковой панели, настройки доверия и строки SQLite.
- В средах с полным доступом или без подтверждений Codex может сразу выполнять запись. Если вы не уверены, сначала запросите только чтение и список кандидатов.
- Не запускайте широкую очистку по расплывчатому запросу. Перед записью проверьте список целей, путь резервной копии и правила сохранения.
- Резервные копии могут содержать локальные пути, заголовки тредов, промпты и содержимое разговоров. Храните их приватно.

Не следует удалять или перезаписывать:

- `auth.json`
- `installation_id`
- `skills/`
- `plugins/`
- `automations/`
- `.sandbox-secrets/`
- исходные проекты пользователя

Навык намеренно консервативен. Он сохраняет сохраненные проекты, обычные чаты и текущий тред, если явно не указано обратное.

## Лицензия

MIT
