---
name: screenshot-reader
description: スクリーンショットのファイルを特定するスキル。C:\Users\admin\Pictures\Screenshots フォルダから最新の画像を特定しファイル名を表示する。画像の読み込みはユーザーの調査依頼時に初めて行う。「スクショ」「スクリーンショット」「画面キャプチャ」「/screenshot-reader」と依頼されたときに使用する。
---

# Screenshot Reader

## スクリーンショットフォルダ

- パス: `C:\Users\admin\Pictures\Screenshots`

## 基本方針

### 特定のみ（/screenshot-reader だけ実行された場合）
1. Bash で `ls -t "C:/Users/admin/Pictures/Screenshots/"*.png | head -1` を実行
2. **ファイル名だけ**をコンソールに表示する（パスは内部で保持）
3. **画像は Read しない（コンテキストに読み込まない）**
4. ユーザーは続けて `/screenshot-reader` を実行して追加画像を指定する場合がある

### 特定＋調査（「スクショのエラー確認して」等、調査依頼を含む場合）
1. Bash で `ls -t "C:/Users/admin/Pictures/Screenshots/"*.png | head -1` を実行して最新ファイルのパスを特定
2. そのまま Read で画像を読み込む
3. 画像の内容に基づいて調査・回答する

## 引数の扱い

- 引数なし → 最新1枚を特定
- 数字（例: `3`）→ 新しい順で3番目を特定。`ls -t ... | wc -l` でファイル数を確認し、指定数より少ない場合は「N枚しかありません」と伝える
- ファイル名 → `C:/Users/admin/Pictures/Screenshots/` を先頭に付けて特定
- フルパス → そのまま特定
- 「最新3枚」等 → Bash で `ls -t ... | head -N` で必要な数だけ特定して一覧表示。ファイル数が足りない場合は実際にある分だけ表示する

