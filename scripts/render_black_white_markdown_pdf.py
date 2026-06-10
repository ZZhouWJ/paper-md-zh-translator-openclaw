#!/usr/bin/env python3
import argparse
import html
import re
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


FONT = "PaperZhFont"
FALLBACK_FONT = "STSong-Light"
FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
]


def register_font() -> str:
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            try:
                pdfmetrics.registerFont(TTFont(FONT, candidate))
                return FONT
            except Exception:
                continue
    pdfmetrics.registerFont(UnicodeCIDFont(FALLBACK_FONT))
    return FALLBACK_FONT


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


def clean_inline(text: str) -> str:
    text = html.escape(text.strip())
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return text


def parse_blocks(markdown: str):
    lines = markdown.splitlines()
    blocks = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue
        image_match = re.match(r"!\[(.*?)\]\((.*?)\)", stripped)
        if image_match:
            blocks.append(("image", image_match.groups()))
            i += 1
            continue
        if stripped.startswith("|") and i + 1 < len(lines) and is_separator(lines[i + 1].strip()):
            rows = [split_table_row(stripped)]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_table_row(lines[i].strip()))
                i += 1
            blocks.append(("table", rows))
            continue
        if stripped.startswith("#"):
            level = min(len(stripped) - len(stripped.lstrip("#")), 6)
            blocks.append((f"h{level}", stripped[level:].strip()))
            i += 1
            continue
        if stripped.startswith("- "):
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(lines[i].strip()[2:].strip())
                i += 1
            blocks.append(("bullets", items))
            continue
        paragraph = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if not nxt or nxt.startswith("#") or nxt.startswith("- ") or nxt.startswith("|") or re.match(r"!\[.*?\]\(.*?\)", nxt):
                break
            paragraph.append(nxt)
            i += 1
        blocks.append(("paragraph", " ".join(paragraph)))
    return blocks


def styles(font_name: str):
    sample = getSampleStyleSheet()
    base = ParagraphStyle(
        "Base",
        parent=sample["Normal"],
        fontName=font_name,
        fontSize=10.5,
        leading=16,
        textColor=colors.black,
        backColor=colors.white,
        spaceAfter=6,
        wordWrap="CJK",
    )
    title = ParagraphStyle(
        "Title",
        parent=base,
        fontName=font_name,
        fontSize=19,
        leading=25,
        alignment=1,
        spaceAfter=14,
    )
    h2 = ParagraphStyle("H2", parent=base, fontName=font_name, fontSize=15, leading=20, spaceBefore=10, spaceAfter=7)
    h3 = ParagraphStyle("H3", parent=base, fontName=font_name, fontSize=12.5, leading=17, spaceBefore=8, spaceAfter=5)
    h4 = ParagraphStyle("H4", parent=base, fontName=font_name, fontSize=11.2, leading=16, spaceBefore=6, spaceAfter=4)
    table_cell = ParagraphStyle("TableCell", parent=base, fontName=font_name, fontSize=7.2, leading=9.4, spaceAfter=0)
    table_head = ParagraphStyle("TableHead", parent=table_cell, fontName=font_name, fontSize=7.2, leading=9.4)
    bullet = ParagraphStyle("Bullet", parent=base, leftIndent=8, firstLineIndent=0)
    return {
        "base": base,
        "title": title,
        "h2": h2,
        "h3": h3,
        "h4": h4,
        "table_cell": table_cell,
        "table_head": table_head,
        "bullet": bullet,
    }


def col_widths(rows, available_width):
    ncols = max(len(row) for row in rows)
    weights = [1] * ncols
    for row in rows:
        for idx in range(ncols):
            text = row[idx] if idx < len(row) else ""
            cjk = sum(1 for ch in text if ord(ch) > 127)
            weights[idx] = max(weights[idx], cjk * 1.6 + max(1, len(text) - cjk))
    total = sum(weights)
    widths = [available_width * weight / total for weight in weights]
    min_width = 18 * mm
    widths = [max(min_width, width) for width in widths]
    scale = available_width / sum(widths)
    return [width * scale for width in widths]


