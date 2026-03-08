"""
インシデント・障害関連メールを全フォルダ再帰検索し、時系列レポートを出力する。

使い方:
  python scripts/search_major_incident.py --date 2026-03-06
  python scripts/search_major_incident.py --date-from 2026-03-05 --date-to 2026-03-06
  python scripts/search_major_incident.py --date 2026-03-06 --extra-keywords WMS,CS1

検索戦略:
  1. 指定日付で全フォルダ再帰的にメールを一括取得（日付 Restrict のみ）
  2. Python 側で件名＋本文をキーワードマッチ（複数キーワード OR）
  3. EntryID で重複排除し、ReceivedTime でソート
  4. 時系列テーブル + 各メール本文を出力
"""
import argparse
import sys
from datetime import datetime

sys.path.insert(0, ".")
from lib.outlook_client import OutlookClient

# ---------------------------------------------------------------------------
# デフォルトキーワード（件名・本文の両方に対して OR マッチ）
# インシデント・障害系の検索で漏れが出ないよう幅広く設定
# ---------------------------------------------------------------------------
DEFAULT_KEYWORDS = [
    # 英語
    "Major Incident", "MajorIncident", "Incident",
    "Restored", "[Restored]",
    # 日本語
    "メジャーインシデント", "インシデント",
    "障害", "緊急", "復旧",
]

BODY_MAX = 3000


def parse_args():
    parser = argparse.ArgumentParser(
        description="インシデント・障害関連メールを全フォルダ再帰検索し、時系列レポートを出力する。",
    )
    parser.add_argument(
        "--date", type=str, default=None,
        help="検索日（YYYY-MM-DD）。1日分を検索する場合はこれだけ指定",
    )
    parser.add_argument(
        "--date-from", type=str, default=None,
        help="検索開始日（YYYY-MM-DD）。--date-to と併用",
    )
    parser.add_argument(
        "--date-to", type=str, default=None,
        help="検索終了日（YYYY-MM-DD）。--date-from と併用",
    )
    parser.add_argument(
        "--extra-keywords", type=str, default=None,
        help="追加キーワード（カンマ区切り）。デフォルトキーワードに加えて検索する",
    )
    parser.add_argument(
        "--keywords-only", type=str, default=None,
        help="デフォルトキーワードを無視し、指定キーワードのみで検索（カンマ区切り）",
    )
    parser.add_argument(
        "--body-max", type=int, default=BODY_MAX,
        help=f"本文の最大出力文字数（デフォルト: {BODY_MAX}）",
    )
    return parser.parse_args()


def parse_dt(s):
    """ReceivedTime 文字列を datetime に変換"""
    try:
        return datetime.fromisoformat(str(s))
    except Exception:
        return datetime.min


def matches_any_keyword(mail, keywords_lower):
    """件名または本文にいずれかのキーワードが含まれるか判定"""
    subject = (mail.get("Subject") or "").lower()
    body = (mail.get("Body") or "").lower()
    text = subject + " " + body
    return any(kw in text for kw in keywords_lower)


def print_timeline(mails, date_label):
    """時系列テーブルを出力"""
    w_time = 8
    w_event = 28
    w_detail = 76
    sep = f"  +{'─' * (w_time + 2)}+{'─' * (w_event + 2)}+{'─' * (w_detail + 2)}+"
    hdr = f"  | {'時刻':<{w_time}} | {'イベント':<{w_event - 8}} {'':>8} | {'概要':<{w_detail - 4}} {'':>4} |"

    print(f"\n● インシデント・障害 時系列レポート（{date_label}）")
    print()
    print(sep)
    print(hdr)
    print(sep)

    for m in mails:
        dt_str = str(m.get("ReceivedTime", ""))
        time_part = dt_str[11:16] if len(dt_str) >= 16 else dt_str[:5]
        subject = (m.get("Subject") or "").strip()

        # イベント名を件名から推定
        event = _classify_event(subject, m.get("Body", ""))

        # 概要: 件名をそのまま使用（長い場合は切り詰め）
        detail = subject
        if len(detail) > w_detail:
            detail = detail[: w_detail - 3] + "..."

        print(f"  | {time_part:<{w_time}} | {event:<{w_event}} | {detail:<{w_detail}} |")

    print(sep)
    print(f"\n  合計: {len(mails)} 件")


