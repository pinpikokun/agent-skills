---
name: html-generator
description: ドキュメントを高品質な HTML に変換する。Markdown（主な入力）、PDF、テキスト、Word、Excel、PowerPoint に対応。議事録・レポート・比較資料・説明資料・WBS・ロードマップなど、ドキュメントの種類に応じたスケルトン HTML でレイアウトを統一する。「HTMLにして」「HTMLに変換して」「HTMLで出力して」「このドキュメントをHTMLにして」「このPDFをHTMLにして」「レポートをHTML化して」「議事録をHTMLにして」と依頼されたときに使用する。ドキュメントからHTMLへの変換が話題に上がったら、入力形式を問わずこのスキルを使うこと。
---

# ドキュメント → HTML 変換

## 対応入力形式

| 形式 | 拡張子 | 備考 |
|------|--------|------|
| Markdown | .md | 主な入力形式。frontmatter で type 指定可能 |
| PDF | .pdf | Read ツールで内容を読み取る |
| テキスト | .txt | そのまま読み取る |
| Word | .docx | テキスト内容を抽出して変換 |
| Excel | .xlsx | シート内容を抽出して変換 |
| PowerPoint | .pptx | スライド内容を抽出して変換 |

Markdown が最も安定した結果を返す。他の形式はベストエフォートで対応する。

## 推奨ワークフロー

このスキルは frontmatter 付き Markdown を入力にしたとき最も高品質な HTML を生成する。
Markdown 以外のドキュメント（PDF、Word、Excel、PowerPoint、テキスト等）を HTML に変換したい場合は、先に `markdown-generator` スキルで Markdown に変換してから本スキルで HTML 化するのが理想的な流れになる。

**frontmatter 付き Markdown 以外が入力された場合は、変換を始める前にこのことをユーザーに伝えること:**

> この文書を直接 HTML に変換することもできますが、先に `/markdown-generator` スキルを使って Markdown に変換し、その Markdown を html-generator で HTML 化した方が、より高品質な結果になります。
> - **そのまま変換する** → このまま直接 HTML に変換します
> - **先に Markdown に変換する** → `/markdown-generator` で Markdown を出力してから、それを HTML に変換します
>
> どちらがいいですか？

ユーザーが「そのまま変換」を選んだ場合は、以下の変換フローに進む。

---

## 変換フロー

```
Phase 1: 参照HTMLのCSS解析（デザイントークン記録）
    ↓
Phase 2: 入力の読み取り + type 判定
    ↓
Phase 3: HTML 変換（スケルトン準拠）
```

Phase 1 の CSS 解析なしに変換を始めないこと。
入力内容の読み取り（Phase 2）から HTML 変換（Phase 3）までを近づけることで、コンテキストから内容が失われるリスクを減らす。

---

## Phase 1: 参照HTMLのデザイン解析

変換前に参照HTMLのCSSを**全行**読み取り、デザイントークン・フォント・コンポーネント数値を厳密に記録する。

詳細な CSS 変数・コンポーネント仕様・数値は `references/design-tokens.md` を参照。

---

## Phase 2: 入力の読み取りと type 判定

入力ファイルの形式に応じて内容を読み取る。

- **Markdown / テキスト** — そのまま読み取る
- **PDF** — Read ツールで読み取る（10ページ超は pages パラメータで分割）
- **Word / Excel / PowerPoint** — Python ライブラリで抽出（`python-docx`, `openpyxl`, `python-pptx`）。未インストールなら `pip install` する

読み取り後、type を判定する。

### frontmatter がある場合（Markdown）
YAML frontmatter の `type` フィールドをそのまま使用する。

### frontmatter がない場合（全形式共通）
内容を分析し、以下の type 候補から適切なものをユーザーに提案する。複数当てはまりそうな場合は候補を2〜3個提示して選んでもらう。

| type | 判定のヒント |
|------|-------------|
| `report` | 調査結果、分析、問題報告、技術文書 |
| `minutes` | 会議、参加者リスト、決定事項、TODO |
| `knowledge-transfer` | KT、引き継ぎ、ナレッジ共有、伝達者・受領者 |
| `comparison` | 複数案の比較、メリット/デメリット |
| `presentation` | プレゼン、スライド、説明会 |
| `wbs` | 作業分解、スケジュール、タスク一覧、期間 |
| `roadmap` | ロードマップ、マイルストーン、フェーズ計画 |

提案の例:
> この文書は調査結果をまとめた内容に見えます。以下のレイアウトから選んでください:
> 1. **report** — 縦スクロール型レポート（おすすめ）
> 2. **presentation** — スライド型プレゼン
>
> どれがいいですか？

### type 一覧とスケルトン HTML

