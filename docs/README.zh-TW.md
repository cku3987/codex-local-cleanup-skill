# Codex Local Cleanup Skill

`codex-local-cleanup` 是一個 Codex 技能，用於安全清理本機 Codex Desktop 中殘留的舊 metadata (`~/.codex`)。

當專案被刪除或重新整理後，Codex Desktop 或行動版 Codex 仍顯示舊專案、已封存 thread，或已刪除的工作路徑時，可以使用這個技能。

## 功能

- 從 `.codex-global-state.json` 讀取已儲存的專案根目錄。
- 依照 `cwd` 分類 `state_*.sqlite` 中的 thread。
- 預設保留已儲存專案、projectless 一般聊天與目前 thread。
- 找出已儲存專案之外的非作用中專案型 thread。
- 找出已刪除的 `cwd` 項目與過期的封存 thread。
- 修改前先備份相關 metadata。
- 清理目標 session JSONL、thread index、global state、`config.toml` 與 SQLite row。
- 驗證 SQLite 完整性，並確認目標資料已不存在。

## 安裝

建議方式：使用 Codex 內建的 `skill-installer` 技能從這個 GitHub 路徑安裝。

```text
$skill-installer Install the skill from https://github.com/cku3987/codex-local-cleanup-skill/tree/main/codex-local-cleanup
```

手動安裝：將技能資料夾複製到 Codex 技能目錄。

```powershell
Copy-Item -Recurse .\codex-local-cleanup "$env:USERPROFILE\.codex\skills\codex-local-cleanup"
```

如果技能沒有立即顯示，請重新啟動 Codex Desktop。

## 使用範例

```text
$codex-local-cleanup Keep my saved projects and projectless chats, then back up and clean non-active project metadata from local Codex.
```

```text
$codex-local-cleanup Find deleted cwd threads in my local Codex metadata, back them up, remove only those stale entries, and verify the result.
```

```text
$codex-local-cleanup Clean saved-project-outside project traces, but do not delete archived_sessions.
```

## 安全注意事項

此技能會處理本機 Codex Desktop 狀態。修改 metadata 前必須先備份。

重要風險與權限注意事項：

- 這是本機應用程式狀態清理，不是原始碼清理。
- 它可能會刪除所選目標的 Codex thread 中繼資料、session JSONL、側邊欄索引、信任設定和 SQLite row。
- 在全權限或不需確認的環境中，Codex 可能可以立即寫入。如果不確定，請先要求唯讀清單。
- 不要用範圍模糊的提示直接執行大範圍清理。寫入前應檢查目標清單、備份路徑和保留規則。
- 備份可能包含本機路徑、thread 標題、prompt 和對話內容。請勿公開分享備份。

不應刪除或重寫下列項目：

- `auth.json`
- `installation_id`
- `skills/`
- `plugins/`
- `automations/`
- `.sandbox-secrets/`
- 使用者原始碼專案

這個技能預設採保守策略。除非明確要求，否則會保留已儲存專案、一般聊天與目前 thread。

## 授權

MIT
