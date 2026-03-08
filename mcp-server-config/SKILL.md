---
name: mcp-server-config
description: Copilot CLI の MCP サーバー設定・管理ガイド。設定ファイル構造、Jira/npx/Python ベースサーバーの設定例、トラブルシューティング。MCP サーバーの追加・設定変更・接続問題の調査を行う際に使用する。
---

# MCP サーバー設定ガイド（Copilot CLI）

## 設定ファイルの場所

| 項目 | パス |
|------|------|
| ✅ 正しいファイル名 | `~/.copilot/mcp-config.json` |
| ❌ 間違い（読み込まれない） | `~/.copilot/mcp.json` |
| ログ | `~/.copilot/logs/` |

> [!WARNING]
> ファイル名を間違えてもエラーは表示されない。ビルトインの `github-mcp-server` だけが接続され、カスタムサーバーは無視される。

## 設定ファイルの基本構造

```json
{
  "mcpServers": {
    "<サーバー名>": {
      "command": "<実行ファイルのフルパス>",
      "args": [],
      "env": {
        "ENV_VAR_1": "value1",
        "ENV_VAR_2": "value2"
      }
    }
  }
}
```

### フィールド説明

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `command` | ✅ | 実行ファイルの絶対パス。Windows ではバックスラッシュ2つ（`\\`） |
| `args` | ❌ | コマンドライン引数の配列 |
| `env` | ❌ | 環境変数のキー・バリュー |

### 複数サーバーの設定例

```json
{
  "mcpServers": {
    "jira": {
      "command": "C:\\Users\\<user>\\AppData\\Local\\Python\\pythoncore-3.14-64\\Scripts\\jira-mcp.exe",
      "args": [],
      "env": {
        "JIRA_BASE_URL": "https://<domain>.atlassian.net",
        "JIRA_USERNAME": "<email>",
        "JIRA_PASSWORD": "<API token>"
      }
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@anthropic/slack-mcp-server"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-..."
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@anthropic/postgres-mcp-server", "postgresql://user:pass@localhost/db"],
      "env": {}
    }
  }
}
```

## Jira MCP サーバーの設定

### インストール

```bash
pip install jira-mcp-server
```

### 実行ファイルの場所を確認

```powershell
# Windows
Get-Command jira-mcp.exe | Select-Object Source

# macOS/Linux
which jira-mcp
```

### 設定

```json
{
  "mcpServers": {
    "jira": {
      "command": "<jira-mcp.exe のフルパス>",
      "args": [],
      "env": {
        "JIRA_BASE_URL": "https://<domain>.atlassian.net",
        "JIRA_USERNAME": "<Atlassian アカウントのメールアドレス>",
        "JIRA_PASSWORD": "<Atlassian API トークン>"
      }
    }
  }
}
```

### Atlassian API トークンの取得

1. https://id.atlassian.com/manage-profile/security/api-tokens にアクセス
2. 「API トークンを作成」をクリック
3. ラベルを入力して作成
4. 生成されたトークンを `JIRA_PASSWORD` に設定

## CLI 内での MCP 管理

### `/mcp` コマンド

Copilot CLI 内で `/mcp` を実行すると、MCP サーバーの状態確認・設定変更が可能。

- 接続中のサーバー一覧を表示
- サーバーの追加・削除
- 接続テスト

## トラブルシューティング

### 1. サーバーが認識されない

**症状**: `/mcp` で自分のサーバーが表示されない

**確認事項**:
- ファイル名が `mcp-config.json` であること（`mcp.json` ではない）
- ファイルが `~/.copilot/` 直下にあること
- JSON の構文が正しいこと

```powershell
# JSON の構文チェック
Get-Content "$env:USERPROFILE\.copilot\mcp-config.json" | ConvertFrom-Json
```

### 2. サーバーが接続失敗する

**症状**: サーバーは認識されるが接続エラーになる

**確認事項**:
- `command` のパスが正しいこと（存在確認）
- 実行ファイルに実行権限があること
- 環境変数が正しく設定されていること

```powershell
# 実行ファイルの存在確認
Test-Path "<command のパス>"

# 直接実行してみる（stdio で起動するか確認）
& "<command のパス>"
```

### 3. ログの確認

```powershell
# 最新のログファイルを確認
$latestLog = Get-ChildItem "$env:USERPROFILE\.copilot\logs" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Get-Content $latestLog.FullName | Select-String -Pattern "mcp|MCP" | Select-Object -Last 20
```

### 4. 接続の再初期化

MCP ツールに `_client_init` 系のツールがある場合はそれを呼び出す。

```
jira-jira_client_init()  # Jira の場合
```

### 5. Copilot CLI の再起動

設定ファイルを変更した場合は、Copilot CLI を再起動しないと反映されない。

## npx ベースのサーバー設定

npm パッケージとして公開されている MCP サーバーは `npx` で直接実行できる。

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@scope/package-name"],
      "env": {}
    }
  }
}
```

- `-y` フラグで自動承認（プロンプトを回避）
- Node.js / npm がインストールされている必要がある

## Python ベースのサーバー設定

pip でインストールした MCP サーバーは、Scripts フォルダの exe を直接指定する。

```json
{
  "mcpServers": {
    "server-name": {
      "command": "C:\\Users\\<user>\\AppData\\Local\\Python\\<version>\\Scripts\\<server>.exe",
      "args": [],
      "env": {}
    }
  }
}
```

### パスの確認方法

```powershell
# pip でインストールされた実行ファイルの場所
pip show <package-name>
Get-Command <server-name>.exe | Select-Object Source
```

## 設定変更後のチェックリスト

- [ ] ファイル名が `mcp-config.json` であること
- [ ] JSON の構文が正しいこと（`ConvertFrom-Json` でエラーが出ないこと）
- [ ] `command` のパスが存在すること
- [ ] 必要な環境変数がすべて設定されていること
- [ ] Copilot CLI を再起動すること
- [ ] `/mcp` で接続を確認すること

