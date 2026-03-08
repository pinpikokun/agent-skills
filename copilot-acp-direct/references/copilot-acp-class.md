# CopilotACP クラス（コピペ用完全版）

以下のクラスを自分のプロジェクトにコピーするだけで、Python から GitHub Copilot CLI を API として呼び出せる。

```python
import subprocess
import json
import uuid
import os


class CopilotACP:
    """Copilot ACP クライアント（依存なし・1ファイル完結・コピペで使える）"""

    def __init__(self, cwd=None, stream_print=True):
        self.cwd = cwd or os.getcwd()
        self.session_id = None
        self.stream_print = stream_print
        self.process = subprocess.Popen(
            ["copilot", "--acp", "--stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            bufsize=1,
        )

    def _send_raw(self, method, params=None):
        """JSON-RPC リクエストを送信。ストリーミングテキストと最終レスポンスを返す"""
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": method,
        }
        if params:
            request["params"] = params

        req_id = request["id"]
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()

        collected_text = ""

        while True:
            line = self.process.stdout.readline()
            if not line:
                return collected_text, {}
            line = line.strip()
            if not line:
                continue

            parsed = json.loads(line)

            # リクエストへの応答
            if parsed.get("id") == req_id:
                return collected_text, parsed

            # ストリーミング通知
            if parsed.get("method") == "session/update":
                update = parsed.get("params", {}).get("update", {})
                if update.get("sessionUpdate") == "agent_message_chunk":
                    content = update.get("content", {})
                    if content.get("type") == "text":
                        text = content["text"]
                        collected_text += text
                        if self.stream_print:
                            print(text, end="", flush=True)

            # 権限リクエスト（自動許可）
            if parsed.get("method") == "requestPermission" and "id" in parsed:
                response = {
                    "jsonrpc": "2.0",
                    "id": parsed["id"],
                    "result": {"outcome": {"outcome": "approved"}}
                }
                self.process.stdin.write(json.dumps(response) + "\n")
                self.process.stdin.flush()

    def start(self):
        """接続してセッションを開始"""
        _, init_resp = self._send_raw("initialize", {
            "protocolVersion": 1,
            "clientCapabilities": {}
        })

        if "error" in init_resp:
            raise RuntimeError(f"初期化失敗: {init_resp['error'].get('message')}")

        _, session_resp = self._send_raw("session/new", {
            "cwd": self.cwd,
            "mcpServers": []
        })

        if "error" in session_resp:
            raise RuntimeError(f"セッション開始失敗: {session_resp['error'].get('message')}")

        self.session_id = session_resp["result"]["sessionId"]
        return self

    def ask(self, question):
        """質問して回答テキストを返す"""
        if not self.session_id:
            raise RuntimeError("start() を先に呼んでください")

        text, _ = self._send_raw("session/prompt", {
            "sessionId": self.session_id,
            "prompt": [{"type": "text", "text": question}]
        })
        return text

    def close(self):
        """接続を終了"""
        try:
            self.process.stdin.close()
            self.process.terminate()
        except Exception:
            pass

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.close()
        return False
```

## 使い方

### パターン1: 最短で使う

```python
with CopilotACP() as copilot:
    answer = copilot.ask("Pythonでクイックソートを書いて")
    print(answer)
```

### パターン2: 対話モード

```python
copilot = CopilotACP()
copilot.start()

while True:
    q = input("あなた > ")
    if q.strip().lower() in ("quit", "exit"):
        break
    print("回答: ", end="", flush=True)
    copilot.ask(q)
    print("\n")

copilot.close()
```

### パターン3: 社内ツールに組み込む（ストリーミング表示なし）

```python
copilot = CopilotACP(stream_print=False)
copilot.start()

# バックエンドで AI に処理させて結果だけ受け取る
result = copilot.ask("このSQLにバグがないかチェックして: SELECT * FORM users")
save_to_database(result)

copilot.close()
```

### パターン4: ヘルパー関数にする

```python
def ask_copilot(question, cwd=None):
    """Copilot に1回だけ質問して回答を返すヘルパー関数"""
    with CopilotACP(cwd=cwd, stream_print=False) as copilot:
        return copilot.ask(question)

# 使う側は1行で呼べる
answer = ask_copilot("Pythonで日付のバリデーション関数を書いて")
```
