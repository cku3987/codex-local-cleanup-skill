# Codex Local Cleanup Skill

`codex-local-cleanup` 是一个 Codex 技能，用于安全清理本地 Codex Desktop 元数据 (`~/.codex`) 中残留的旧项目记录。

当项目被删除或重组后，Codex Desktop 或移动端 Codex 仍然显示旧项目、归档线程或已删除工作路径时，可以使用此技能。

## 功能

- 从 `.codex-global-state.json` 读取已保存的项目根目录。
- 按 `cwd` 对 `state_*.sqlite` 中的线程进行分类。
- 默认保留已保存项目、projectless 普通聊天和当前线程。
- 查找已保存项目之外的非活动项目类线程。
- 查找已删除的 `cwd` 条目和过期归档线程。
- 在修改前备份相关元数据。
- 清理目标 session JSONL、线程索引、global state、`config.toml` 和 SQLite 行。
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
$codex-local-cleanup Keep my saved projects and projectless chats, then back up and clean non-active project metadata from local Codex.
```

```text
$codex-local-cleanup Find deleted cwd threads in my local Codex metadata, back them up, remove only those stale entries, and verify the result.
```

```text
$codex-local-cleanup Clean saved-project-outside project traces, but do not delete archived_sessions.
```

## 安全说明

此技能会处理本地 Codex Desktop 状态。修改元数据前必须先备份。

重要风险和权限说明：

- 这是本地应用状态清理，不是源代码清理。
- 它可能会删除所选目标的 Codex 线程元数据、会话 JSONL、侧边栏索引、信任配置和 SQLite 行。
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

该技能默认采取保守策略。除非明确要求，否则会保留已保存项目、普通聊天和当前线程。

## 许可证

MIT
