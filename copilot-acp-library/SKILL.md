---
name: copilot-acp-library
description: copilot-acp ライブラリで Python から GitHub Copilot CLI を API として呼び出す方法。pip install して CopilotClient クラスを使用する。「copilot-acp の使い方」「CopilotClient の使い方」「ライブラリで Copilot を呼びたい」と聞かれたときに使用する。
---

# copilot-acp ライブラリ

## 概要

`copilot-acp` は、GitHub Copilot CLI の ACP (Agent Client Protocol) を使って
Python プログラムから Copilot を API として呼び出すライブラリ。
`pip install` してから `from copilot_acp import CopilotClient` で使用する。

## 前提条件

- Python 3.9 以上
- Copilot CLI がインストール済み（`copilot --version` で確認）
- Copilot CLI にログイン済み（`copilot auth status` で確認）

## インストール

```bash
cd <copilot-acp のルートディレクトリ>
python3 -m pip install -e .
```

## 基本的な使い方

### 最もシンプルな例（4行）

```python
from copilot_acp import CopilotClient

with CopilotClient() as client:
    answer = client.ask("Pythonでクイックソートを書いて")
    print(answer)
```

### 対話モード

```python
from copilot_acp import CopilotClient

client = CopilotClient()
client.start()

while True:
    question = input("質問 > ")
    if question.strip().lower() in ("quit", "exit"):
        break
    print("回答: ", end="", flush=True)
    answer = client.ask(question)
    print()

client.close()
```

### コードレビュー

```python
from copilot_acp import CopilotClient

def review_file(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    with CopilotClient(stream=False) as client:
        return client.ask(
            f"以下のコードをレビューしてください。"
            f"バグ、改善点、セキュリティ上の問題を指摘してください。\n\n"
            f"```\n{code}\n```"
        )

result = review_file("path/to/file.py")
print(result)
```

### マルチエージェント（2つの Copilot を対話させる）

```python
from copilot_acp import CopilotClient

coder = CopilotClient(stream=False)
reviewer = CopilotClient(stream=False)
coder.start()
reviewer.start()

code = coder.ask("FastAPI で TODO API を作って")
feedback = reviewer.ask(f"このコードをレビューしてください:\n\n{code}")
print(feedback)

coder.close()
reviewer.close()
```

## CopilotClient のオプション

```python
client = CopilotClient(
    cwd="C:\\path\\to\\project",  # 作業ディレクトリ（絶対パス）。省略時はカレントディレクトリ
    copilot_command="copilot",     # copilot コマンドのパス。省略時は "copilot"
    verbose=False,                 # True にすると通信内容をデバッグ表示
    stream=True,                   # True にするとストリーミング応答をリアルタイム表示
)
```

## メソッド一覧

| メソッド | 説明 | 戻り値 |
|---|---|---|
| `start()` | Copilot に接続してセッション開始 | `dict`（セッション情報） |
| `ask(question)` | 質問して回答テキストを取得 | `str`（回答テキスト） |
| `ask_raw(question)` | 質問して生の JSON レスポンスを取得 | `dict`（JSON-RPC レスポンス） |
| `close()` | 接続を終了 | `None` |

## プロパティ一覧

| プロパティ | 説明 | 型 |
|---|---|---|
| `session_id` | 現在のセッション ID | `str` |
| `agent_info` | エージェント情報（name, version） | `dict` |
| `current_model` | 現在使用中のモデル ID | `str` |
| `available_models` | 利用可能なモデル ID のリスト | `list[str]` |

## with 文（コンテキストマネージャ）対応

`with` 文を使うと `start()` と `close()` が自動で呼ばれる。
`close()` 忘れを防げるため、こちらの書き方を推奨する。

```python
with CopilotClient() as client:
    answer = client.ask("質問")
```

## ファイル構成

```
copilot_acp/
├── copilot_acp/
│   ├── __init__.py       # パッケージエントリポイント
│   └── client.py         # CopilotClient 本体
├── examples/
│   ├── simple_chat.py    # 対話サンプル
│   ├── code_review.py    # コードレビューサンプル
│   └── multi_agent.py    # マルチエージェントサンプル
├── pyproject.toml        # パッケージ設定
└── README.md             # ドキュメント
```

## トラブルシューティング

### `ModuleNotFoundError: No module named 'copilot_acp'`
→ `python3 -m pip install -e .` を copilot-acp のルートディレクトリで実行する

### `pip` コマンドが見つからない
→ `python3 -m pip install -e .` のように `python3 -m pip` で呼び出す

### `FileNotFoundError: 'copilot' が見つかりません`
→ Copilot CLI をインストールする: `winget install GitHub.Copilot`

### `RuntimeError: セッション開始失敗: Directory path must be absolute`
→ `cwd` に絶対パスを指定する: `CopilotClient(cwd="C:\\full\\path")`

