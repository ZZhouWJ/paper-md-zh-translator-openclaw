#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

from pypdf import PdfReader


REFERENCES_RE = re.compile(r"^\s*(references|bibliography|literature cited)\s*$", re.I)
BACK_MATTER_RE = re.compile(
    r"^\s*(acknowledgements?|funding|data availability|code availability|"
    r"materials availability|author contributions?|competing interests?|"
    r"conflicts? of interest|ethics declarations?|supplementary information)\s*:?$",
    re.I,
)
CAPTION_RE = re.compile(r"^\s*((?:Figure|Fig\.?|Table)\s+[A-Za-z]?\d+[A-Za-z]?(?:\.\d+)?[\.:]?)\s*(.*)", re.I)
HEADING_RE = re.compile(r"^\s*(\d+(?:\.\d+)*)\s+([A-Z][A-Za-z0-9 ,:/()\-]{2,})\s*$")


def normalize_line(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def page_lines(page) -> list[str]:
    try:
        text = page.extract_text() or ""
    except Exception:
        text = ""
    return [normalize_line(line) for line in text.splitlines() if normalize_line(line)]


def line_is_equation_candidate(line: str) -> bool:
    if len(line) > 180 or len(line) < 4:
        return False
    if CAPTION_RE.match(line) or REFERENCES_RE.match(line) or BACK_MATTER_RE.match(line):
        return False
    math_chars = sum(1 for ch in line if ch in "=∑∏∫√≤≥≈≠±×÷∂αβγδθλμσπΩ∞{}[]_^")
    compare_ops = sum(1 for ch in line if ch in "=<>")
    if math_chars == 0 and compare_ops == 0:
        return False
    letters = sum(1 for ch in line if ch.isalpha())
    digits = sum(1 for ch in line if ch.isdigit())
    return (math_chars + compare_ops >= 1 and digits + letters <= max(90, len(line) * 0.9))


def first_index(lines, pattern):
    for idx, item in enumerate(lines):
        if pattern.match(item["text"]):
            return idx
    return None


def collect_captions(flat_lines):
    captions = []
    for idx, item in enumerate(flat_lines):
        match = CAPTION_RE.match(item["text"])
        if not match:
            continue
        label = match.group(1).strip().rstrip(":")
        tail = match.group(2).strip()
        caption_lines = [item["text"]]
        # Add a short continuation when the next line looks like sentence text, not a heading.
        for nxt in flat_lines[idx + 1 : idx + 3]:
            if nxt["page"] != item["page"]:
                break
            text = nxt["text"]
            if CAPTION_RE.match(text) or REFERENCES_RE.match(text) or BACK_MATTER_RE.match(text) or HEADING_RE.match(text):
                break
            if len(text) < 220:
                caption_lines.append(text)
        captions.append(
            {
                "label": label,
                "kind": "table" if label.lower().startswith("table") else "figure",
                "page": item["page"],
                "line_index": item["line_index"],
                "text": " ".join(caption_lines),
                "tail": tail,
            }
        )
    return captions


def main():
    parser = argparse.ArgumentParser(description="Extract text and simple structure from an extractable-text PDF.")
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--references-out")
    parser.add_argument("--back-matter-out")
    parser.add_argument("--min-total-chars", type=int, default=1200)
    parser.add_argument("--min-avg-page-chars", type=int, default=250)
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    reader = PdfReader(str(pdf_path))
    pages = []
    flat_lines = []

    for page_idx, page in enumerate(reader.pages, start=1):
        lines = page_lines(page)
        page_text = "\n".join(lines)
        pages.append(
            {
                "page": page_idx,
                "width": float(page.mediabox.width),
                "height": float(page.mediabox.height),
                "char_count": len(page_text),
                "text": page_text,
                "lines": lines,
            }
        )
        for line_idx, line in enumerate(lines):
            flat_lines.append({"page": page_idx, "line_index": line_idx, "text": line})

    total_chars = sum(page["char_count"] for page in pages)
    no_text_pages = [page["page"] for page in pages if page["char_count"] < 50]
    avg_page_chars = total_chars / max(len(pages), 1)

    ref_idx = first_index(flat_lines, REFERENCES_RE)
    back_idx = first_index(flat_lines, BACK_MATTER_RE)
    body_end_candidates = [idx for idx in [ref_idx, back_idx] if idx is not None]
    body_end = min(body_end_candidates) if body_end_candidates else len(flat_lines)

    body_lines = flat_lines[:body_end]
    back_matter_lines = []
    reference_lines = []
    if back_idx is not None:
        end = ref_idx if ref_idx is not None and ref_idx > back_idx else len(flat_lines)
        back_matter_lines = flat_lines[back_idx:end]
    if ref_idx is not None:
        reference_lines = flat_lines[ref_idx:]

    captions = collect_captions(flat_lines)
    equation_candidates = [
        {"page": item["page"], "line_index": item["line_index"], "text": item["text"]}
        for item in flat_lines
        if line_is_equation_candidate(item["text"])
    ]

    likely_bad = (
        total_chars < args.min_total_chars
        or avg_page_chars < args.min_avg_page_chars
        or (len(no_text_pages) / max(len(pages), 1)) > 0.25
    )

    result = {
        "source_pdf": str(pdf_path),
        "page_count": len(pages),
        "quality": {
            "total_chars": total_chars,
            "avg_page_chars": avg_page_chars,
            "no_text_pages": no_text_pages,
            "likely_bad_text_extraction": likely_bad,
            "stop_if_likely_bad": likely_bad,
        },
        "sections": {
            "references_start": flat_lines[ref_idx] if ref_idx is not None else None,
            "back_matter_start": flat_lines[back_idx] if back_idx is not None else None,
        },
        "captions": captions,
        "equation_candidates": equation_candidates,
        "body_text": "\n".join(item["text"] for item in body_lines),
        "back_matter_text": "\n".join(item["text"] for item in back_matter_lines),
        "references_text": "\n".join(item["text"] for item in reference_lines),
        "pages": pages,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.references_out:
        Path(args.references_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.references_out).write_text(result["references_text"], encoding="utf-8")
    if args.back_matter_out:
        Path(args.back_matter_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.back_matter_out).write_text(result["back_matter_text"], encoding="utf-8")

    print(json.dumps({"ok": not likely_bad, "quality": result["quality"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
