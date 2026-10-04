#!/usr/bin/env python3
"""原稿の簡易チェック(文字数、章ごとの分量、表記ゆれ、長文)。

使い方: python3 kindle/tools/check_manuscript.py kindle/books/<book-id>
"""
import re
import sys
from pathlib import Path

LONG_SENTENCE = 100  # 1文の文字数がこれを超えたら警告
ALERTS = [
    (r"[ｱ-ﾝ]", "半角カタカナ"),
    (r"([^\d])\.{3}([^\d.])", "三点リーダは「……」を推奨"),
    (r"！！|？？", "感嘆符・疑問符の連続"),
    (r"[ \t]+$", "行末の空白"),
    (r"【要入力】", "未記入の枠(【要入力】)が残っている"),
    (r"要確認", "要確認の印が残っている"),
    (r"(?:ので|から|が)、.*(?:ので|から|が)、.*(?:ので|から|が)、", "接続が3回以上続く長文"),
]


def main(book: Path):
    files = sorted((book / "chapters").glob("*.md"))
    if not files:
        sys.exit("chapters/*.md がありません")
    total = 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        body = re.sub(r"^#.*$", "", text, flags=re.M)
        n = len(re.sub(r"\s", "", body))
        total += n
        print(f"{f.name}: {n:,}文字")
        for i, line in enumerate(text.splitlines(), 1):
            for pat, msg in ALERTS:
                if re.search(pat, line):
                    print(f"  L{i}: {msg}")
            for s in re.split(r"[。!?！？]", line):
                if len(s) > LONG_SENTENCE:
                    print(f"  L{i}: 1文が長い({len(s)}文字): {s[:30]}…")
    print(f"合計: {total:,}文字")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