| type | レイアウト | スケルトン HTML |
|---|---|---|
| `report`（デフォルト） | 縦スクロール | `references/skeleton-report.html` |
| `minutes` | 縦スクロール（議事録固有コンポーネント） | `references/skeleton-minutes.html` |
| `knowledge-transfer` | 縦スクロール（KT固有コンポーネント） | `references/skeleton-knowledge-transfer.html` |
| `comparison` | カードグリッド | `references/skeleton-comparison.html` |
| `presentation` (slide) | 横スライド遷移 | `references/skeleton-slide.html` |
| `presentation` (spa) | SPA型カードナビ | `references/skeleton-spa.html` |
| `wbs` | 4パターンから選択 | `references/skeleton-wbs-*.html`（下記参照） |
| `roadmap` | 5パターンから選択 | `references/skeleton-roadmap-*.html`（下記参照） |

- type が決まらない場合は `report` として扱う
- `type: presentation` の場合、`layout` フィールドで形式を決定:
  - `layout: slide` → 横スライド型（左右矢印ナビ）
  - `layout: spa` → SPA型（カードナビゲーション）
- `type: wbs` の場合、`layout` フィールドでパターンを決定（下記参照）
- `type: roadmap` の場合、`layout` フィールドでパターンを決定（下記参照）
- **すべての type でスケルトン HTML をお手本として読み込み、同じ構造・CSS で生成する**
- **Mermaid.js の使用は禁止** — ガントチャート・タイムライン等はすべて純粋な CSS/HTML で実装する

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
   3. ユーザーが希望した場合、`start` コマンドでスケルトン HTML をブラウザで開く
   4. ユーザーが選択したパターンで変換を進める
3. スケルトン HTML 内の `.pattern-banner`（固定バナー）と `body { padding-top: 44px }` はプレビュー識別用。生成する HTML には含めない

---

## Phase 3: HTML変換ルール

### 共通の変換手順（全 type 共通）

1. **Phase 1.5 で特定した type に対応するスケルトン HTML を読み込む**
2. スケルトンの HTML 構造（タグ、クラス名、ネスト）を**そのまま踏襲**する
3. スケルトンの CSS（デザイントークン、コンポーネント数値）を**そのまま使用**する
4. 入力ドキュメントの内容をスケルトンの構造に忠実にマッピングする

### type ごとの構造マッピング

`references/type-mappings.md` を参照し、**該当 type のセクションだけ**を読むこと。
各 type のドキュメント → HTML 対応表、遅延時の表現ルールがまとまっている。

### 内容忠実性ルール（厳守）

1. **原文テキストを一字一句改変しない** — 省略・要約・言い換え禁止
2. **原文にないテキストを追加しない** — 特にサマリー文の捏造は厳禁
3. **テーブルの列を省略しない** — 全列・全行を忠実に変換
4. **括弧内注釈を省略しない** — `✅（オプションツール経由）` 等の補足情報は必須
5. **人名のフルネーム（英語名含む）を保持** — 議事録の出席者記録は正確性が最重要
6. **セクション番号を保持** — `## 1.`〜`## 7.` 等の番号は`<h2>`に含める
7. **特殊文字を統一** — `⚠️`（U+26A0 + U+FE0F emoji variant）で統一、plain `⚠` は不可

### 除外ルール（厳守）

入力ドキュメントにはヘッダ・フッタ・メタ情報など目立たない箇所に機械的な注記が含まれることがある。
以下に該当する情報は**HTMLに一切含めない**こと。変換時にドキュメント全体（特に冒頭・末尾・メタ情報周辺）を精査すること。

1. **AI生成に関する文言を除外する**
   - 「AIが作成」「AI文字起こし」「自動生成」「ChatGPTで作成」「Copilotで生成」等の記述はHTMLに含めない
   - 「録画から作成」「文字起こしベース」「自動議事録」等も同様に除外

2. **人間ではない参加者を除外する**
   - 「スピーカー」「録画者」「Recording Bot」「Transcription」「Microsoft Teams」「Notetaker」等、明らかに人物ではないものは参加者リストに含めない
   - 判断基準: 固有の人名（姓名）を持たないエントリはすべて除外対象

これらの情報はドキュメントの**ヘッダ・フッタ・メタ情報テーブルなど気づきにくい場所**に記載されていることが多い。変換前にドキュメントの先頭と末尾を必ず確認すること。

---

## リファレンス

| ファイル | 内容 | いつ読むか |
|---------|------|-----------|
| `references/design-tokens.md` | CSS変数、フォント、コンポーネント数値、バッジ注釈パターン | Phase 1（CSS解析）のとき |
| `references/type-mappings.md` | type別のドキュメント → HTML 構造マッピング、遅延時表現ルール | Phase 3（HTML変換）のとき — 該当 type のセクションだけ読む |
| `references/skeleton-report.html` | report のお手本HTML — 縦スクロール型レポート | type: report のとき |
| `references/skeleton-minutes.html` | minutes のお手本HTML — 議事録（参加者・決定事項・TODO） | type: minutes のとき |
| `references/skeleton-knowledge-transfer.html` | knowledge-transfer のお手本HTML — KT（伝達者・確認事項・フォローアップ） | type: knowledge-transfer のとき |
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
