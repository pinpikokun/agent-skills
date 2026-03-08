# マルチエージェントレビュー仕様

## Phase 3: レビューエージェント（3つ並列起動）

### Agent 1: 内容チェック（Content Accuracy）

- MDの全セクション・全テーブル行・全ワークフロー手順がHTMLに存在するか
- テキストの省略・改変・追加がないか
- テーブル列の欠落がないか
- 括弧内注釈が保持されているか
- 人名・日時の正確性

### Agent 2: デザインチェック（Design Consistency）

- CSS変数が参照HTMLと一致しているか
- フォントファミリー（Noto Serif JP / Noto Sans JP）が正しいか
- コンポーネントの数値（font-size, padding, margin, border-radius）が厳密に一致しているか
- Hero / Section / Callout / Conclusion / Footer のパターンが踏襲されているか
- レスポンシブ（@media）のブレークポイントと値が一致しているか

### Agent 3: 校正チェック（Proofreading & Structure）

- HTML構造の妥当性（タグの開閉、セマンティックHTML）
- 見出し階層（h1 > h2 > h3）の整合性
- 特殊文字（⚠️, ✅, ❌, ✓, ★）の一貫性
- テーブル構造（thead/tbody, 列数の一致）
- 日本語テキストの誤字・文法
- セクションラベル英語テキストと内容の対応

### type 別の追加チェック項目

#### type: comparison

- Agent 1（内容）: `##` の数だけ comparison-column が存在するか、`###` の数だけ comparison-card が存在するか
- Agent 2（デザイン）: `.comparison-grid` / `.comparison-card` / `.card-price-badge` のCSS値が design-tokens.md と一致するか、レスポンシブ対応（1カラムフォールバック）が正しいか
- Agent 3（校正）: カードの並び順がMDの順序と一致するか、価格バッジのフォーマットが統一されているか

#### type: presentation (slide)

- Agent 1（内容）: `##` の数だけスライドが存在するか、各スライドの内容が完全か
- Agent 2（デザイン）: skeleton-slide.html の構造（`.slide-nav`, `.slides-wrapper`, `.slide-arrow`, `.slide-progress`）が踏襲されているか、CSS変数が design-tokens.md と一致するか
- Agent 3（校正）: スライド番号の整合性、キーボードナビゲーション（矢印キー）が動作するか、プログレスバーの計算が正しいか

#### type: presentation (spa)

- Agent 1（内容）: トップページのカード数とページ数が一致するか、各ページの内容が完全か
- Agent 2（デザイン）: skeleton-spa.html の構造（`.hero`, `.nav-cards`, `.page-detail`, `.back-link`）が踏襲されているか、CSS変数が design-tokens.md と一致するか
- Agent 3（校正）: ページ遷移の JavaScript が正しいか、「トップに戻る」リンクが全ページにあるか、ハッシュナビゲーションが動作するか

#### type: report

- Agent 1（内容）: skeleton-report.html の全コンポーネント（hero, section, callout, workflow, overview-cards, conclusion, footer）が正しく使われているか
- Agent 2（デザイン）: skeleton-report.html のCSS（`.hero`, `.section`, `.callout`, `.overview-card`, `.conclusion`）が踏襲されているか
- Agent 3（校正）: `.section-label` の英語テキストが各セクション内容と対応しているか

#### type: minutes

- Agent 1（内容）: 参加者リスト（`.participants`）が全員含まれているか、決定事項（`.decisions`）が漏れなく記載されているか、アクション項目（`.action-items`）に担当と期限が含まれているか
- Agent 2（デザイン）: skeleton-minutes.html の議事録固有コンポーネント（`.participant-tag`, `.decision-item`, `.action-item`）が踏襲されているか
- Agent 3（校正）: ファシリテーターの `.participant-tag.facilitator` スタイルが正しいか、アクション項目のグリッドレイアウトが正しいか

#### type: wbs

- Agent 1（内容）: WBS テーブルの全行がMDに存在するか、CSS ガントチャートのタスクバーがテーブル行と1対1で対応しているか、進捗サマリーの数値がテーブルと整合しているか
- Agent 2（デザイン）: skeleton-wbs.html の構造（`.status-cards`, `.wbs-gantt`, `.phase-row`, `.badge`）が踏襲されているか、CSS変数（`--day-w`, `--left-w` 等）がスケルトンと一致するか
- Agent 3（校正）: WBS番号（1.1, 1.2, 2.1...）の連番が正しいか、ステータスバッジ（`.badge.done` / `.badge.in-progress` / `.badge.not-started` / `.badge.delayed`）が内容と一致するか、遅延タスクのバーが赤色（`var(--accent-red)`）で表示されているか

---

## Phase 4: 統合判定（2つ並列起動）

### Agent 4: 統合判定（Synthesis）

- 3レポートの全findingsを MUST FIX / SHOULD FIX / SKIP に分類
- 判定基準:
  - MUST FIX: 内容の改変・欠落・追加、アクセシビリティ破綻
  - SHOULD FIX: デザイン数値の乖離、軽微な省略
  - SKIP: 主観的好み、4px以下の差、保守性のみの問題

### Agent 5: クロスバリデーション（Cross-Validation）

- 3レポート間の矛盾を検出
- 重要度の再評価（過大/過小評価の是正）
- 最小限の修正セットの提案
- 3エージェントが見逃した問題の指摘

---

## Phase 5: 修正適用

統合判定の結果に基づき修正を適用する。

### 修正時の注意事項

1. **editツールでテーブル行を編集する際は `<tr>` の区切りを壊さない**
   - 複数行にまたがるeditは行のマージ事故を起こしやすい
   - 安全策: テーブル全体（`<tbody>`〜`</tbody>`）を一括置換する

2. **バッジ内に長いテキストを入れない**
   - バッジ + `<br><small class="badge-note">` パターンを使う（`design-tokens.md` 参照）

3. **修正後は最終検証エージェントで全項目PASSを確認する**

### 最終検証チェックリスト

1. Hero: フルネーム参加者情報
2. テーブル: 全列・全行・注釈の存在
3. ワークフロー図: 全ステップの内容一致
4. Callout: テキストの完全一致
5. テーブルヘッダー: 原文通り
6. 次回アクション: 全列（期限含む）の存在
7. 捏造テキストが存在しないこと
8. 見出し階層の整合性（h1 > h2 > h3）
9. 特殊文字の統一（⚠️ emoji variant）
10. セクション番号の保持
11. セマンティックHTML（ul/li統一）
12. CSSデザイン値の参照HTMLとの一致

---

## エージェント起動パターン

```
[Phase 3] 並列起動（mode: background）
  ├─ Agent 1: Content Accuracy   (general-purpose)
  ├─ Agent 2: Design Consistency  (general-purpose)
  └─ Agent 3: Proofreading        (general-purpose)

  ↓ 全完了を待つ

[Phase 4] 並列起動（mode: background）
  ├─ Agent 4: Synthesis           (general-purpose)
  └─ Agent 5: Cross-Validation    (general-purpose)

  ↓ 全完了を待つ

[Phase 5] 修正適用 → 最終検証エージェント（sync）
```
