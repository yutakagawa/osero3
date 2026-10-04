---
name: kindle-draft
description: PLAN.md の章立てに沿って、Kindle本の各章を kindle/books/<book-id>/chapters/ にMarkdownで下書きする。「原稿を書いて」「第N章を書いて」と言われたら使う。
---

# Kindle原稿の下書き

## 前提
`kindle/books/<book-id>/PLAN.md` と `STYLE.md`(文体ガイド。なければ作る)を最初に読む。

## 手順
1. STYLE.md が無ければ、著者の文体サンプルや好みを聞いて作る(一人称、です・ます調、1文の長さ、禁止表現)。
2. 章ごとに `chapters/NN-slug.md` を作る。先頭は `# 章タイトル` の1行のみ。見出しは `##` 以下。
3. 各章の構造: 導入(問い)→ 本論(具体例・手順)→ まとめ(次にやること)。
4. 事実・数値・固有名詞は、確認できないものを断定しない。要確認箇所は `<!-- 要確認: ... -->` で残す。
5. 書き終えたら `python3 kindle/tools/check_manuscript.py kindle/books/<book-id>` で分量と表記を確認する。

## 守ること
- 他の書籍やWebの文章を転載・近い言い換えで流用しない。
- 医療・法律・投資など専門性の高い内容は、根拠と注意書きを入れる。