def image_flowable(src: str, alt: str, md_dir: Path, available_width: float, style_map):
    path = Path(src)
    if not path.is_absolute():
        path = md_dir / path
    if not path.exists():
        return Paragraph(f"[missing image: {clean_inline(src)}]", style_map["base"])
    with PILImage.open(path) as im:
        width_px, height_px = im.size
    # Crops are rendered at 200 dpi by crop_region.py. Preserve the natural
    # physical size for small equation crops instead of upscaling every image.
    natural_width = width_px / 200.0 * 72.0
    width = min(available_width, 160 * mm, natural_width)
    height = width * height_px / max(width_px, 1)
    max_height = 210 * mm
    if height > max_height:
        height = max_height
        width = height * width_px / max(height_px, 1)
    flow = Image(str(path), width=width, height=height)
    flow.hAlign = "CENTER"
    return flow


def build_story(markdown: str, md_dir: Path, doc, style_map):
    story = []
    for kind, payload in parse_blocks(markdown):
        if kind == "h1":
            story.append(Paragraph(clean_inline(payload), style_map["title"]))
        elif kind == "h2":
            story.append(Paragraph(clean_inline(payload), style_map["h2"]))
        elif kind == "h3":
            story.append(Paragraph(clean_inline(payload), style_map["h3"]))
        elif kind.startswith("h"):
            story.append(Paragraph(clean_inline(payload), style_map["h4"]))
        elif kind == "paragraph":
            story.append(Paragraph(clean_inline(payload), style_map["base"]))
        elif kind == "bullets":
            items = [ListItem(Paragraph(clean_inline(item), style_map["bullet"])) for item in payload]
            story.append(ListFlowable(items, bulletType="bullet", leftIndent=12, bulletFontName=style_map["base"].fontName))
            story.append(Spacer(1, 2 * mm))
        elif kind == "image":
            alt, src = payload
            story.append(Spacer(1, 3 * mm))
            story.append(image_flowable(src, alt, md_dir, doc.width, style_map))
            story.append(Spacer(1, 3 * mm))
        elif kind == "table":
            rows = payload
            ncols = max(len(row) for row in rows)
            normalized = [row + [""] * (ncols - len(row)) for row in rows]
            data = []
            for row_idx, row in enumerate(normalized):
                cell_style = style_map["table_head"] if row_idx == 0 else style_map["table_cell"]
                data.append([Paragraph(clean_inline(cell), cell_style) for cell in row])
            table = Table(data, colWidths=col_widths(normalized, doc.width), repeatRows=1, splitByRow=1)
            table.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (-1, -1), style_map["base"].fontName),
                        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                        ("GRID", (0, 0), (-1, -1), 0.4, colors.black),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 3),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                        ("TOPPADDING", (0, 0), (-1, -1), 3),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            story.append(table)
            story.append(Spacer(1, 4 * mm))
    return story


def draw_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(colors.black)
    canvas.setFont(doc.font_name, 8)
    canvas.drawCentredString(A4[0] / 2, 10 * mm, str(doc.page))
    canvas.restoreState()


def main():
    parser = argparse.ArgumentParser(description="Render Markdown to a searchable black-on-white A4 PDF.")
    parser.add_argument("--md", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--title")
    args = parser.parse_args()

    md_path = Path(args.md)
    out_path = Path(args.out)
    font_name = register_font()
    style_map = styles(font_name)
    markdown = md_path.read_text(encoding="utf-8")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        title=args.title or md_path.stem,
        author="Codex",
    )
    doc.font_name = font_name
    story = build_story(markdown, md_path.parent, doc, style_map)
    doc.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)
    print(f"saved {out_path}")


if __name__ == "__main__":
    main()
