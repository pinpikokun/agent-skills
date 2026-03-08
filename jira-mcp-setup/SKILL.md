---
name: jira-mcp-setup
description: Jira MCP サーバーの設定・トラブルシューティングガイド。インストール、API トークン取得、接続エラーの解決手順。「Jira MCP を設定して」「Jira に接続できない」「MCP サーバーが認識されない」と相談されたときに使用する。
---

# Jira MCP サーバー設定ガイド

Jira MCP サーバーの設定手順・トラブルシューティングは **mcp-server-config スキル** に統合されている。

以下のセクションを参照すること:

- **設定ファイルの場所・基本構造** → mcp-server-config「設定ファイルの場所」「設定ファイルの基本構造」
- **Jira MCP の設定・API トークン取得** → mcp-server-config「Jira MCP サーバーの設定」
- **トラブルシューティング** → mcp-server-config「トラブルシューティング」

## クイックリファレンス

| 項目 | 値 |
|------|------|
| パッケージ名 | `jira-mcp-server`（`pip install jira-mcp-server`） |
| 実行ファイル名 | `jira-mcp.exe` |
| 設定ファイル | `~/.copilot/mcp-config.json`（`mcp.json` は不可） |
| 必須環境変数 | `JIRA_BASE_URL`, `JIRA_USERNAME`, `JIRA_PASSWORD` |

