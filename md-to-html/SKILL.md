---
name: md-to-html
description: Markdown ドキュメントを高品質な HTML に変換。議事録・レポート・比較資料・説明資料・WBS・ロードマップに対応し、frontmatter type に応じたレイアウトで生成する。各 type にスケルトン HTML を用意し、一貫したデザインを保証する。「議事録を HTML にして」「レポートを HTML 化して」「比較資料を HTML にして」「説明資料を HTML 化して」「WBS を HTML にして」「ロードマップを HTML にして」「Markdown を HTML に変換して」と依頼されたときに使用する。
---

# Markdown → HTML レポート変換

## 最初にやること

1. **Phase 1（参照HTMLのCSS解析）から開始する** — 変換前にデザイントークンを全行記録
2. Phase 2（HTML変換）で完了
3. Phase 1 のCSS解析なしに変換を始めないこと

## Phase 1: 参照HTMLのデザイン解析

変換前に参照HTMLのCSSを**全行**読み取り、デザイントークン・フォント・コンポーネント数値を厳密に記録する。

詳細な CSS 変数・コンポーネント仕様・数値は `references/design-tokens.md` を参照。

---

## Phase 1.5: frontmatter type 判定

Markdown の YAML frontmatter に `type` フィールドがある場合、それに応じてレイアウトと変換ルールを切り替える。

| type | レイアウト | スケルトン HTML |
|---|---|---|
| `report`（デフォルト） | 縦スクロール | `references/skeleton-report.html` |
| `minutes` | 縦スクロール（議事録固有コンポーネント） | `references/skeleton-minutes.html` |
| `comparison` | カードグリッド | `references/skeleton-comparison.html` |
| `presentation` (slide) | 横スライド遷移 | `references/skeleton-slide.html` |
| `presentation` (spa) | SPA型カードナビ | `references/skeleton-spa.html` |
| `wbs` | 4パターンから選択 | `references/skeleton-wbs-*.html`（下記参照） |
| `roadmap` | 5パターンから選択 | `references/skeleton-roadmap-*.html`（下記参照） |

- frontmatter がない、または `type` が未指定の場合は `report` として扱う
- `type: presentation` の場合、`layout` フィールドで形式を決定:
  - `layout: slide` → 横スライド型（左右矢印ナビ）
  - `layout: spa` → SPA型（カードナビゲーション）
- `type: wbs` の場合、`layout` フィールドでパターンを決定（下記参照）
- `type: roadmap` の場合、`layout` フィールドでパターンを決定（下記参照）
- **すべての type でスケルトン HTML をお手本として読み込み、同じ構造・CSS で生成する**
- **Mermaid.js の使用は禁止** — ガントチャート・タイムライン等はすべて純粋な CSS/HTML で実装する。`<script src="mermaid...">` や `<pre class="mermaid">` は使用しない

### wbs パターン一覧

| layout | スケルトン | 特徴 | 適するケース |
|---|---|---|---|
| `daily`（デフォルト） | `skeleton-wbs.html` | CSSガントチャート（日付単位グリッド、TODAY マーカー）+ WBS テーブル | 開発期間が2か月以内の短期プロジェクト |
| `weekly` | `skeleton-wbs-weekly.html` | CSSガントチャート（週単位グリッド、TODAY マーカー）+ WBS テーブル | 開発期間が2か月超の中長期プロジェクト。日付単位より生成が軽量 |
| `monthly` | `skeleton-wbs-monthly.html` | CSSガントチャート（月単位グリッド、四半期ヘッダー、TODAY マーカー）+ WBS テーブル | 開発期間が半年以上の大規模プロジェクト。最もコンパクトなガントチャート |
| `table` | `skeleton-wbs-table.html` | WBS テーブルのみ（ガントチャート無し） | 開発期間が長い、またはスケジュール可視化が不要なケース。最も軽量 |

### wbs layout 選択フロー

1. frontmatter に `layout` が **指定されている** → そのパターンで変換
2. frontmatter に `layout` が **未指定** → 開発期間から自動判定:
   - 開発期間が **2か月以内** → `daily`（日付単位ガントチャート）
   - 開発期間が **2か月超** → ユーザーに `weekly`、`monthly`、`table` を提案する。日付単位ガントチャート（`daily`）は期間が長いと生成時間・トークン消費が大きくなるため、これらから選択するよう案内する。目安: 2〜6か月は `weekly`、半年以上は `monthly` が適切

### roadmap パターン一覧

| layout | スケルトン | 特徴 | 適するケース |
|---|---|---|---|
| `gantt`（デフォルト） | `skeleton-roadmap-gantt.html` | CSSガントチャート（月単位、フェーズグループ、TODAY マーカー） | プロジェクト全体のスケジュール管理 |
| `timeline` | `skeleton-roadmap-timeline.html` | 水平タイムライン（フェーズバー、マイルストーン、KPIボックス） | 経営層向け・戦略レベルの概要 |
| `swimlane` | `skeleton-roadmap-swimlane.html` | スイムレーン（カテゴリストライプ × 四半期グリッド） | 複数チーム・領域の並行作業を俯瞰 |
| `feature` | `skeleton-roadmap-feature.html` | フィーチャーリリース（シェブロンフェーズ、製品スイムレーン） | プロダクトの機能リリース計画 |
| `chevron` | `skeleton-roadmap-chevron.html` | シェブロンフロー（5フェーズ、交互アノテーション） | シンプルなフェーズ概要・役員説明向け |

### roadmap layout 選択フロー

