---
name: outlook-python
description: Outlook メール操作（Python COM）。大量メールの検索・集計・分析、添付ファイル一括保存、本文からのデータ抽出、インシデント時系列整理、監視バッチ集計など、解析を伴う重い処理向け。
disable-model-invocation: true
---

# Outlook Python COM 操作ガイド

## 3つの鉄則（すべての作業の前に確認）

### 鉄則 1: 既存スクリプトを最優先で使う

`scripts/` にテスト済みスクリプトがある。自前でコードを書く前に必ず確認すること。
自作コードはエッジケース対応が不足しがちで、既に解決済みの問題を踏み直すことになる。

| トリガー | スクリプト | 実行例 |
|---------|-----------|--------|
| インシデント・障害・緊急 | `search_major_incident.py` | `python scripts\search_major_incident.py --date 2026-03-06` |

```
cd "$env:USERPROFILE\.copilot\skills\outlook-python"
python scripts\<name>.py --help
```

対応スクリプトがない場合のみ、`OutlookClient` を import してコードを書く。
`OutlookClient` は COM のエラーハンドリングや日付境界補正を内包しており、`win32com.client` を直接使うとこれらの対処が漏れてバグになるため、必ず `OutlookClient` 経由で操作する。

### 鉄則 2: メール検索はサブエージェントに委任する

メール本文は1通で数千トークンになる。メインコンテキストで検索すると数通で容量を圧迫し、後続の会話が成り立たなくなる。

**`general-purpose` サブエージェント（task ツール）に委任すること。** サブエージェントへの指示:

- `cd $env:USERPROFILE\.copilot\skills\outlook-python` を最初に実行（import パスを通す）
- `from lib.outlook_client import OutlookClient` を使う
- 結果は要約して返す

メール送信・返信・転送はユーザー確認が必要なため、メインで直接実行してよい。

### 鉄則 3: 改善対象はコードであり、SKILL.md ではない

ユーザーから改善案をもらったら、**`scripts/` のスクリプトや `lib/outlook_client.py` を修正する**。
SKILL.md はガイドに過ぎず、実際の動作を決めるのはコード。
再利用できそうなコードは `scripts/` にスクリプト化する（argparse + `--help` 対応）。

---

## 前提条件

- **Outlook が起動していること**（未起動ならユーザーに起動を促す。自動起動は行わない）
- Python + `pywin32`, `pandas`, `openpyxl`, `matplotlib` がインストール済み

起動確認: `Get-Process OUTLOOK -ErrorAction SilentlyContinue`

---

## リファレンス

作業に応じて以下を参照する:

| ファイル | 内容 | いつ読むか |
|---------|------|-----------|
| `references/search-workflow.md` | 検索ワークフロー、絞り込み条件、フォルダ特定、人名検索、本文検索、フラグ検索 | メール検索を行うとき |
| `references/output-format.md` | メール一覧テーブル、提示順序、定期バッチ形式、インシデント形式 | 検索結果を表示するとき |
| `references/api.md` | OutlookClient API 一覧、メールプロパティ、フォルダ ID、メール送信ルール、注意事項 | コードを書くとき |
| `lib/outlook_client.py` | OutlookClient の実装と docstring | API の詳細仕様を確認するとき |

