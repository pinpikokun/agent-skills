# Type別 構造マッピング

Phase 1.5 で特定した type のセクションだけを読むこと。

---

## type: report（`skeleton-report.html` を参照）

| Markdown | HTML |
|---|---|
| `# タイトル` | `.hero` 内 `<h1>` |
| メタ情報（日時・作成者） | `.hero-meta` 内 `.hero-meta-item` |
| `## N. セクション名` | `.section` 内 `.section-label`（英語）+ `<h2>`（**番号保持**） |
| `### サブセクション` | `<h3>` |
| `> [!NOTE]` | `.callout.note` |
| `> [!TIP]` | `.callout.improvement` |
| `> [!IMPORTANT]` | `.callout.important` |
| `> [!WARNING]` | `.callout.warning` |
| `> [!CAUTION]` | `.callout.caution` |
| ワークフロー図 | `.workflow` + `.workflow-steps` |
| テーブル | `<table>` with `<thead>/<tbody>` |
| 最終セクション | `.conclusion` |

---

## type: minutes（`skeleton-minutes.html` を参照）

report の構造に加え、議事録固有のコンポーネント:

| Markdown | HTML |
|---|---|
| 参加者リスト | `.participants` 内 `.participant-tag` |
| 決定事項 | `.decisions` 内 `.decision-item` |
| アクション項目 | `.action-items` 内 `.action-item`（担当・期限付き） |
| 課題リスト | `.issue-list` 内 `.issue-item` |

---

## type: comparison（`skeleton-comparison.html` を参照）

| Markdown | HTML |
|---|---|
| `# タイトル` | `.hero` 内 `<h1>` |
| frontmatter `subtitle` | `.hero-subtitle` |
| `## カテゴリ名` | `.comparison-column` + `.comparison-column-header` |
| `## カテゴリ名` 直下テキスト | `.comparison-column-description` |
| `### プラン名 -- 価格` | `.comparison-card` + `.card-price-badge` |
| 推奨マーク（例: `推奨`） | `.card-badge-recommended` |
| 非推奨マーク（例: `高コスト`） | `.card-badge-not-recommended` |
| `- 項目` | `.comparison-card` 内 `<ul>/<li>` |
| カテゴリ全体のラッパー | `.comparison-section` 内 `.comparison-grid` |
| `## まとめ` | `.content-narrow` 内 `.conclusion` |

---

## type: presentation（`skeleton-slide.html` / `skeleton-spa.html` を参照）

| Markdown | HTML |
|---|---|
| `##` or `---` | ページ/スライド区切り |
| slide: ナビゲーション | `.slide-arrow` + キーボードイベント |
| spa: トップページ | `.nav-cards` でカード一覧 |
| spa: 各ページ | `.page-detail` + `.back-link` |

---

## type: wbs（4パターンから選択）

### 共通マッピング（全 layout 共通）

| Markdown | HTML |
|---|---|
| `# タイトル` | `.hero` 内 `<h1>` |
| 進捗サマリー | `.status-cards` 内 `.status-card`（`.on-track` / `.at-risk` / `.delayed`） |
| WBS テーブル | `<table>` with `.phase-row` + `.badge` |
| ステータス（完了/進行中/未着手/遅延） | `.badge.done` / `.badge.in-progress` / `.badge.not-started` / `.badge.delayed` |

### layout: daily（`skeleton-wbs.html` を参照）

| Markdown | HTML |
|---|---|
| ガントチャート（Markdown の表形式） | `.wbs-gantt` 内の CSS ガントチャート（**日付単位**グリッド、フェーズグループ、バー） |

ガントチャートは純粋な CSS/HTML で実装する（Mermaid.js 禁止）。スケルトンの `.wbs-gantt` 構造を踏襲し、左パネル（タスク名・ステータス・開始/終了/締切・担当）と右タイムライン（日付グリッド + バー）で構成する。CSS変数 `--day-w: 30px` で1日あたりの幅を制御。

### layout: weekly（`skeleton-wbs-weekly.html` を参照）

