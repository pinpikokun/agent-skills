# PowerShell コード例

## メール作成

```powershell
$mail = $outlook.CreateItem(0)
$mail.To = "user@example.com"
$mail.CC = "cc@example.com"
$mail.Subject = "件名"
$mail.Body = "本文"
# $mail.HTMLBody = "<html><body>HTML本文</body></html>"
# $mail.Attachments.Add("C:\path\to\file.pdf")
$mail.Display()
```

## 返信・転送

```powershell
$item = $namespace.GetItemFromID($EntryID)
$reply = $item.Reply()       # 返信
$reply.Display()
# $item.ReplyAll().Display() # 全員に返信
# $fwd = $item.Forward(); $fwd.To = "to@example.com"; $fwd.Display()  # 転送
```

## メール検索（Restrict フィルタ）

```powershell
$folder = $namespace.GetDefaultFolder(6)  # 6=受信トレイ
$conditions = @()
if ($DateFrom) { $conditions += """urn:schemas:httpmail:datereceived"" >= '$DateFrom'" }
if ($DateTo)   { $conditions += """urn:schemas:httpmail:datereceived"" < '$DateTo'" }
if ($Subject)  { $conditions += """urn:schemas:httpmail:subject"" LIKE '%$Subject%'" }
if ($FromName) { $conditions += """urn:schemas:httpmail:fromname"" LIKE '%$FromName%'" }

$items = $folder.Items
if ($conditions.Count -gt 0) {
    $filter = "@SQL=" + ($conditions -join " AND ")
    $items = $items.Restrict($filter)
}
$items.Sort("[ReceivedTime]", $true)
$count = [Math]::Min($items.Count, $MaxResults)
for ($i = 1; $i -le $count; $i++) {
    $item = $items.Item($i)
    # $item.Subject, $item.SenderName, $item.ReceivedTime, $item.EntryID
}
```

## フォルダ操作

### サブフォルダの取得（ネスト対応）

```powershell
$folder = $namespace.GetDefaultFolder(6)  # 受信トレイ
$subParts = "Projects/TeamA" -split "/"
foreach ($part in $subParts) {
    $folder = $folder.Folders.Item($part)
}
```

### フォルダ一覧の表示

```powershell
function Show-Folders($folder, $indent = 0) {
    $prefix = "  " * $indent
    Write-Host "$prefix$($folder.Name) ($($folder.Items.Count) items)"
    foreach ($sub in $folder.Folders) { Show-Folders $sub ($indent + 1) }
}

# 受信トレイ以下を表示
Show-Folders ($namespace.GetDefaultFolder(6))

# 全ストアを表示
foreach ($store in $namespace.Stores) {
    Write-Host "=== $($store.DisplayName) ==="
    Show-Folders $store.GetRootFolder() 1
}
```

## 添付ファイル保存

```powershell
$item = $namespace.GetItemFromID($EntryID)
$saveDir = "C:\temp\attachments"
if (-not (Test-Path $saveDir)) { New-Item -ItemType Directory -Path $saveDir -Force | Out-Null }
foreach ($attachment in $item.Attachments) {
    $path = Join-Path $saveDir $attachment.FileName
    $attachment.SaveAsFile($path)
    Write-Host "Saved: $path"
}
```

## 本文検索（PowerShell 実装）

Python スキルの `search_body_hybrid()` が推奨。PowerShell で実装が必要な場合のみ:

```powershell
$dateFrom = (Get-Date).AddDays(-7).ToString("MM/dd/yyyy")
$filter = "@SQL=""urn:schemas:httpmail:datereceived"" >= '$dateFrom'"
$items = $folder.Items.Restrict($filter)
$items.Sort("[ReceivedTime]", $true)
$count = $items.Count
for ($i = 1; $i -le $count; $i++) {
    $item = $items.Item($i)
    if ($item.Body -match "検索キーワード") {
        # マッチ
    }
}
```

## フラグ検索（PowerShell 実装）

Python スキルの `search_flagged()` が推奨。PowerShell で実装が必要な場合のみ:

```powershell
$dateFrom = (Get-Date).AddYears(-1).ToString("MM/dd/yyyy")
$filter = "@SQL=""urn:schemas:httpmail:datereceived"" >= '$dateFrom'"
$items = $folder.Items.Restrict($filter)
$items.Sort("[ReceivedTime]", $true)
for ($i = 1; $i -le $items.Count; $i++) {
    $item = $items.Item($i)
    if ($item.FlagStatus -eq 2) {  # 2=未完了フラグ
        # マッチ
    }
}
```

- FlagStatus: 0=なし, 1=完了, 2=未完了フラグ
- TaskDueDate: 未設定時は `Year=4501` 等の異常値 → `Year -lt 4500` でガード

## デフォルトフォルダ ID

| ID | フォルダ |
|----|---------|
| 3  | 削除済みアイテム |
| 4  | 送信トレイ |
| 5  | 送信済みアイテム |
| 6  | 受信トレイ |
| 9  | 予定表 |
| 10 | 連絡先 |
| 16 | 下書き |

## メールのプロパティ

| プロパティ | 内容 |
|-----------|------|
| `.Subject` | 件名 |
| `.SenderName` | 送信者名 |
| `.SenderEmailAddress` | 送信者メールアドレス |
| `.ReceivedTime` | 受信日時 |
| `.Body` | プレーンテキスト本文 |
| `.HTMLBody` | HTML本文 |
| `.To` | 宛先 |
| `.CC` | CC |
| `.Attachments` | 添付ファイルコレクション |
| `.EntryID` | メール固有ID |
| `.FlagStatus` | フラグ状態（0=なし, 1=完了, 2=フラグ付き） |
| `.FlagRequest` | フラグの種類 |
| `.IsMarkedAsTask` | タスクとしてマーク済みか |
| `.TaskDueDate` | タスクの期限日 |

## 注意事項

- セキュリティダイアログが表示される場合がある（外部プログラムからのアクセス警告）
- サブフォルダは `"/"` 区切りでネスト指定可能（例: `"Projects/TeamA"`）

## 日付境界問題の対処

```powershell
# Restrict は広めに取る（前日から）
$dateFrom = (Get-Date "2026-02-24").ToString("MM/dd/yyyy")
$dateTo   = (Get-Date "2026-02-28").ToString("MM/dd/yyyy")
$filter = "@SQL=""urn:schemas:httpmail:datereceived"" >= '$dateFrom' AND ""urn:schemas:httpmail:datereceived"" < '$dateTo'"
# 取得後に PowerShell 側で正確にフィルタ
if ($item.ReceivedTime.Date -ge [datetime]"2026-02-25" -and $item.ReceivedTime.Date -le [datetime]"2026-02-26") { ... }
```
