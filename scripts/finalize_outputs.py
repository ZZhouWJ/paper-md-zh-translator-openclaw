#!/usr/bin/env python3
import argparse
import json
import shutil
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
    parser = argparse.ArgumentParser(
        description="Re-check searchable PDF text, then delete all intermediate files and leave only three PDFs."
    )
    parser.add_argument("--folder", required=True)
    parser.add_argument("--basename", required=True)
    parser.add_argument("--min-zh-text-chars", type=int, default=300)
    parser.add_argument("--min-summary-text-chars", type=int, default=200)
    parser.add_argument("--confirm-delete-intermediates", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    folder = Path(args.folder)
    basename = args.basename
    final_pdfs = [
        folder / f"{basename}.pdf",
        folder / f"{basename}_zh.pdf",
        folder / f"{basename}_summary.pdf",
    ]
    errors = []
    for path in final_pdfs:
        if not path.exists():
            errors.append(f"missing final PDF: {path}")

    zh_chars = pdf_text_chars(final_pdfs[1]) if final_pdfs[1].exists() else 0
    summary_chars = pdf_text_chars(final_pdfs[2]) if final_pdfs[2].exists() else 0
    if final_pdfs[1].exists() and zh_chars < args.min_zh_text_chars:
        errors.append(f"translated PDF has too little extractable text: {zh_chars}")
    if final_pdfs[2].exists() and summary_chars < args.min_summary_text_chars:
        errors.append(f"summary PDF has too little extractable text: {summary_chars}")

    allowed = {path.resolve() for path in final_pdfs}
    delete_candidates = []
    if folder.exists():
        for child in folder.iterdir():
            if child.resolve() not in allowed:
                delete_candidates.append(child)

    if delete_candidates and not args.confirm_delete_intermediates and not args.dry_run:
        errors.append("refusing to delete intermediates without --confirm-delete-intermediates")

    deleted = []
    if not errors and not args.dry_run:
        for path in delete_candidates:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            deleted.append(str(path))

    result = {
        "ok": not errors,
        "errors": errors,
        "translated_pdf_text_chars": zh_chars,
        "summary_pdf_text_chars": summary_chars,
        "final_pdfs": [str(path) for path in final_pdfs],
        "delete_candidates": [str(path) for path in delete_candidates],
        "deleted": deleted,
        "dry_run": args.dry_run,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
