# Codex Local Cleanup Skill

`codex-local-cleanup` は、ローカルの Codex Desktop メタデータ (`~/.codex`) に残った古いプロジェクト情報を安全に整理するための Codex スキルです。

プロジェクトを削除または整理したあとも、Codex Desktop やモバイル版 Codex に古いプロジェクト、アーカイブ済みスレッド、削除済み作業パスが表示される場合に使います。

## 主な機能

- `.codex-global-state.json` から保存済みプロジェクトのルートを読み取ります。
- `state_*.sqlite` のスレッドを `cwd` で分類します。
- 既定では、保存済みプロジェクト、projectless の通常チャット、現在のスレッドを保持します。
- 保存済みプロジェクト外にある非アクティブなプロジェクト系スレッドを検出します。
- 削除済み `cwd` と古いアーカイブスレッドを検出します。
- 変更前に対象メタデータをバックアップします。
- 対象のセッション JSONL、スレッドインデックス、global state、`config.toml`、SQLite 行を整理します。
- SQLite の整合性と削除対象が残っていないことを検証します。

## インストール

スキルフォルダーを Codex のスキルディレクトリにコピーします。

```powershell
Copy-Item -Recurse .\codex-local-cleanup "$env:USERPROFILE\.codex\skills\codex-local-cleanup"
```

スキルがすぐに表示されない場合は、Codex Desktop を再起動してください。

## 使用例

```text
$codex-local-cleanup Keep my saved projects and projectless chats, then back up and clean non-active project metadata from local Codex.
```

```text
$codex-local-cleanup Find deleted cwd threads in my local Codex metadata, back them up, remove only those stale entries, and verify the result.
```

```text
$codex-local-cleanup Clean saved-project-outside project traces, but do not delete archived_sessions.
```

## 安全上の注意

このスキルはローカルの Codex Desktop 状態を扱います。メタデータを変更する前に必ずバックアップしてください。

次の項目は削除または書き換えないでください。

- `auth.json`
- `installation_id`
- `skills/`
- `plugins/`
- `automations/`
- `.sandbox-secrets/`
- ユーザーのソースプロジェクト

このスキルは意図的に保守的です。明示的に指示されない限り、保存済みプロジェクト、通常チャット、現在のスレッドを保持します。

## ライセンス

MIT
