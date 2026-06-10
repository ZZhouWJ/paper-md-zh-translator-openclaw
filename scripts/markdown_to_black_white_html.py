#!/usr/bin/env python3
import argparse
import html
import re
from pathlib import Path


def split_table_row(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    cells, current, in_code, escaped = [], [], False, False
    for ch in body:
        if escaped:
            current.append(ch)
            escaped = False
            continue
        if ch == "\\":
            current.append(ch)
            escaped = True
            continue
        if ch == "`":
            in_code = not in_code
            current.append(ch)
            continue
        if ch == "|" and not in_code:
            cells.append("".join(current).strip())
            current = []
            continue
        current.append(ch)
    cells.append("".join(current).strip())
    return cells


def is_separator(line: str) -> bool:
    cells = split_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def inline(text: str) -> str:
    text = html.escape(text.strip())
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def image_src(src: str, md_dir: Path) -> str:
    src = src.strip()
    if re.match(r"^[a-z]+://", src):
        return html.escape(src)
    path = Path(src)
    if not path.is_absolute():
        path = md_dir / path
    return path.resolve().as_uri()


def convert(markdown: str, md_dir: Path) -> str:
    lines = markdown.splitlines()
    out = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue
        image_match = re.match(r"!\[(.*?)\]\((.*?)\)", stripped)
        if image_match:
            alt, src = image_match.groups()
            out.append(f'<figure><img src="{image_src(src, md_dir)}" alt="{html.escape(alt)}"></figure>')
            i += 1
            continue
        if stripped.startswith("|") and i + 1 < len(lines) and is_separator(lines[i + 1].strip()):
            rows = [split_table_row(stripped)]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_table_row(lines[i].strip()))
                i += 1
            out.append("<table>")
            for row_idx, row in enumerate(rows):
                tag = "th" if row_idx == 0 else "td"
                out.append("<tr>" + "".join(f"<{tag}>{inline(cell)}</{tag}>" for cell in row) + "</tr>")
            out.append("</table>")
            continue
        if stripped.startswith("#"):
            level = min(len(stripped) - len(stripped.lstrip("#")), 6)
            text = stripped[level:].strip()
            out.append(f"<h{level}>{inline(text)}</h{level}>")
            i += 1
            continue
        if stripped.startswith("- "):
            out.append("<ul>")
            while i < len(lines) and lines[i].strip().startswith("- "):
                out.append(f"<li>{inline(lines[i].strip()[2:])}</li>")
                i += 1
            out.append("</ul>")
            continue
        paragraph = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if not nxt or nxt.startswith("#") or nxt.startswith("- ") or nxt.startswith("|") or re.match(r"!\[.*?\]\(.*?\)", nxt):
                break
            paragraph.append(nxt)
            i += 1
        out.append(f"<p>{inline(' '.join(paragraph))}</p>")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to minimal black-on-white HTML.")
    parser.add_argument("--md", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--title")
    args = parser.parse_args()

    md_path = Path(args.md)
    out_path = Path(args.out)
    markdown = md_path.read_text(encoding="utf-8")
    title = args.title or md_path.stem
    body = convert(markdown, md_path.parent)
    css = """
html, body { background: white; color: black; }
body {
  font-family: "Arial Unicode MS", "PingFang SC", "Songti SC", "Noto Sans CJK SC", serif;
  font-size: 12pt;
  line-height: 1.62;
  margin: 32px auto;
  max-width: 820px;
}
h1, h2, h3, h4, h5, h6 { color: black; background: white; page-break-after: avoid; }
h1 { font-size: 22pt; text-align: center; margin: 0 0 24px; }
h2 { font-size: 17pt; margin-top: 28px; }
h3 { font-size: 14pt; margin-top: 20px; }
p { margin: 0 0 12px; text-align: justify; }
img { display: block; max-width: 100%; height: auto; margin: 16px auto 8px; }
figure { margin: 18px 0; padding: 0; }
table { width: 100%; border-collapse: collapse; margin: 16px 0; page-break-inside: avoid; }
th, td { border: 1px solid black; padding: 5px; vertical-align: top; color: black; background: white; }
code { color: black; background: white; }
@page { size: A4; margin: 22mm 18mm; }
"""
    html_text = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>{css}</style>
</head>
<body>
{body}
</body>
</html>
"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_text, encoding="utf-8")
    print(f"saved {out_path}")


if __name__ == "__main__":
    main()
