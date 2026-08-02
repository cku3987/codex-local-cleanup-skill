# Codex Local Cleanup Skill

`codex-local-cleanup` 是一个 Codex 技能，用于安全清理本地 Codex Desktop 元数据 (`~/.codex`) 中残留的旧项目记录。

当项目被删除或重组后，Codex Desktop 或移动端 Codex 仍然显示旧项目、归档线程或已删除工作路径时，可以使用此技能。

## 功能

- 从 `local-projects` 读取当前项目定义，并从 `thread-project-assignments` 读取线程分配关系。
- 使用每个项目的 `rootPaths` 支持多文件夹项目；旧的 saved root 仅作为回退数据。
- 默认保留活动项目、projectless 普通聊天、automation 线程、生成的工作区和当前线程。
- 在直接修复 JSONL 或 SQLite 之前，优先使用官方 Codex App Server 的 `thread/delete`。
- 将 `.codex/sqlite/codex-dev.db` 视为重新同步后用于验证的派生目录，而不是主要删除源。
- 将 `session_index.jsonl` 和 legacy 数据库作为兼容性数据，而不是权威清单。
- 将仅改名的项目视为显示名称同步问题，而不是删除目标。
- 查找悬空的项目分配和活动项目之外的项目线程。
- 查找已删除的 `cwd` 条目和过期归档线程。
- 在修改前备份相关元数据。
- 将显示清理、归档清理、空间清理和最终直接修复分开，只处理已确认的目标。
- 验证 SQLite 完整性，并确认目标记录不再存在。

## 安装

推荐方式：使用 Codex 内置的 `skill-installer` 技能从这个 GitHub 路径安装。

```text
$skill-installer Install the skill from https://github.com/cku3987/codex-local-cleanup-skill/tree/main/codex-local-cleanup
```

手动安装：将技能文件夹复制到 Codex 技能目录。

```powershell
Copy-Item -Recurse .\codex-local-cleanup "$env:USERPROFILE\.codex\skills\codex-local-cleanup"
```

如果技能没有立即显示，请重启 Codex Desktop。

## 示例提示

```text
$codex-local-cleanup Keep my active local projects and projectless chats, then back up and clean non-active project metadata from local Codex.
```

```text
$codex-local-cleanup Find deleted cwd threads in my local Codex metadata, back them up, remove only those stale entries, and verify the result.
```

```text
$codex-local-cleanup Clean project traces outside my active local projects, but do not delete archived sessions or diagnostic logs.
```

## 安全说明

此技能会处理本地 Codex Desktop 状态。修改元数据前必须先备份。

重要风险和权限说明：

- 这是本地应用状态清理，不是源代码清理。
- 它可能会删除所选目标的 Codex 线程元数据、会话 JSONL、侧边栏索引、信任配置和 SQLite 行。
- 优先使用 Desktop 的 **Remove** 和官方 App Server 线程流程，仅对已验证的残留数据执行直接修复。
- 显示清理不代表删除归档、诊断日志、备份或执行数据库压缩。
- 在全权限或无需确认的环境中，Codex 可能可以立即写入。如果不确定，请先要求只读清单。
- 不要用含糊的提示直接执行大范围清理。写入前应检查目标列表、备份路径和保留规则。
- 备份可能包含本地路径、线程标题、提示词和对话内容。请勿公开分享备份。

不应删除或重写以下内容：

- `auth.json`
- `installation_id`
- `skills/`
- `plugins/`
- `automations/`
- `.sandbox-secrets/`
- 用户源码项目

该技能默认采取保守策略。除非明确要求，否则会保留当前本地项目、普通聊天和当前线程，也不会删除含义未确认的 tombstone 状态。

## 许可证

MIT