| Markdown | HTML |
|---|---|
| ガントチャート（Markdown の表形式） | `.wbs-gantt` 内の CSS ガントチャート（**週単位**グリッド、フェーズグループ、バー） |

daily と同じ構造だが、ルーラーが週単位。CSS変数 `--week-w: 100px` で1週あたりの幅を制御。ヘッダーの日付セルは `.wbs-weeks .w`（週の開始日を表示）。バーの `left` / `width` は週数ベースで計算する（例: 2週間のタスク → `width: calc(2 * var(--week-w))`、端数は小数で表現）。

### layout: monthly（`skeleton-wbs-monthly.html` を参照）

| Markdown | HTML |
|---|---|
| ガントチャート（Markdown の表形式） | `.wbs-gantt` 内の CSS ガントチャート（**月単位**グリッド、四半期ヘッダー、フェーズグループ、バー） |

weekly と同じ構造だが、ルーラーが月単位。CSS変数 `--month-w: 140px` で1か月あたりの幅を制御。ヘッダーは四半期行（`.wbs-quarters .wbs-quarter-lbl`）+ 月名行（`.wbs-months-hdr .m`）の2段構成。バーの `left` / `width` は月数ベースで計算する（例: 3か月のタスク → `width: calc(3 * var(--month-w))`、端数は小数で表現）。4フェーズ以上に対応するため `.p4`（青系）のカラーも用意。

### layout: table（`skeleton-wbs-table.html` を参照）

ガントチャートを含まない。Hero + 進捗サマリーカード + WBS テーブルのみで構成。`.wbs-gantt` 関連の CSS・HTML は一切不要。最も軽量なレイアウト。

### WBS の遅延時 HTML 表現ルール

| Markdown の表現 | HTML での変換 |
|---|---|
| `~~2/21~~ 2/24` | `<s>2/21</s> 2/24` |
| `遅延中` / `N日遅延で完了` | `.badge.delayed`（赤バッジ） |
| 遅延タスクの進捗バー | `background: var(--accent-red)` で赤色表示 |
| 遅延フェーズの `.status-card` | `.status-card.delayed`（赤枠） |
| gantt の遅延タスク | `.wbs-bar` に赤色グラデーション + 赤ボーダーで強調 |

---

## type: roadmap（`skeleton-roadmap-*.html` を参照 — 5パターンから選択）

| Markdown | HTML |
|---|---|
| `# タイトル` | `.hero` 内 `<h1>` |
| 現在のステータス表 | `.status-cards` 内 `.status-card`（`.on-track` / `.at-risk` / `.delayed`） |
| タイムライン/ガントチャート | 選択したパターンのCSS構造で生成（Mermaid.js 禁止） |
| `## Phase N: フェーズ名` | `.timeline-item` + `.timeline-phase-title` |
| `### 主な成果物` + リスト | `.timeline-body` 内 `<ul>` |
| `### マイルストーン: 名前 — 日付` | `.milestone-marker` |
| リスクテーブル | `<table>` with `.badge.high` / `.badge.medium` / `.badge.low` |
| 変更履歴 | `.changelog` 内 `.changelog-entry` |

マイルストーンの状態は `.done`（達成済）/ `.active`（進行中）/ `.upcoming`（今後）で表現。すべてのチャート・タイムラインは純粋な CSS/HTML で実装する。

### roadmap の遅延時 HTML 表現ルール

| Markdown の表現 | HTML での変換 |
|---|---|
| `~~5/31~~ 6/14` | `<s>5/31</s> 6/14` |
| `（2週間遅延）` | `.delay-note`（赤字テキスト）または `.milestone-marker.delayed`（赤バッジ） |
| `[!WARNING]` 遅延影響 | `.callout.warning` |
| 遅延フェーズ | `.timeline-dot.delayed`（赤丸 + 赤い影）、`.status-card.delayed`（赤枠） |
| `当初予定: ...` | `.timeline-period` 内に `.delay-note` で赤字表示 |
