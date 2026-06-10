#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from pypdf import PdfReader


def pdf_text_chars(path: Path) -> int:
    reader = PdfReader(str(path))
    total = 0
    for page in reader.pages:
        try:
            total += len(page.extract_text() or "")
        except Exception:
            pass
    return total


def main():
    parser = argparse.ArgumentParser(description="Validate paper-md-zh-translator deliverables.")
    parser.add_argument("--folder", required=True)
    parser.add_argument("--basename", required=True)
    parser.add_argument("--stage", choices=["working", "final"], default="working")
    parser.add_argument("--min-zh-text-chars", type=int, default=300)
    parser.add_argument("--min-summary-text-chars", type=int, default=200)
    args = parser.parse_args()

    folder = Path(args.folder)
    basename = args.basename
    final_pdfs = [
        folder / f"{basename}.pdf",
        folder / f"{basename}_zh.pdf",
        folder / f"{basename}_summary.pdf",
    ]
    working_artifacts = [
        folder / f"{basename}_zh.md",
        folder / f"{basename}_summary.md",
        folder / "assets",
        folder / "work",
        folder / "work" / "extracted_text.json",
        folder / "work" / "references.txt",
        folder / "work" / "untranslated_back_matter.md",
        folder / "work" / f"{basename}_zh.html",
    ]
    expected = final_pdfs + (working_artifacts if args.stage == "working" else [])
    errors = []
    warnings = []
    for path in expected:
        if not path.exists():
            errors.append(f"missing: {path}")

    zh_pdf = folder / f"{basename}_zh.pdf"
    summary_pdf = folder / f"{basename}_summary.pdf"
    zh_chars = pdf_text_chars(zh_pdf) if zh_pdf.exists() else 0
    summary_chars = pdf_text_chars(summary_pdf) if summary_pdf.exists() else 0
    if zh_pdf.exists() and zh_chars < args.min_zh_text_chars:
        errors.append(f"translated PDF has too little extractable text: {zh_chars}")
    if summary_pdf.exists() and summary_chars < args.min_summary_text_chars:
        errors.append(f"summary PDF has too little extractable text: {summary_chars}")

    asset_count = 0
    assets = folder / "assets"
    if assets.exists():
        asset_count = len(list(assets.glob("*.png")))
        if asset_count == 0:
            warnings.append("assets folder has no cropped figure/table/equation images")

    extra_entries = []
    if args.stage == "final" and folder.exists():
        allowed = {path.resolve() for path in final_pdfs}
        for child in folder.iterdir():
            if child.resolve() not in allowed:
                extra_entries.append(str(child))
        if extra_entries:
            errors.append("final folder contains non-PDF intermediate entries")

    result = {
        "ok": not errors,
        "stage": args.stage,
        "errors": errors,
        "warnings": warnings,
        "translated_pdf_text_chars": zh_chars,
        "summary_pdf_text_chars": summary_chars,
        "asset_png_count": asset_count,
        "extra_entries": extra_entries,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
