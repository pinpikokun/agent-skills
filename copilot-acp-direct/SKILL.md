---
name: copilot-acp-direct
description: ライブラリなしで Python から GitHub Copilot CLI を ACP プロトコルで直接呼び出す方法。subprocess と JSON-RPC で通信し、pip install 不要で1ファイル完結。「ライブラリなしで Copilot を呼びたい」「1ファイルで Copilot を組み込みたい」「ACP プロトコルの仕様を教えて」と聞かれたときに使用する。
---

# Copilot ACP 直接組み込みガイド

## 概要

pip install 不要。CopilotACP クラスを自分のプロジェクトにコピーするだけで
Python から GitHub Copilot CLI を API として呼び出せる。

## 前提条件

- Python 3.9 以上
- Copilot CLI がインストール済み（`copilot --version` で確認）
- Copilot CLI にログイン済み（`copilot auth status` で確認）

## 最短の使い方

```python
with CopilotACP() as copilot:
    answer = copilot.ask("Pythonでクイックソートを書いて")
    print(answer)
```

---

## リファレンス

| ファイル | 内容 | いつ読むか |
|---------|------|-----------|
| `references/copilot-acp-class.md` | CopilotACP クラス全文（コピペ用）、4つの使い方パターン | クラスをコピーするとき、使い方を確認するとき |
| `references/acp-protocol.md` | ACP プロトコル仕様（通信フロー、JSON-RPC 詳細）、トラブルシューティング | プロトコルの詳細を知りたいとき、エラーが出たとき |

