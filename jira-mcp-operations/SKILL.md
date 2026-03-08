---
name: jira-mcp-operations
description: Jira MCP チケット操作ガイド。課題の作成・取得・更新・ステータス遷移・コメント追加・添付ダウンロード。サブエージェント委任ルール付き。Jira チケットを操作する際に使用する。
---

# Jira MCP 操作ガイド

## 最初にやること

1. **チケットの検索・取得（読み取り）** → `general-purpose` サブエージェントに委任する（本文が長くコンテキストを圧迫するため）
2. **チケットの作成・更新・遷移・コメント追加（書き込み）** → メインで直接実行する
3. 接続エラーが出たら `jira-jira_client_init` で再初期化する

## 利用可能なツール一覧

| ツール名 | 用途 |
|---------|------|
| `jira-jira_client_init` | 接続の初期化・確認 |
| `jira-jira_get_issue` | 単一チケットの詳細取得 |
| `jira-jira_get_batch_issues` | 複数チケットの一括取得 |
| `jira-jira_create_issue` | 新規チケット作成 |
| `jira-jira_update_issue` | チケットの更新（フィールド変更・コメント追加） |
| `jira-jira_get_transitions` | ステータス遷移の選択肢取得 |
| `jira-jira_transition_issue` | ステータス遷移の実行 |
| `jira-jira_add_comment` | コメント追加 |
| `jira-jira_get_project_issue_types` | プロジェクトの課題タイプ一覧取得 |
| `jira-jira_download_attachments` | 添付ファイルのダウンロード |

## チケット作成

### 手順

1. **課題タイプを確認する**（初回やプロジェクトが不明な場合）

   ```
   jira-jira_get_project_issue_types(project_key="PROJ")
   ```

   よくある課題タイプ: `Bug`, `Task`, `Story`, `Epic`, `Sub-task`

2. **チケットを作成する**

   ```
   jira-jira_create_issue(
     project_key="PROJ",
     summary="チケットタイトル",
     issuetype_name="Task",
     description="詳細な説明",
     priority_name="Medium",
     assignee_name="username",
     labels=["label1", "label2"]
   )
   ```

### 必須パラメータ

- `project_key`: プロジェクトキー（例: `PROJ`）
- `summary`: チケットのタイトル
- `issuetype_name`: 課題タイプ名（`jira_get_project_issue_types` で確認）

### オプションパラメータ

- `description`: 詳細説明
- `priority_name`: 優先度（`Highest`, `High`, `Medium`, `Low`, `Lowest`）
- `assignee_name`: 担当者のユーザー名
- `labels`: ラベルのリスト
- `custom_fields`: カスタムフィールド（例: `{"customfield_10010": "value"}`）

## チケット取得

### 単一チケット

```
jira-jira_get_issue(
  issue_key="PROJ-123",
  fields=["summary", "status", "assignee", "priority", "description"],
  expand=["changelog"]
)
```

- `fields` を指定すると必要なフィールドだけ取得でき、レスポンスが軽くなる
- `expand=["changelog"]` で変更履歴も取得可能
- `expand=["renderedFields"]` でレンダリング済みフィールドも取得可能

### 複数チケット一括取得

```
jira-jira_get_batch_issues(
  issue_keys=["PROJ-123", "PROJ-124", "PROJ-125"],
  fields=["summary", "status", "assignee"]
)
```

## チケット更新

```
jira-jira_update_issue(
  issue_key="PROJ-123",
  summary="新しいタイトル",
  description="新しい説明",
  priority_name="High",
  assignee_name="new_user",
  add_labels=["new-label"],
  remove_labels=["old-label"],
  comment="更新時のコメント",
  custom_fields={"customfield_10010": "new_value"}
)
```

### ラベル操作の注意点

- `labels`: 既存ラベルを完全に置き換える
- `add_labels`: 既存ラベルに追加する
- `remove_labels`: 指定ラベルを削除する
- `labels` と `add_labels`/`remove_labels` は同時に使わないこと

### 担当者の解除

```
jira-jira_update_issue(issue_key="PROJ-123", assignee_name="")
```

## ステータス遷移

### 手順（必ず2ステップ）

1. **利用可能な遷移を取得する**

   ```
   jira-jira_get_transitions(issue_key="PROJ-123")
   ```

   → 遷移ID・遷移名の一覧が返る

2. **遷移を実行する**

   ```
   jira-jira_transition_issue(
     issue_key="PROJ-123",
     transition="遷移名 or 遷移ID",
     comment="完了コメント",
     resolution_name="Done"
   )
   ```

### 注意事項

- `transition` には遷移ID（数値文字列）または遷移名を指定
- 完了系の遷移（Done, Resolved 等）には `resolution_name` が必要な場合がある（例: `"Done"`, `"Fixed"`, `"Won't Fix"`）
- 遷移時に `assignee_name` や `custom_fields` も同時に設定可能

## コメント追加

```
jira-jira_add_comment(
  issue_key="PROJ-123",
  body="コメント内容",
  visibility_type="role",
  visibility_value="Developers"
)
```

- `visibility_type` / `visibility_value` はオプション。指定すると特定ロール/グループのみに表示される制限付きコメントになる

## 添付ファイルダウンロード

```
jira-jira_download_attachments(
  issue_key="PROJ-123",
  target_dir="C:\\temp\\attachments"
)
```

- `target_dir` のデフォルトはカレントディレクトリ

## チケット検索・取得はサブエージェントに委任すること

チケットの検索・取得は説明文やコメントが長くメインコンテキストを圧迫するため、**必ず `general-purpose` サブエージェント（task ツール）に委任すること**。

- サブエージェントに「jira-mcp-operations スキルのツールを使ってチケットを検索・取得し、結果を要約して返せ」と指示する
- 生データ（description、コメント等）はサブエージェント側のコンテキストに閉じ込められ、メインには要約のみが返るためトークン効率が良い
- チケットの作成・更新・ステータス遷移・コメント追加など**書き込み操作はメインで直接実行**してよい

## ベストプラクティス

1. **接続確認**: 操作前にエラーが出た場合は `jira-jira_client_init` で接続を再初期化する
2. **フィールド指定**: `jira_get_issue` では `fields` パラメータで必要なフィールドだけ取得してレスポンスを軽量化する
3. **課題タイプ確認**: チケット作成前に `jira_get_project_issue_types` で利用可能な課題タイプを確認する
4. **遷移確認**: ステータス変更前に必ず `jira_get_transitions` で利用可能な遷移を確認する
5. **一括取得**: 複数チケットを取得する場合は `jira_get_batch_issues` を使い、個別取得のループを避ける
6. **コメント活用**: `jira_update_issue` の `comment` パラメータで更新と同時にコメントを残せる

