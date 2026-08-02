# Codex Local Cleanup Skill

`codex-local-cleanup` es una skill de Codex para limpiar de forma segura metadatos locales obsoletos de Codex Desktop en `~/.codex`.

Úsala cuando, después de eliminar o reorganizar proyectos, todavía aparezcan proyectos antiguos, hilos archivados, rutas de trabajo eliminadas o elementos residuales visibles en Codex móvil.

## Qué Hace

- Lee las definiciones actuales de proyecto desde `local-projects` y las asignaciones de hilos desde `thread-project-assignments`.
- Admite proyectos con varias carpetas mediante `rootPaths`; las raíces guardadas antiguas solo se usan como respaldo.
- Conserva por defecto los proyectos activos, los chats sin proyecto, los hilos de automation, los espacios de trabajo generados y el hilo actual.
- Prefiere el método oficial `thread/delete` de Codex App Server antes de reparar directamente JSONL o SQLite.
- Trata `.codex/sqlite/codex-dev.db` como un catálogo derivado para verificar tras la reconciliación, no como la fuente principal de borrado.
- Trata `session_index.jsonl` y las bases legacy como datos de compatibilidad, no como inventarios autoritativos.
- Trata los proyectos renombrados como problemas de sincronización del nombre visible, no como objetivos para eliminar.
- Encuentra asignaciones de proyecto huérfanas e hilos fuera de los proyectos activos.
- Encuentra entradas `cwd` eliminadas e hilos archivados obsoletos.
- Crea una copia de seguridad de los metadatos afectados antes de modificar nada.
- Separa la limpieza de visibilidad, archivos, espacio y reparación directa final, y solo procesa objetivos confirmados.
- Verifica la integridad de SQLite y confirma que los objetivos eliminados ya no aparecen.

## Instalación

Recomendado: pídele a Codex que instale esta ruta de GitHub con la skill integrada `skill-installer`:

```text
$skill-installer Install the skill from https://github.com/cku3987/codex-local-cleanup-skill/tree/main/codex-local-cleanup
```

Instalación manual: copia la carpeta de la skill en el directorio de skills de Codex:

```powershell
Copy-Item -Recurse .\codex-local-cleanup "$env:USERPROFILE\.codex\skills\codex-local-cleanup"
```

Reinicia Codex Desktop si la skill no aparece inmediatamente.

## Ejemplos de Prompts

```text
$codex-local-cleanup Keep my active local projects and projectless chats, then back up and clean non-active project metadata from local Codex.
```

```text
$codex-local-cleanup Find deleted cwd threads in my local Codex metadata, back them up, remove only those stale entries, and verify the result.
```

```text
$codex-local-cleanup Clean project traces outside my active local projects, but do not delete archived sessions or diagnostic logs.
```

## Notas de Seguridad

Esta skill trabaja con el estado local de Codex Desktop. Siempre debe crear una copia de seguridad antes de modificar metadatos.

Notas importantes sobre riesgos y permisos:

- Esto limpia el estado local de la aplicación, no el código fuente.
- Puede eliminar metadatos de threads de Codex, archivos session JSONL, índices de la barra lateral, entradas de confianza y filas SQLite de los objetivos seleccionados.
- Prefiere **Remove** en Desktop y el ciclo oficial de hilos de App Server; la reparación directa se limita a residuos verificados.
- La limpieza de visibilidad no implica borrar archivos, logs de diagnóstico, backups ni compactar la base de datos.
- En entornos con acceso completo o sin aprobaciones, Codex puede escribir inmediatamente. Si no estás seguro, pide primero un inventario de solo lectura.
- No ejecutes una limpieza amplia con un prompt ambiguo. Revisa la lista de objetivos, la ruta de backup y las reglas de preservación antes de permitir escrituras.
- Los backups pueden contener rutas locales, títulos de threads, prompts y contenido de conversaciones. Mantén los backups privados.

No debe eliminar ni sobrescribir:

- `auth.json`
- `installation_id`
- `skills/`
- `plugins/`
- `automations/`
- `.sandbox-secrets/`
- proyectos de código fuente del usuario

La skill es intencionalmente conservadora. Preserva los proyectos locales actuales, los chats sin proyecto y el hilo actual salvo indicación explícita, y no elimina estados tipo tombstone cuyo propósito no esté confirmado.

## Licencia

MIT
