---
name: outlook-powershell
description: Outlook メール操作（PowerShell COM）。メール送信・返信・転送、フォルダ一覧、簡単な件名検索など軽量な操作向け。追加インストール不要。
disable-model-invocation: true
---

# Outlook PowerShell COM 操作ガイド

## Python スキルとの使い分け

| こんな操作 | 使うスキル |
|-----------|-----------|
| メール作成・送信・返信・転送 | **PowerShell** |
| フォルダ一覧表示 | **PowerShell** |
| 単純な検索（10件以下） | **PowerShell** |
| 大量メール検索・再帰検索・本文検索・フラグ検索 | **Python** |
| 集計・分析・レポート・添付一括保存 | **Python** |

迷ったら Python スキルを使う。PowerShell は「追加パッケージ不要で手軽にできる操作」に向いている。

## 3つの鉄則

### 鉄則 1: メール検索はサブエージェントに委任する

メール本文は1通で数千トークンになる。メインコンテキストで検索すると容量を圧迫し、後続の会話が成り立たなくなる。

**`general-purpose` サブエージェント（task ツール）に委任すること。** 結果は要約して返す。
メール送信・返信・転送はユーザー確認が必要なため、メインで直接実行してよい。

### 鉄則 2: Display() で下書き表示、Send() はユーザーが求めた場合のみ

メール作成・返信・転送は `Display()` で下書きウィンドウを表示し、ユーザーに確認してもらう。
誤送信は取り消せないため、`Send()` はユーザーが明示的に自動送信を求めた場合だけ使う。

### 鉄則 3: インライン実行、スクリプトファイル不要

PowerShell の操作は1回限りの短いコードが多い。ファイルに保存すると不要なゴミが残り、ユーザーが後で掃除する手間になるため、その場でインライン実行する。

---

## 前提条件

- **Outlook が起動していること**（未起動ならユーザーに起動を促す。自動起動は行わない）

起動確認: `Get-Process OUTLOOK -ErrorAction SilentlyContinue`

すべての操作の冒頭で以下を実行する:

```powershell
if (-not (Get-Process OUTLOOK -ErrorAction SilentlyContinue)) {
    Write-Error "Outlook が起動していません。起動してから再実行してください。"
    exit 1
}
$outlook = New-Object -ComObject Outlook.Application
$namespace = $outlook.GetNamespace("MAPI")
```

---

## リファレンス

作業に応じて以下を参照する:

| ファイル | 内容 | いつ読むか |
|---------|------|-----------|
| `references/code-examples.md` | メール作成・返信・転送・検索のコードパターン、フォルダ操作、添付保存、プロパティ一覧 | コードを書くとき |
| `references/search-workflow.md` | 検索ワークフロー、絞り込み条件、フォルダ特定、人名検索、本文検索・フラグ検索の判断 | メール検索を行うとき |
| `references/output-format.md` | メール一覧テーブル、提示順序、グルーピング禁止ルール | 検索結果を表示するとき |

