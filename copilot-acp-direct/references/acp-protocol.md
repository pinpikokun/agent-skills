# ACP プロトコル仕様

## 通信の流れ

```
Python プログラム                   copilot --acp --stdio
     │                                      │
     │  1. initialize                       │
     │  {"protocolVersion": 1}    ────────▶ │
     │                            ◀──────── │  OK
     │                                      │
     │  2. session/new                      │
     │  {"cwd": "C:\\..."}        ────────▶ │
     │                            ◀──────── │  {sessionId: "xxx"}
     │                                      │
     │  3. session/prompt                   │
     │  {"prompt": "質問"}        ────────▶ │
     │                            ◀──────── │  session/update (通知 x N回)
     │                            ◀──────── │  session/update (通知 x N回)
     │                            ◀──────── │  session/update (通知 x N回)
     │                            ◀──────── │  最終レスポンス
     │                                      │

```

## 仕様詳細

| 項目 | 値 |
|---|---|
| 起動コマンド | `copilot --acp --stdio` |
| 通信方式 | stdin/stdout で JSON-RPC 2.0 |
| protocolVersion | `1`（整数。文字列や小数はエラーになる） |
| 初期化 | `initialize` メソッド |
| セッション開始 | `session/new`（cwd は絶対パス必須、mcpServers: [] 必須） |
| 質問送信 | `session/prompt` |
| ストリーミング通知メソッド | `session/update` |
| ストリーミング通知タイプ | `agent_message_chunk`（回答本文）、`agent_thought_chunk`（思考過程） |
| 権限リクエスト | `requestPermission`（`{"outcome": {"outcome": "approved"}}` で許可） |
| Windows 注意点 | subprocess に `encoding="utf-8"` が必須（cp932 だと文字化けする） |

## トラブルシューティング

### `FileNotFoundError: 'copilot' が見つかりません`
→ Copilot CLI をインストールする: `winget install GitHub.Copilot`

### `RuntimeError: セッション開始失敗: Directory path must be absolute`
→ `cwd` に絶対パスを指定する: `CopilotACP(cwd="C:\\full\\path")`

### `UnicodeDecodeError: 'cp932' codec can't decode byte`
→ subprocess.Popen に `encoding="utf-8"` を指定する

### 回答が空になる
→ ストリーミング通知（`session/update` → `agent_message_chunk`）を処理する必要がある