def _classify_event(subject, body):
    """件名・本文からイベント種別を推定する"""
    s = (subject or "").lower()
    b = (body or "").lower()

    if "restored" in s or "[restored]" in s:
        return "[Restored] 復旧通知"
    if "initial" in s and ("major incident" in s or "inc" in s):
        return "Major Incident 登録"
    if "major incident" in s or "majorincident" in s:
        return "Major Incident 更新"
    if "dor" in s or "daily operational" in s:
        return "DOR配信"
    if "cab" in s:
        return "CAB Agenda/Minutes"
    if "復旧" in s:
        return "復旧通知"
    if "緊急" in s:
        return "緊急通知"
    if "障害" in s:
        return "障害通知"
    # 本文チェック
    if "major incident" in b or "メジャーインシデント" in b:
        return "関連通知"
    if "障害" in b or "incident" in b:
        return "関連通知"
    return "関連メール"


def print_mail_detail(i, m, body_max):
    """個別メールの詳細を出力"""
    print(f"\n{'=' * 80}")
    print(f"[{i}] 件名: {m.get('Subject', '')}")
    print(f"    送信者: {m.get('SenderName', '')} <{m.get('SenderEmail', '')}>")
    print(f"    受信日時: {m.get('ReceivedTime', '')}")
    print(f"    宛先: {m.get('To', '')}")
    print(f"    CC: {m.get('CC', '')}")
    print(f"    添付: {m.get('AttachmentCount', 0)} 件")
    print(f"    フォルダ: {m.get('Folder', '')}")
    print(f"{'─' * 80}")
    body = (m.get("Body") or "")[:body_max]
    print(body)


def main():
    args = parse_args()

    # 日付の解決
    if args.date:
        date_from = date_to = args.date
    elif args.date_from and args.date_to:
        date_from, date_to = args.date_from, args.date_to
    else:
        print("エラー: --date または --date-from/--date-to を指定してください", file=sys.stderr)
        sys.exit(1)

    # キーワードの解決
    if args.keywords_only:
        keywords = [k.strip() for k in args.keywords_only.split(",") if k.strip()]
    else:
        keywords = list(DEFAULT_KEYWORDS)
        if args.extra_keywords:
            keywords.extend(k.strip() for k in args.extra_keywords.split(",") if k.strip())

    keywords_lower = [kw.lower() for kw in keywords]

    date_label = date_from if date_from == date_to else f"{date_from} 〜 {date_to}"
    print(f"[設定] 日付: {date_label}", file=sys.stderr)
    print(f"[設定] キーワード ({len(keywords)}個): {', '.join(keywords)}", file=sys.stderr)

    # --- Outlook 接続 & 全メール取得（日付 Restrict のみ、1回だけ） ---
    client = OutlookClient()
    inbox = client.get_folder(client.FOLDER_INBOX)

    print(f"[検索中] 全フォルダ再帰検索 ({date_label}) ...", file=sys.stderr)
    all_mails = client.search_recursive(
        inbox,
        filter_str=client.build_filter(date_from=date_from, date_to=date_to),
        limit=None,
        body_length=args.body_max,
    )
    print(f"  -> 日付フィルタで {len(all_mails)} 件取得", file=sys.stderr)

    # --- Python 側でキーワードマッチ（件名 + 本文 OR） ---
    matched = [m for m in all_mails if matches_any_keyword(m, keywords_lower)]

    # EntryID で重複排除（念のため）
    seen = set()
    unique = []
    for m in matched:
        eid = m.get("EntryID", "")
        if eid and eid not in seen:
            seen.add(eid)
            unique.append(m)

    # ReceivedTime でソート
    unique.sort(key=lambda m: parse_dt(m.get("ReceivedTime", "")))

    print(f"  -> キーワードマッチ: {len(unique)} 件", file=sys.stderr)

    if not unique:
        print(f"\n該当するインシデント関連メールは見つかりませんでした。({date_label})")
        return

    # --- 出力 ---
    # 1. 時系列テーブル
    print_timeline(unique, date_label)

    # 2. 各メールの本文
    for i, m in enumerate(unique, 1):
        print_mail_detail(i, m, args.body_max)

    print(f"\n{'=' * 80}")
    print(f"合計: {len(unique)} 件")


if __name__ == "__main__":
    main()
