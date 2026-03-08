# OutlookClient API リファレンス

## API 一覧

主要メソッド（詳細は `lib/outlook_client.py` の docstring を参照）:

| メソッド | 用途 |
|---------|------|
| `OutlookClient()` | 接続（未起動なら RuntimeError） |
| `build_filter(date_from, date_to, subject, from_name)` | Restrict フィルタ構築（日付境界を自動補正） |
| `get_folder(folder_id)` / `get_subfolder(path)` | フォルダ取得 |
| `list_folders(root_folder_id, max_depth)` | フォルダ一覧 |
| `get_mails(folder_id, filter_str, limit)` | メール取得 |
| `get_mails_from_folder(folder_obj, filter_str, limit)` | 任意フォルダからメール取得 |
| `get_mails_between(start_date, end_date, folder_id)` | 期間指定取得 |
| `get_mails_since(since_date, folder_id)` | 指定日以降取得 |
| `search(keyword, folder_id, limit)` | キーワード検索 |
| `search_recursive(folder_obj, filter_str)` | サブフォルダ再帰検索 |
| `search_body_hybrid(folder_obj, keyword, ...)` | 本文検索（日付Restrict + Python判定） |
| `search_flagged(folder_obj, date_from)` | フラグ付きメール検索 |
| `get_item_by_id(entry_id)` | EntryID でメール取得 |
| `save_attachments(entry_id, save_dir)` | 添付ファイル保存 |

## デフォルトフォルダ ID

| 定数 | ID | フォルダ |
|------|----|---------|
| `FOLDER_INBOX` | 6 | 受信トレイ |
| `FOLDER_SENT` | 5 | 送信済みアイテム |
| `FOLDER_DRAFTS` | 16 | 下書き |
| `FOLDER_DELETED` | 3 | 削除済みアイテム |
| `FOLDER_OUTBOX` | 4 | 送信トレイ |

## メールのプロパティ

OutlookClient の返却辞書に含まれるキー:

| キー | 内容 |
|------|------|
| `EntryID` | メール固有ID（返信・転送・添付保存で使用） |
| `Subject` | 件名 |
| `SenderName` | 送信者名 |
| `SenderEmail` | 送信者メールアドレス |
| `To` | 宛先 |
| `CC` | CC |
| `ReceivedTime` | 受信日時 |
| `Body` | プレーンテキスト本文 |
| `HasAttachments` | 添付ファイルの有無 |
| `AttachmentCount` | 添付ファイル数 |
| `Folder` | フォルダ名（再帰検索時のみ） |
| `FlagStatus` | フラグ状態（0=なし, 1=完了, 2=未完了） |
| `FlagRequest` | フラグの種類 |
| `TaskDueDate` | タスクの期限日 |

## メール送信ルール

誤送信は取り消せないため、`Display()` で下書き表示してユーザー確認を得る。`Send()` はユーザーが明示的に求めた場合のみ使う。

## 注意事項

- Python スクリプトはファイルに保存して実行する（インライン実行はクォートのエスケープ問題を起こす）
- `build_filter()` が日付境界を自動補正する（正確な日付が必要ならスクリプト側で ReceivedTime を再比較）
- セキュリティダイアログが表示される場合がある
- サブフォルダは `"/"` 区切りでネスト指定可能（例: `"Projects/TeamA"`）
