# デザイントークン・コンポーネント仕様

## 必須踏襲デザイントークン（CSS変数）

```css
:root {
  --bg-primary: #faf9f7;
  --bg-card: #ffffff;
  --bg-warm: #f5f0eb;
  --bg-dark: #191919;
  --text-primary: #1a1a1a;
  --text-secondary: #6b6560;
  --text-light: #9a938d;
  --accent-warm: #c4704b;
  --accent-green: #2d7a5f;
  --accent-red: #b85450;
  --border: #e8e2db;
  --border-light: #f0ece7;
}
```

## 必須踏襲フォント

```css
font-family: 'Noto Sans JP' /* 本文 */
font-family: 'Noto Serif JP' /* 見出し h1, h2, h3, .card-title */
```

Google Fonts CDN:
```html
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&family=Noto+Sans+JP:wght@300;400;500;600&display=swap" rel="stylesheet">
```

## 必須踏襲コンポーネント数値（厳密一致）

| コンポーネント | プロパティ | 値 |
|---------------|-----------|-----|
| `.hero` | background | `var(--bg-dark)` |
| `.hero` | padding | `100px 0 80px` |
| `.hero::before` | background | `radial-gradient(circle, rgba(196,112,75,0.15) 0%, transparent 70%)` |
| `.hero h1` | font-size | `40px` |
| `.hero h1` | font-weight | `700` |
| `.hero h1` | line-height | `1.4` |
| `.hero-date` / hero meta | color | `rgba(255,255,255,0.45)` |
| `.hero-label` | font-size / letter-spacing / color | `12px` / `3px` / `var(--accent-warm)` |
| `.content` | max-width | `780px` |
| `.section` | padding | `72px 0` |
| `.section` | border-bottom | `1px solid var(--border-light)` |
| `.section-label` | font-size / letter-spacing | `11px` / `3px` |
| `.section h2` | font-size | `28px` |
| `.callout` | margin | `40px 0` |
| `.callout` | padding | `28px 32px` |
| `.callout.note` | border-left | `3px solid var(--accent-warm)` |
| `.callout.note` | background | `#fef8f0` |
| `.diagram` / `.workflow` | padding | `48px 40px` |
| `.diagram` / `.workflow` | border-radius | `16px` |
| `.diagram-title` | margin-bottom | `32px` |
| `.card-badge` | border-radius | `100px` |
| `.card-badge` | padding | `4px 12px` |
| `.card-badge.warn` | background / color | `#fef3ef` / `var(--accent-red)` |
| `.card-badge.good` | background / color | `#edf7f1` / `var(--accent-green)` |
| `.card-title` | margin-bottom | `8px` |
| `.overview-card` | border-radius | `16px` |
| `.overview-card` | padding | `36px 32px` |
| `.conclusion` | background | `var(--bg-dark)` |
| `.conclusion` | border-radius | `20px` |
| `.conclusion` | padding | `48px` |
| `.conclusion .action` | margin-top | `24px` |
| `.conclusion .action` | border-radius | `12px` |
| `.conclusion .action-label` | color | `var(--accent-warm)` |
| `.footer` | padding | `48px 0` |
| Mobile `@media (max-width: 640px)` `.hero h1` | font-size | `28px` |
| Mobile `.content` | padding | `0 24px` |
| Mobile `.diagram` | padding | `32px 20px` |
| Mobile `.conclusion` | padding | `32px 24px` |

## 追加コンポーネント（議事録用に拡張可）

内容に応じて以下を**同じデザインシステム**で追加してよい：
- `.callout.warning` — `background: #fef3ef; border-left: 3px solid var(--accent-red);`
- `.callout.improvement` — `background: #edf7f1; border-left: 3px solid var(--accent-green);`
- テーブル系（`.tool-table`, `.request-table`, `.appendix-table`）
- ワークフロー図（`.workflow-steps`, `.workflow-step`）
- データフロー図（`.dataflow-container`）

**重要:** 新しいコンポーネントを追加する際は、既存のCSS変数・カラーパレット・border-radius・font-size体系を逸脱しないこと。

## type 固有のコンポーネント

type 固有のコンポーネント（comparison のカード、WBS のガントチャート等）の CSS 値は各スケルトン HTML が正とする。design-tokens.md には書かない（二重管理を避けるため）。

---

## テーブルセル内の注釈表示パターン

バッジ内に長い注釈テキストを入れるとレイアウトが崩れる。以下のパターンを使う：

```html
<!-- バッジ + 注釈を分離表示 -->
<td>
  <span class="badge-yes">あり</span>
  <br><small class="badge-note">オプションツール経由</small>
</td>
```

```css
.tool-table .badge-note {
  display: block;
  font-size: 10px;
  font-weight: 300;
  color: var(--text-light);
  margin-top: 4px;
}
```
