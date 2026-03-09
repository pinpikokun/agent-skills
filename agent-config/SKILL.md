---
name: agent-config
description: AI エージェント設定ファイル（AGENTS.md, CLAUDE.md, .cursorrules 等）の作成・編集ルール。簡潔さの基準、スキルへの移行判断、ファイルごとの書式。設定ファイルの新規作成や内容見直し時に使用する。
---

# AI エージェント設定ファイル ガイド

AGENTS.md や CLAUDE.md など、AI コーディングエージェント向けの設定ファイルを作成・編集する際のルールを定義する。

## 対象ファイル一覧

| ファイル | 対象エージェント | 配置場所 |
|:---|:---|:---|
| `AGENTS.md` | GitHub Copilot（コーディングエージェント） | リポジトリルート |
| `CLAUDE.md` | Claude Code（Anthropic） | リポジトリルート |
| `.cursorrules` | Cursor | リポジトリルート |
| `copilot-instructions.md` | GitHub Copilot Chat | リポジトリルート |
| `.github/copilot-instructions.md` | GitHub Copilot Chat（公式配置） | `.github/` |

## 書くべき内容

プロジェクトに該当するものだけを書く。すべて埋める必要はない。

1. **技術スタック** — 使用言語・フレームワーク・主要ライブラリ
   - 例: `Next.js 14, TypeScript, Prisma`
2. **コマンド** — ビルド・テスト・Lint の実行方法
   - 例: `npm run build`, `npm test`, `npm run lint`
3. **コーディング規約** — 命名規則、スタイル、フォーマット
   - 例: `camelCase 使用`、`アロー関数を優先`
4. **禁止事項** — やってはいけないこと
   - 例: `any 型禁止`、`console.log をコミットしない`
5. **応答言語** — エージェントの応答やコメントの言語
   - 例: `日本語で応答すること`

## 基本原則

### 簡潔に書く

設定ファイルはセッション開始時に**常時ロード**される。書いた分だけトークンを消費し続ける。

- 目標: **30 行以下**
- 上限目安: **50 行**
- ルール 1 つにつき 1 行が理想

```markdown
<!-- ✅ Good: 1 ルール 1 行 -->
- TypeScript で書く。any 型は使わない
- テストは Vitest を使用。`npm test` で実行
- 日本語で応答する

<!-- ❌ Bad: 説明が長い -->
- TypeScript を使用してください。TypeScript は型安全性を提供し、
  コードの品質を向上させます。any 型は型安全性を損なうため、
  使用を避けてください。代わりに具体的な型を定義するか、
  unknown 型を使用してください。
```

### スキルへの移行を検討する

以下に該当するルールは、設定ファイルではなく **AI エージェントスキル**（`.claude/skills/` 等）への移行を検討する。

- 特定の作業時にしか参照しないルール（例: マークダウンの書き方、コミットメッセージ規約）
- 具体例やテンプレートを含む長いルール
- 特定のツール・ライブラリに限定されたルール

> [!IMPORTANT]
> 設定ファイルが **50 行を超えている**、または特定作業に限定されたルールが含まれている場合は、スキルへの移行をユーザーに提案すること。

### 提案の例

```text
この設定ファイルが 50 行を超えています。
以下のルールは特定作業時にのみ必要なため、スキルに移行すると
常時のトークン消費を減らせます:

- マークダウンの書き方 → markdown-writing スキル
- コミットメッセージ規約 → git-safety スキル

移行しますか？
```

## ファイルごとの書式

### AGENTS.md / CLAUDE.md

Markdown 形式。見出しでセクションを分ける。

```markdown
# プロジェクト名

## 技術スタック
- Python 3.12, FastAPI, SQLAlchemy

## コマンド
- ビルド: `docker compose build`
- テスト: `pytest`
- Lint: `ruff check .`

## コーディング規約
- snake_case を使用
- docstring は Google スタイル

## 禁止事項
- `print()` デバッグをコミットしない
- `# type: ignore` を理由なく使わない

## 応答言語
- 日本語で応答する
```

### .cursorrules

Markdown またはプレーンテキスト。構造は AGENTS.md と同様。

### copilot-instructions.md / .github/copilot-instructions.md

Markdown 形式。GitHub Copilot Chat が参照する。書き方は AGENTS.md と同様だが、Copilot Chat 固有の指示（コード補完の方針など）を含められる。

## チェックリスト

- [ ] プロジェクトに該当する項目だけが書かれている
- [ ] 50 行以下に収まっている
- [ ] 1 ルール 1 行で簡潔に書かれている
- [ ] 長いルールや限定的なルールはスキルに移行済み
- [ ] 応答言語が指定されている

