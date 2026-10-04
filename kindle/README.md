# Kindle出版ツールキット

原稿(Markdown)から Kindle 用 EPUB を作り、企画・執筆・校正・KDP登録までを Claude のスキルで回すための一式です。

## 構成
- `tools/build_epub.py` Markdown → EPUB3(縦書き対応、表紙対応)
- `tools/check_manuscript.py` 文字数・表記ゆれ・長文の簡易チェック
- `books/_template/` 新しい本のひな形(コピーして使う)
- `docs/` 市場メモ、出版チェックリスト
- `../.claude/skills/kindle-*` 専用スキル(市場調査/企画/下書き/校正/KDP登録情報)

## 使い方
```bash
pip install markdown
cp -r kindle/books/_template kindle/books/my-first-book
# book.json と chapters/*.md を編集
python3 kindle/tools/check_manuscript.py kindle/books/my-first-book
python3 kindle/tools/build_epub.py kindle/books/my-first-book   # dist/*.epub
```

## 流れ
`kindle-market-research` → `kindle-outline` → `kindle-draft` → `kindle-proofread` → ビルド → `kindle-kdp-listing` → KDPで公開

## 注意
- 生成したEPUBは Kindle Previewer などで必ず表示確認する(自作ビルダーのため)。
- KDPの条件は変わるため、価格・表紙・規約は公式ヘルプで確認する。
