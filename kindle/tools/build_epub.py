#!/usr/bin/env python3
"""Markdown原稿から Kindle(KDP)向け EPUB3 を生成する。

使い方:
    python3 kindle/tools/build_epub.py kindle/books/<book-id>

必要なもの: Python 3.9+ と `pip install markdown`
入力: <book>/book.json, <book>/chapters/*.md (ファイル名順), <book>/cover.jpg (任意)
出力: <book>/dist/<book-id>.epub
"""
import json
import re
import sys
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

import markdown

CSS = """\
body { line-height: 1.8; margin: 0; }
h1 { font-size: 1.5em; margin: 2em 0 1em; page-break-before: always; }
h2 { font-size: 1.2em; margin: 1.5em 0 0.8em; }
p { margin: 0; text-indent: 1em; }
blockquote { margin: 1em 1.5em; font-size: 0.95em; }
img { max-width: 100%; }
"""

XHTML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{lang}" xml:lang="{lang}">
<head><meta charset="UTF-8"/><title>{title}</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>
{body}
</body>
</html>
"""


def load_chapters(book_dir: Path):
    files = sorted((book_dir / "chapters").glob("*.md"))
    if not files:
        sys.exit(f"章ファイルが見つかりません: {book_dir / 'chapters'}")
    chapters = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        m = re.search(r"^#\s+(.+)$", text, re.M)
        title = m.group(1).strip() if m else f.stem
        html = markdown.markdown(text, extensions=["extra", "sane_lists"])
        chapters.append((f.stem, title, html))
    return chapters


def build(book_dir: Path):
    meta = json.loads((book_dir / "book.json").read_text(encoding="utf-8"))
    lang = meta.get("language", "ja")
    title = meta["title"]
    book_id = meta.get("id", book_dir.name)
    uid = meta.get("identifier") or f"urn:uuid:{uuid.uuid4()}"
    vertical = meta.get("vertical", False)
    chapters = load_chapters(book_dir)
    remaining = sum(h.count("【要入力】") + h.count("要確認") for _, _, h in chapters)
    if remaining:
        print(f"警告: 未記入の枠・要確認が {remaining} 箇所残っています(公開前に解消してください)")

    css = CSS
    if vertical:  # 縦書き(右開き)
        css += "html { writing-mode: vertical-rl; -epub-writing-mode: vertical-rl; }\n"

    out_dir = book_dir / "dist"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"{book_id}.epub"

    cover = next((p for p in (book_dir / "cover.jpg", book_dir / "cover.png") if p.exists()), None)

    manifest, spine, nav_items = [], [], []
    for stem, ctitle, html in chapters:
        manifest.append(f'<item id="{stem}" href="{stem}.xhtml" media-type="application/xhtml+xml"/>')
        spine.append(f'<itemref idref="{stem}"/>')
        nav_items.append(f'<li><a href="{stem}.xhtml">{escape(ctitle)}</a></li>')

    nav = XHTML.format(
        lang=lang, title="目次",
        body=f'<nav epub:type="toc" id="toc"><h1>目次</h1><ol>{"".join(nav_items)}</ol></nav>',
    )
    modified = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cover_meta = '<meta name="cover" content="cover-image"/>' if cover else ""
    cover_item = (
        f'<item id="cover-image" href="{cover.name}" media-type="image/{"png" if cover.suffix == ".png" else "jpeg"}" properties="cover-image"/>'
        if cover else ""
    )
    opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="{lang}">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="bookid">{escape(uid)}</dc:identifier>
<dc:title>{escape(title)}</dc:title>
<dc:creator>{escape(meta.get("author", ""))}</dc:creator>
<dc:language>{lang}</dc:language>
<dc:description>{escape(meta.get("description", ""))}</dc:description>
<meta property="dcterms:modified">{modified}</meta>
{cover_meta}
</metadata>
<manifest>
<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
<item id="css" href="style.css" media-type="text/css"/>
{cover_item}
{chr(10).join(manifest)}
</manifest>
<spine{' page-progression-direction="rtl"' if vertical else ''}>
<itemref idref="nav"/>
{chr(10).join(spine)}
</spine>
</package>
"""
    container = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>
"""
    with zipfile.ZipFile(out, "w") as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", opf, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/nav.xhtml", nav, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/style.css", css, compress_type=zipfile.ZIP_DEFLATED)
        if cover:
            z.write(cover, f"OEBPS/{cover.name}", compress_type=zipfile.ZIP_DEFLATED)
        for stem, ctitle, html in chapters:
            z.writestr(
                f"OEBPS/{stem}.xhtml",
                XHTML.format(lang=lang, title=escape(ctitle), body=html),
                compress_type=zipfile.ZIP_DEFLATED,
            )
    print(f"生成しました: {out} ({out.stat().st_size:,} bytes, {len(chapters)}章)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    build(Path(sys.argv[1]))
