# Codex Local Cleanup Skill

`codex-local-cleanup` es una skill de Codex para limpiar de forma segura metadatos locales obsoletos de Codex Desktop en `~/.codex`.

Úsala cuando, después de eliminar o reorganizar proyectos, todavía aparezcan proyectos antiguos, hilos archivados, rutas de trabajo eliminadas o elementos residuales visibles en Codex móvil.

## Qué Hace

- Lee las raíces de proyectos guardados desde `.codex-global-state.json`.
- Clasifica los hilos de `state_*.sqlite` por `cwd`.
- Conserva por defecto los proyectos guardados, los chats sin proyecto y el hilo actual.
- Encuentra hilos de proyecto no activos fuera de las raíces guardadas.
- Encuentra entradas `cwd` eliminadas e hilos archivados obsoletos.
- Crea una copia de seguridad de los metadatos afectados antes de modificar nada.
- Limpia archivos session JSONL, índices de hilos, global state, `config.toml` y filas SQLite relacionados.
- Verifica la integridad de SQLite y confirma que los objetivos eliminados ya no aparecen.

## Instalación

Copia la carpeta de la skill en el directorio de skills de Codex:

```powershell
Copy-Item -Recurse .\codex-local-cleanup "$env:USERPROFILE\.codex\skills\codex-local-cleanup"
```

Reinicia Codex Desktop si la skill no aparece inmediatamente.

## Ejemplos de Prompts

```text
$codex-local-cleanup Keep my saved projects and projectless chats, then back up and clean non-active project metadata from local Codex.
```

```text
$codex-local-cleanup Find deleted cwd threads in my local Codex metadata, back them up, remove only those stale entries, and verify the result.
```

```text
$codex-local-cleanup Clean saved-project-outside project traces, but do not delete archived_sessions.
```

## Notas de Seguridad

Esta skill trabaja con el estado local de Codex Desktop. Siempre debe crear una copia de seguridad antes de modificar metadatos.

No debe eliminar ni sobrescribir:

- `auth.json`
- `installation_id`
- `skills/`
- `plugins/`
- `automations/`
- `.sandbox-secrets/`
- proyectos de código fuente del usuario

La skill es intencionalmente conservadora. Preserva las raíces de proyectos guardados, los chats sin proyecto y el hilo actual salvo que se indique explícitamente lo contrario.

## Licencia

MIT
