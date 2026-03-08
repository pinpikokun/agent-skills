"""
Outlook COM 共通モジュール

Outlook アプリケーションへの COM 接続を管理し、メールの取得・検索・
添付ファイル保存などの操作を提供する共有ライブラリ。

すべてのスクリプトはこのモジュールを通じて Outlook にアクセスする。
直接 win32com.client を呼び出すことは避け、このクライアントを使うこと。

使用例:
    from lib.outlook_client import OutlookClient
    client = OutlookClient()
    mails = client.get_mails(limit=10)
"""

import logging
import os
from datetime import datetime, timedelta

import pywintypes
import win32com.client

# ---------------------------------------------------------------------------
# ロガー設定
# このモジュール専用のロガーを作成する。
# 呼び出し元で logging.basicConfig() を設定すれば、自動的に出力される。
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)


class OutlookClient:
    """
    Outlook COM クライアント

    Outlook の MAPI 名前空間を通じてフォルダ・メールアイテムを操作する。
    インスタンス生成時に Outlook が起動していなければ RuntimeError を送出する。
    """

    # -----------------------------------------------------------------------
    # Outlook OlDefaultFolders 列挙値
    # https://learn.microsoft.com/en-us/office/vba/api/outlook.oldefaultfolders
    # -----------------------------------------------------------------------
    FOLDER_INBOX = 6       # 受信トレイ
    FOLDER_SENT = 5        # 送信済みアイテム
    FOLDER_DRAFTS = 16     # 下書き
    FOLDER_DELETED = 3     # 削除済みアイテム
    FOLDER_OUTBOX = 4      # 送信トレイ
    FOLDER_CALENDAR = 9    # 予定表
    FOLDER_CONTACTS = 10   # 連絡先

    def __init__(self):
        """
        Outlook COM オブジェクトを初期化する。

        まず GetActiveObject で既に起動中の Outlook プロセスに接続を試みる。
        Outlook が起動していない場合は RuntimeError を発生させ、
        ユーザーに手動起動を促す。

        Raises:
            RuntimeError: Outlook が起動していない場合
        """
        try:
            # ---------------------------------------------------------------
            # GetActiveObject は既に起動済みの COM サーバーに接続する。
            # Dispatch と違い、新規プロセスを起動しない。
            # これにより「Outlook が起動していない」状態を検知できる。
            # ---------------------------------------------------------------
            self.outlook = win32com.client.GetActiveObject("Outlook.Application")
            logger.info("Outlook アプリケーションに接続しました")
        except pywintypes.com_error as e:
            # COM エラーが発生 ＝ Outlook が起動していない
            logger.error("Outlook への接続に失敗しました: %s", e)
            raise RuntimeError(
                "Outlookが起動していません。起動してからやり直してください。"
            ) from e

        # MAPI 名前空間を取得（メール・フォルダ操作の起点）
        self.namespace = self.outlook.GetNamespace("MAPI")
        logger.debug("MAPI 名前空間を取得しました")

    # ===================================================================
    # フォルダ操作
    # ===================================================================

    def get_folder(self, folder_id=FOLDER_INBOX):
        """
        デフォルトフォルダを取得する。

        Args:
            folder_id: OlDefaultFolders 列挙値（デフォルト: 受信トレイ）

        Returns:
            MAPIFolder オブジェクト

        Raises:
            pywintypes.com_error: フォルダが見つからない場合
        """
        try:
            folder = self.namespace.GetDefaultFolder(folder_id)
            logger.debug("デフォルトフォルダを取得: %s (ID=%d)", folder.Name, folder_id)
            return folder
        except pywintypes.com_error as e:
            logger.error("フォルダ ID=%d の取得に失敗しました: %s", folder_id, e)
            raise

    def get_subfolder(self, path, root_folder_id=FOLDER_INBOX):
        """
        サブフォルダをパス指定で取得する。

        "/" 区切りのパス文字列でネストしたサブフォルダに辿り着く。
        例: "Alerting/SRM連携" → 受信トレイ/Alerting/SRM連携

        Args:
            path: "/" 区切りのサブフォルダパス（例: "Alerting/SRM連携"）
            root_folder_id: 起点となるデフォルトフォルダの ID

        Returns:
            MAPIFolder オブジェクト

        Raises:
            KeyError: 指定パスのフォルダが存在しない場合
        """
        # 起点フォルダを取得
        current = self.get_folder(root_folder_id)
        logger.debug("サブフォルダ探索開始: 起点='%s', パス='%s'", current.Name, path)

        # "/" で分割して1階層ずつ降りていく
        for part in path.split("/"):
            part = part.strip()
            if not part:
                # 空文字（先頭や末尾の "/" ）はスキップ
                continue
            try:
                current = current.Folders[part]
                logger.debug("  → '%s' に移動", current.Name)
            except pywintypes.com_error:
                # フォルダが見つからない場合のエラーメッセージ
                available = [current.Folders.Item(i + 1).Name
                             for i in range(current.Folders.Count)]
                logger.error(
                    "サブフォルダ '%s' が見つかりません。利用可能: %s",
                    part, available,
                )
                raise KeyError(
                    f"サブフォルダ '{part}' が見つかりません。"
                    f"利用可能なフォルダ: {available}"
                )
        return current

    def list_folders(self, root_folder_id=FOLDER_INBOX, max_depth=3):
        """
        フォルダ構造を再帰的に一覧表示する。

        デバッグやフォルダ名の確認に使う。
        結果はリスト形式で返し、各要素は (depth, folder_name, folder_path) のタプル。

        Args:
            root_folder_id: 起点フォルダの ID
            max_depth: 探索する最大深さ（デフォルト: 3）

        Returns:
            list[tuple[int, str, str]]: (深さ, フォルダ名, フルパス) のリスト
        """
        root = self.get_folder(root_folder_id)
        result = []

        def _walk(folder, depth):
            """再帰的にフォルダツリーを走査する内部関数"""
            # インデントで階層を視覚化するためのプレフィックス
            prefix = "  " * depth
            folder_path = folder.FolderPath
            result.append((depth, folder.Name, folder_path))
            logger.debug("%s%s (%s)", prefix, folder.Name, folder_path)

            # 最大深さに達したら再帰を止める
            if depth >= max_depth:
                return

            # サブフォルダを走査（インデックスは 1 始まり）
            try:
                for i in range(folder.Folders.Count):
                    subfolder = folder.Folders.Item(i + 1)
                    _walk(subfolder, depth + 1)
            except pywintypes.com_error as e:
                # アクセス権のないフォルダなどでエラーになる場合がある
                logger.warning("フォルダ走査中にエラー: %s", e)

        _walk(root, 0)
        return result

    # ===================================================================
    # フィルタ構築
    # ===================================================================

    def build_filter(self, date_from=None, date_to=None, subject=None,
                     from_name=None, extend_boundary=True):
        """
        Outlook Restrict 用のフィルタ文字列を構築する。

        複数条件を指定した場合は AND で結合される。
        日付は datetime オブジェクトまたは "YYYY/MM/DD" 形式の文字列で指定可能。

        Note:
            extend_boundary=True の場合、日付のみ（時刻なし）の指定時に
            COM の日付境界問題を回避するため date_from を 1 日前、date_to を
            1 日後に拡張する。Restrict の日付フィルタは 00:00:00 ちょうどの
            メールを取りこぼす場合があるための対策。正確な日付が必要な場合は
            呼び出し側で結果を再フィルタすること。

        Args:
            date_from: 開始日（この日時以降、datetime or str）
            date_to:   終了日（この日時以前、datetime or str）
            subject:   件名に含まれる文字列（部分一致）
            from_name: 送信者名に含まれる文字列（部分一致）
            extend_boundary: 日付境界を拡張するか（デフォルト: True）

        Returns:
            str | None: Restrict に渡すフィルタ文字列。条件なしの場合は None

        使用例:
            f = client.build_filter(
                date_from="2025/01/01",
                date_to=datetime(2025, 1, 31),
                subject="月次レポート",
            )
            mails = client.get_mails(filter_str=f)
        """
        conditions = []

        # --- 日付フィルタ ---
        if date_from is not None:
            # datetime オブジェクトの場合は文字列に変換
            if isinstance(date_from, datetime):
                # 時刻成分がゼロ（日付のみ）の場合のみ境界を拡張する
                if extend_boundary and date_from.hour == 0 and date_from.minute == 0 and date_from.second == 0:
                    date_from = (date_from - timedelta(days=1)).strftime("%Y/%m/%d %H:%M")
                else:
                    date_from = date_from.strftime("%Y/%m/%d %H:%M")
            else:
                # 文字列の場合: 時刻成分を含まない場合のみ拡張
                if extend_boundary and ":" not in str(date_from):
                    try:
                        dt = datetime.strptime(str(date_from).replace("-", "/"), "%Y/%m/%d")
                        date_from = (dt - timedelta(days=1)).strftime("%Y/%m/%d")
                    except ValueError:
                        logger.warning("日付文字列のパース失敗（境界補正スキップ）: %s", date_from)
            conditions.append(f"[ReceivedTime] >= '{date_from}'")

        if date_to is not None:
            if isinstance(date_to, datetime):
                if extend_boundary and date_to.hour == 0 and date_to.minute == 0 and date_to.second == 0:
                    date_to = (date_to + timedelta(days=1)).strftime("%Y/%m/%d %H:%M")
                else:
                    date_to = date_to.strftime("%Y/%m/%d %H:%M")
            else:
                if extend_boundary and ":" not in str(date_to):
                    try:
                        dt = datetime.strptime(str(date_to).replace("-", "/"), "%Y/%m/%d")
                        date_to = (dt + timedelta(days=1)).strftime("%Y/%m/%d")
                    except ValueError:
                        logger.warning("日付文字列のパース失敗（境界補正スキップ）: %s", date_to)
            conditions.append(f"[ReceivedTime] <= '{date_to}'")

        # --- 件名フィルタ（DASL 構文で部分一致検索）---
        # Restrict の標準構文は完全一致のみなので、DASL (ci_startswith/ci_phrasematch)
        # または SQL like 構文を使って部分一致を実現する
        if subject is not None:
            conditions.append(
                f"@SQL=\"urn:schemas:httpmail:subject\" LIKE '%{subject}%'"
            )

        # --- 送信者名フィルタ ---
        if from_name is not None:
            conditions.append(
                f"@SQL=\"urn:schemas:httpmail:fromemail\" LIKE '%{from_name}%'"
            )

        if not conditions:
            return None

        # ---------------------------------------------------------------
        # 複数条件の結合
        # DASL (@SQL=...) と通常の Restrict 構文は混在できないため、
        # DASL 条件がある場合はすべて DASL 形式で結合する。
        # 通常の条件（日付のみ）の場合は AND で結合する。
        # ---------------------------------------------------------------
        has_dasl = any(c.startswith("@SQL=") for c in conditions)

        if has_dasl:
            # DASL 条件と通常条件を統合するため、日付条件も DASL に変換する
            dasl_parts = []
            for c in conditions:
                if c.startswith("@SQL="):
                    # "@SQL=" プレフィックスを除去して中身だけ取り出す
                    dasl_parts.append(c[5:])
                elif "[ReceivedTime] >=" in c:
                    # 通常の日付条件を DASL 形式に変換
                    val = c.split("'")[1]
                    dasl_parts.append(
                        f"\"urn:schemas:httpmail:datereceived\" >= '{val}'"
                    )
                elif "[ReceivedTime] <=" in c:
                    val = c.split("'")[1]
                    dasl_parts.append(
                        f"\"urn:schemas:httpmail:datereceived\" <= '{val}'"
                    )
                else:
                    dasl_parts.append(c)
            filter_str = "@SQL=" + " AND ".join(dasl_parts)
        else:
            # 通常の Restrict 構文で AND 結合
            filter_str = " AND ".join(conditions)

        logger.debug("構築したフィルタ: %s", filter_str)
        return filter_str

    # ===================================================================
    # メール取得（内部共通処理）
    # ===================================================================

    def _fetch_items(self, items, limit=None, body_length=1000):
        """
        Items コレクションからメール情報を抽出する内部メソッド。

        for-each ではなくインデックスアクセス (Items.Item(i)) を使用する。
        理由: for-each は COM コレクションのカーソルを内部で管理するため、
        Sort/Restrict 後の順序保証やパフォーマンスに問題が出ることがある。
        インデックスアクセスはこれらの問題を回避できる。

        Args:
            items: Outlook Items コレクション（Sort/Restrict 済み）
            limit: 取得件数の上限（None で全件）
            body_length: Body を切り詰める最大文字数（デフォルト: 1000）

        Returns:
            list[dict]: メール情報の辞書リスト。各辞書のキー:
                - EntryID: メールの一意識別子（後続操作で使用）
                - Subject: 件名
                - SenderName: 送信者名
                - SenderEmail: 送信者メールアドレス
                - ReceivedTime: 受信日時（datetime）
                - Body: 本文（body_length で切り詰め）
                - HasAttachments: 添付ファイルの有無
                - AttachmentCount: 添付ファイル数
                - To: 宛先
                - CC: CC
                - FlagStatus: フラグ状態（0=なし, 1=完了, 2=未完了）
                - FlagRequest: フラグの要求内容
                - TaskDueDate: フラグの期限日
        """
        data = []
        # Items.Count で総件数を取得し、上限があれば小さい方を採用
        total = items.Count
        fetch_count = min(total, limit) if limit else total
        logger.info("メール取得開始: 総件数=%d, 取得件数=%d", total, fetch_count)

        for i in range(1, fetch_count + 1):
            try:
                # -------------------------------------------------------
                # インデックスは 1 始まり（COM の慣例）
                # Item(i) で i 番目のアイテムを直接取得する
                # -------------------------------------------------------
                item = items.Item(i)

                # Body が None の場合に備えて空文字をフォールバック
                body = item.Body or ""

                data.append({
                    "EntryID": item.EntryID,
                    "Subject": item.Subject,
                    "SenderName": item.SenderName,
                    "SenderEmail": item.SenderEmailAddress,
                    "ReceivedTime": str(item.ReceivedTime),
                    "Body": body[:body_length],
                    "HasAttachments": item.Attachments.Count > 0,
                    "AttachmentCount": item.Attachments.Count,
                    "To": getattr(item, 'To', '') or '',
                    "CC": getattr(item, 'CC', '') or '',
                    "FlagStatus": getattr(item, 'FlagStatus', 0),
                    "FlagRequest": getattr(item, 'FlagRequest', '') or '',
                    "TaskDueDate": self._safe_get_task_due_date(item),
                })
            except pywintypes.com_error as e:
                # 暗号化メールや破損アイテムなど、アクセスできない場合はスキップ
                logger.warning("アイテム %d の取得に失敗（スキップ）: %s", i, e)
                continue
            except AttributeError as e:
                # 会議出席依頼など MailItem 以外のアイテムはスキップ
                logger.debug("アイテム %d は MailItem ではありません（スキップ）: %s", i, e)
                continue

        logger.info("メール取得完了: %d 件取得", len(data))
        return data

    @staticmethod
    def _safe_get_task_due_date(item):
        """TaskDueDate を安全に取得する。未設定時(year=4501等)は空文字を返す。"""
        try:
            due = item.TaskDueDate
            if due and due.year < 4500:
                return str(due)
        except (pywintypes.com_error, AttributeError):
            pass
        return ''

    # ===================================================================
    # メール取得（公開 API）
    # ===================================================================

    def get_mails(self, folder_id=FOLDER_INBOX, filter_str=None,
                  limit=None, body_length=1000):
        """
        デフォルトフォルダからメールを取得する。

        処理順序:
          1. フォルダの Items コレクションを取得
          2. Restrict でフィルタリング（指定時のみ）
          3. Sort で受信日時の降順にソート
          4. _fetch_items で結果を抽出

        重要: Restrict → Sort の順序で実行する。
        Sort → Restrict だと Restrict がソート順を無視する場合がある。

        Args:
            folder_id:   フォルダ ID（デフォルト: 受信トレイ）
            filter_str:  Restrict フィルタ文字列（None でフィルタなし）
            limit:       取得件数の上限
            body_length: Body の最大文字数

        Returns:
            list[dict]: メール情報の辞書リスト
        """
        folder = self.get_folder(folder_id)
        items = folder.Items
        logger.debug("フォルダ '%s' からメール取得開始", folder.Name)

        # ---------------------------------------------------------------
        # Restrict → Sort の順序が重要
        # 先にフィルタで対象を絞り込み、その後でソートする。
        # こうすることで、ソート結果が正しく保持される。
        # ---------------------------------------------------------------
        if filter_str:
            logger.debug("フィルタ適用: %s", filter_str)
            items = items.Restrict(filter_str)

        # 受信日時の降順（新しいメールが先頭）
        items.Sort("[ReceivedTime]", True)

        return self._fetch_items(items, limit=limit, body_length=body_length)

    def get_mails_from_folder(self, folder_obj, filter_str=None,
                              limit=None, body_length=1000):
        """
        任意のフォルダオブジェクトからメールを取得する。

        get_subfolder() で取得したフォルダオブジェクトを直接渡せる。
        デフォルトフォルダ以外（サブフォルダなど）のメール取得に使用する。

        使用例:
            folder = client.get_subfolder("Alerting/SRM連携")
            mails = client.get_mails_from_folder(folder, limit=20)

        Args:
            folder_obj:  MAPIFolder オブジェクト
            filter_str:  Restrict フィルタ文字列
            limit:       取得件数の上限
            body_length: Body の最大文字数

        Returns:
            list[dict]: メール情報の辞書リスト
        """
        items = folder_obj.Items
        logger.debug("フォルダ '%s' からメール取得開始", folder_obj.Name)

        # Restrict → Sort の正しい順序で処理
        if filter_str:
            logger.debug("フィルタ適用: %s", filter_str)
            items = items.Restrict(filter_str)

        items.Sort("[ReceivedTime]", True)

        return self._fetch_items(items, limit=limit, body_length=body_length)

    def get_mails_between(self, start_date, end_date,
                          folder_id=FOLDER_INBOX, limit=None):
        """
        日付範囲を指定してメールを取得する。

        start_date と end_date の間のメールを返す（両端含む）。
        内部で build_filter を使ってフィルタを構築する。

        Args:
            start_date: 開始日（datetime or "YYYY/MM/DD" 文字列）
            end_date:   終了日（datetime or "YYYY/MM/DD" 文字列）
            folder_id:  フォルダ ID
            limit:      取得件数の上限

        Returns:
            list[dict]: メール情報の辞書リスト
        """
        filter_str = self.build_filter(date_from=start_date, date_to=end_date)
        logger.info(
            "日付範囲メール取得: %s ～ %s",
            start_date, end_date,
        )
        return self.get_mails(folder_id, filter_str=filter_str, limit=limit)

    def get_mails_since(self, since_date, folder_id=FOLDER_INBOX, limit=None):
        """
        指定日以降のメールを取得する。

        Args:
            since_date: 開始日（datetime or "YYYY/MM/DD" 文字列）
            folder_id:  フォルダ ID
            limit:      取得件数の上限

        Returns:
            list[dict]: メール情報の辞書リスト
        """
        filter_str = self.build_filter(date_from=since_date)
        logger.info("指定日以降のメール取得: %s ～", since_date)
        return self.get_mails(folder_id, filter_str=filter_str, limit=limit)

    # ===================================================================
    # 検索
    # ===================================================================

    def search(self, keyword, folder_id=FOLDER_INBOX, limit=100):
        """
        件名・本文からキーワード検索する。

        DASL クエリを使用して件名 (subject) と本文 (textdescription) の
        両方を対象に部分一致検索を行う。

        Args:
            keyword:   検索キーワード
            folder_id: 検索対象フォルダ ID
            limit:     取得件数の上限（デフォルト: 100）

        Returns:
            list[dict]: メール情報の辞書リスト
        """
        # ---------------------------------------------------------------
        # DASL (DAV Searching and Locating) 構文でキーワード検索
        # OR で件名と本文の両方を対象にする
        # ---------------------------------------------------------------
        filter_str = (
            f"@SQL=\"urn:schemas:httpmail:subject\" LIKE '%{keyword}%' OR "
            f"\"urn:schemas:httpmail:textdescription\" LIKE '%{keyword}%'"
        )
        logger.info("キーワード検索: '%s' (limit=%d)", keyword, limit)
        return self.get_mails(folder_id, filter_str=filter_str, limit=limit)

    # ===================================================================
    # アイテム操作
    # ===================================================================

    def get_item_by_id(self, entry_id):
        """
        EntryID でメールアイテムを直接取得する。

        get_mails() の返り値に含まれる EntryID を使って、
        特定のメールアイテムの COM オブジェクトを取得する。
        添付ファイルの保存や詳細情報の取得に使用する。

        Args:
            entry_id: メールの EntryID 文字列

        Returns:
            MailItem COM オブジェクト

        Raises:
            pywintypes.com_error: アイテムが見つからない場合
        """
        try:
            item = self.namespace.GetItemFromID(entry_id)
            logger.debug("アイテム取得: EntryID=%s...", entry_id[:20])
            return item
        except pywintypes.com_error as e:
            logger.error("EntryID によるアイテム取得に失敗: %s", e)
            raise

    def save_attachments(self, entry_id, save_dir):
        """
        指定メールの添付ファイルをすべて保存する。

        EntryID からメールを取得し、添付ファイルを save_dir に保存する。
        同名ファイルが存在する場合は上書きされる。

        Args:
            entry_id: メールの EntryID 文字列
            save_dir: 保存先ディレクトリパス

        Returns:
            list[str]: 保存したファイルのフルパスのリスト
        """
        # EntryID からメールアイテムを取得
        mail_item = self.get_item_by_id(entry_id)

        # 保存先ディレクトリを作成（既存なら何もしない）
        os.makedirs(save_dir, exist_ok=True)

        saved = []
        attachment_count = mail_item.Attachments.Count
        logger.info(
            "添付ファイル保存開始: %d 件, 保存先='%s'",
            attachment_count, save_dir,
        )

        # 添付ファイルのインデックスは 1 始まり（COM の慣例）
        for i in range(1, attachment_count + 1):
            try:
                attachment = mail_item.Attachments.Item(i)
                filepath = os.path.join(save_dir, attachment.FileName)
                attachment.SaveAsFile(filepath)
                saved.append(filepath)
                logger.debug("  保存完了: %s", attachment.FileName)
            except pywintypes.com_error as e:
                logger.error("  添付ファイル %d の保存に失敗: %s", i, e)
                continue

        logger.info("添付ファイル保存完了: %d/%d 件", len(saved), attachment_count)
        return saved

    # ===================================================================
    # 再帰検索・ハイブリッド検索
    # ===================================================================

    def search_recursive(self, folder_obj, filter_str=None, limit=None,
                         body_length=1000):
        """
        フォルダとそのサブフォルダを再帰的に検索する。

        Args:
            folder_obj: 起点となる MAPIFolder オブジェクト
            filter_str: Restrict フィルタ文字列
            limit: フォルダあたりの取得件数上限（None で全件）
            body_length: Body の最大文字数

        Returns:
            list[dict]: メール情報の辞書リスト（各辞書に "Folder" キーを追加）
        """
        results = []
        logger.info("再帰検索開始: フォルダ='%s', フィルタ=%s", folder_obj.Name, filter_str or "なし")

        def _search(folder, path=""):
            current_path = f"{path}/{folder.Name}" if path else folder.Name
            mails = self.get_mails_from_folder(
                folder, filter_str=filter_str,
                limit=limit, body_length=body_length,
            )
            for mail in mails:
                mail["Folder"] = current_path
            results.extend(mails)

            try:
                for i in range(1, folder.Folders.Count + 1):
                    subfolder = folder.Folders.Item(i)
                    _search(subfolder, current_path)
            except pywintypes.com_error as e:
                logger.warning("サブフォルダ走査中にエラー: %s", e)

        _search(folder_obj)
        logger.info("再帰検索完了: %d 件取得", len(results))
        return results

    def search_body_hybrid(self, folder_obj, keyword, filter_str=None,
                           date_from=None, date_to=None, recursive=False,
                           limit=None, body_length=1000):
        """
        本文検索のハイブリッド方式。

        DASL の本文検索は非常に遅いため、日付 Restrict で絞り込んだ後に
        Python 側で本文をフィルタする。

        Args:
            folder_obj: 検索対象フォルダ
            keyword: 本文に含まれるキーワード
            filter_str: 追加の Restrict フィルタ（日付等）。
                        None の場合 date_from/date_to から自動構築
            date_from: 開始日（filter_str が None の場合に使用）
            date_to: 終了日（filter_str が None の場合に使用）
            recursive: サブフォルダも再帰検索するか
            limit: 取得件数上限
            body_length: Body の最大文字数

        Returns:
            list[dict]: 本文にキーワードを含むメール情報の辞書リスト
        """
        if filter_str is None:
            filter_str = self.build_filter(
                date_from=date_from, date_to=date_to,
            )

        if recursive:
            all_mails = self.search_recursive(
                folder_obj, filter_str=filter_str,
                limit=limit, body_length=body_length,
            )
        else:
            all_mails = self.get_mails_from_folder(
                folder_obj, filter_str=filter_str,
                limit=limit, body_length=body_length,
            )

        keyword_lower = keyword.lower()
        matched = [
            m for m in all_mails
            if keyword_lower in (m.get("Body", "") or "").lower()
        ]
        logger.info(
            "本文検索: '%s' → %d/%d 件マッチ",
            keyword, len(matched), len(all_mails),
        )
        return matched

    def search_flagged(self, folder_obj=None, date_from=None, recursive=True,
                       flag_status=2, limit=None):
        """
        フラグ付きメールを検索する（ハイブリッド方式）。

        FlagStatus は Restrict フィルタでは使用できないため、
        日付で絞り込んだ後に Python 側で FlagStatus を判定する。

        Args:
            folder_obj: 検索対象フォルダ（None の場合は受信トレイ）
            date_from: 開始日（デフォルト: 1年前）
            recursive: サブフォルダも再帰検索するか（デフォルト: True）
            flag_status: 検索するフラグ状態（デフォルト: 2=未完了フラグ）
                0=なし, 1=完了, 2=未完了フラグ
            limit: フォルダあたりの取得件数上限

        Returns:
            list[dict]: フラグ付きメール情報の辞書リスト
                各辞書に FlagStatus, FlagRequest, TaskDueDate が含まれる
        """
        if folder_obj is None:
            folder_obj = self.get_folder(self.FOLDER_INBOX)

        if date_from is None:
            date_from = datetime.now() - timedelta(days=365)

        filter_str = self.build_filter(date_from=date_from)

        if recursive:
            all_mails = self.search_recursive(
                folder_obj, filter_str=filter_str, limit=limit,
            )
        else:
            all_mails = self.get_mails_from_folder(
                folder_obj, filter_str=filter_str, limit=limit,
            )

        flagged = [
            m for m in all_mails if m.get("FlagStatus") == flag_status
        ]
        logger.info(
            "フラグ検索 (status=%d): %d/%d 件マッチ",
            flag_status, len(flagged), len(all_mails),
        )
        return flagged
