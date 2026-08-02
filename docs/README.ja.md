# Codex Local Cleanup Skill

`codex-local-cleanup` は、ローカルの Codex Desktop メタデータ (`~/.codex`) に残った古いプロジェクト情報を安全に整理するための Codex スキルです。

プロジェクトを削除または整理したあとも、Codex Desktop やモバイル版 Codex に古いプロジェクト、アーカイブ済みスレッド、削除済み作業パスが表示される場合に使います。

## 主な機能

- `local-projects` から現在のプロジェクト定義を、`thread-project-assignments` からスレッドの割り当てを読み取ります。
- 各プロジェクトの `rootPaths` で複数フォルダーを扱い、旧 saved root はフォールバックとしてのみ使用します。
- 既定では、アクティブなプロジェクト、projectless の通常チャット、automation スレッド、生成されたワークスペース、現在のスレッドを保持します。
- JSONL や SQLite を直接修復する前に、公式 Codex App Server の `thread/delete` を優先します。
- `.codex/sqlite/codex-dev.db` は主な削除元ではなく、再同期後に確認する派生カタログとして扱います。
- `session_index.jsonl` と legacy DB は互換性確認用として扱い、正規のインベントリにはしません。
- 名前だけ変更されたプロジェクトは、削除対象ではなく表示名同期の問題として扱います。
- 不整合なプロジェクト割り当てと、アクティブなプロジェクト外のスレッドを検出します。
- 削除済み `cwd` と古いアーカイブスレッドを検出します。
- 変更前に対象メタデータをバックアップします。
- 表示、アーカイブ、容量、最終的な直接修復を別の範囲として扱い、確認済みの対象だけを整理します。
- SQLite の整合性と削除対象が残っていないことを検証します。

## インストール

推奨: Codex の組み込み `skill-installer` スキルで、この GitHub パスからインストールします。

```text
$skill-installer Install the skill from https://github.com/cku3987/codex-local-cleanup-skill/tree/main/codex-local-cleanup
```

手動インストール: スキルフォルダーを Codex のスキルディレクトリにコピーします。

```powershell
Copy-Item -Recurse .\codex-local-cleanup "$env:USERPROFILE\.codex\skills\codex-local-cleanup"
```

スキルがすぐに表示されない場合は、Codex Desktop を再起動してください。

## 使用例

```text
$codex-local-cleanup Keep my active local projects and projectless chats, then back up and clean non-active project metadata from local Codex.
```

```text
$codex-local-cleanup Find deleted cwd threads in my local Codex metadata, back them up, remove only those stale entries, and verify the result.
```

```text
$codex-local-cleanup Clean project traces outside my active local projects, but do not delete archived sessions or diagnostic logs.
```

## 安全上の注意

このスキルはローカルの Codex Desktop 状態を扱います。メタデータを変更する前に必ずバックアップしてください。

重要なリスクと権限に関する注意:

- これはソースコードの削除ではなく、ローカルアプリケーション状態のクリーンアップです。
- 選択した対象の Codex スレッドメタデータ、セッション JSONL、サイドバーインデックス、信頼設定、SQLite 行を削除する場合があります。
- Desktop の **Remove** と公式 App Server のスレッド処理を先に使用し、直接修復は確認済みの残留データに限定します。
- 表示の整理は、アーカイブ、ログ、バックアップ、DB 圧縮の削除を意味しません。
- フルアクセスまたは承認なしの環境では、Codex がすぐに書き込みを実行できる場合があります。不安がある場合は、先に読み取り専用の一覧確認を依頼してください。
- 範囲が曖昧なプロンプトで広範なクリーンアップを実行しないでください。書き込み前に対象一覧、バックアップ先、保持ルールを確認してください。
- バックアップにはローカルパス、スレッドタイトル、プロンプト、会話内容が含まれる場合があります。バックアップは非公開で扱ってください。

次の項目は削除または書き換えないでください。

- `auth.json`
- `installation_id`
- `skills/`
- `plugins/`
- `automations/`
- `.sandbox-secrets/`
- ユーザーのソースプロジェクト

このスキルは意図的に保守的です。明示的に指示されない限り、現在のローカルプロジェクト、通常チャット、現在のスレッドを保持し、意味が確認できない tombstone 形式の状態は削除しません。

## ライセンス

MIT