1. frontmatter に `layout` が **指定されている** → そのパターンで変換
2. frontmatter に `layout` が **未指定** → 以下の手順でユーザーに選ばせる:
   1. 上記5パターンの特徴一覧をユーザーに提示する
   2. 「スケルトンHTMLをブラウザでプレビューしますか？」と確認する
   3. ユーザーが希望した場合、`start` コマンドでスケルトン HTML をブラウザで開く:
      ```
      start "" "references/skeleton-roadmap-gantt.html"
      start "" "references/skeleton-roadmap-timeline.html"
      （必要に応じて他も開く）
      ```
   4. ユーザーが選択したパターンで変換を進める
3. スケルトン HTML 内の `.pattern-banner`（固定バナー）と `body { padding-top: 44px }` はプレビュー識別用。生成する HTML には含めない

---

## Phase 2: HTML変換ルール

### 共通の変換手順（全 type 共通）

1. **Phase 1.5 で特定した type に対応するスケルトン HTML を読み込む**
2. スケルトンの HTML 構造（タグ、クラス名、ネスト）を**そのまま踏襲**する
3. スケルトンの CSS（デザイントークン、コンポーネント数値）を**そのまま使用**する
4. Markdown の内容をスケルトンの構造に忠実にマッピングする

### type ごとの構造マッピング

`references/type-mappings.md` を参照し、**該当 type のセクションだけ**を読むこと。
各 type の Markdown → HTML 対応表、遅延時の表現ルールがまとまっている。

### 内容忠実性ルール（厳守）

1. **原文テキストを一字一句改変しない** — 省略・要約・言い換え禁止
2. **原文にないテキストを追加しない** — 特にサマリー文の捏造は厳禁
3. **テーブルの列を省略しない** — 全列・全行を忠実に変換
4. **括弧内注釈を省略しない** — `✅（オプションツール経由）` 等の補足情報は必須
5. **人名のフルネーム（英語名含む）を保持** — 議事録の出席者記録は正確性が最重要
6. **セクション番号を保持** — `## 1.`〜`## 7.` 等の番号は`<h2>`に含める
7. **特殊文字を統一** — `⚠️`（U+26A0 + U+FE0F emoji variant）で統一、plain `⚠` は不可

### 除外ルール（厳守）

MDファイルにはヘッダ・フッタ・メタ情報など目立たない箇所に機械的な注記が含まれることがある。
以下に該当する情報は**HTMLに一切含めない**こと。変換時にMD全体（特に冒頭・末尾・メタ情報テーブル周辺）を精査すること。

1. **AI生成に関する文言を除外する**
   - 「AIが作成」「AI文字起こし」「自動生成」「ChatGPTで作成」「Copilotで生成」等の記述はHTMLに含めない
   - 「録画から作成」「文字起こしベース」「自動議事録」等も同様に除外

2. **人間ではない参加者を除外する**
   - 「スピーカー」「録画者」「Recording Bot」「Transcription」「Microsoft Teams」「Notetaker」等、明らかに人物ではないものは参加者リストに含めない
   - 判断基準: 固有の人名（姓名）を持たないエントリはすべて除外対象

これらの情報はMDの**ヘッダ・フッタ・メタ情報テーブルなど気づきにくい場所**に記載されていることが多い。変換前にMDの先頭10行と末尾10行を必ず確認すること。

---

## リファレンス

| ファイル | 内容 | いつ読むか |
|---------|------|-----------|
| `references/design-tokens.md` | CSS変数、フォント、コンポーネント数値、バッジ注釈パターン | Phase 1（CSS解析）のとき |
| `references/type-mappings.md` | type別の Markdown → HTML 構造マッピング、遅延時表現ルール | Phase 2（HTML変換）のとき — 該当 type のセクションだけ読む |
| `references/skeleton-report.html` | report のお手本HTML — 縦スクロール型レポート | type: report のとき |
| `references/skeleton-minutes.html` | minutes のお手本HTML — 議事録（参加者・決定事項・TODO） | type: minutes のとき |
| `references/skeleton-comparison.html` | comparison のお手本HTML — カードグリッド比較 | type: comparison のとき |
| `references/skeleton-slide.html` | presentation (slide) のお手本HTML — 横スライド型 | type: presentation, layout: slide のとき |
| `references/skeleton-spa.html` | presentation (spa) のお手本HTML — SPA型カードナビ | type: presentation, layout: spa のとき |
| `references/skeleton-wbs.html` | wbs (daily) のお手本HTML — 日付単位ガントチャート + WBS テーブル | type: wbs, layout: daily のとき |
| `references/skeleton-wbs-weekly.html` | wbs (weekly) のお手本HTML — 週単位ガントチャート + WBS テーブル | type: wbs, layout: weekly のとき |
| `references/skeleton-wbs-monthly.html` | wbs (monthly) のお手本HTML — 月単位ガントチャート + WBS テーブル | type: wbs, layout: monthly のとき |
| `references/skeleton-wbs-table.html` | wbs (table) のお手本HTML — WBS テーブルのみ | type: wbs, layout: table のとき |
| `references/skeleton-roadmap-gantt.html` | roadmap のお手本HTML — CSSガントチャート | type: roadmap のとき |
| `references/skeleton-roadmap-timeline.html` | roadmap のお手本HTML — 水平タイムライン + KPI | type: roadmap のとき |
| `references/skeleton-roadmap-swimlane.html` | roadmap のお手本HTML — スイムレーン | type: roadmap のとき |
| `references/skeleton-roadmap-feature.html` | roadmap のお手本HTML — フィーチャーリリース | type: roadmap のとき |
| `references/skeleton-roadmap-chevron.html` | roadmap のお手本HTML — シェブロンフロー | type: roadmap のとき |

