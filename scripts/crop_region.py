#!/usr/bin/env python3
import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image
from pypdf import PdfReader


COMMON_PDFTOPPM = [
    "/Users/zhouwenjie/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/pdftoppm",
    "/opt/homebrew/bin/pdftoppm",
    "/usr/local/bin/pdftoppm",
]


def find_pdftoppm() -> str:
    found = shutil.which("pdftoppm")
    if found:
        return found
    for candidate in COMMON_PDFTOPPM:
        if Path(candidate).exists():
            return candidate
    raise SystemExit("pdftoppm not found. Install poppler or use the bundled Codex runtime.")


def parse_bbox(value: str) -> tuple[float, float, float, float]:
    parts = [float(part.strip()) for part in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("--bbox must have four comma-separated numbers")
    x0, y0, x1, y1 = parts
    if x1 <= x0 or y1 <= y0:
        raise argparse.ArgumentTypeError("--bbox must be x0,y0,x1,y1 with positive width and height")
    return x0, y0, x1, y1


def render_page(pdf: Path, page_number: int, dpi: int, tmpdir: Path) -> Path:
    prefix = tmpdir / "page"
    subprocess.run(
        [
            find_pdftoppm(),
            "-png",
            "-r",
            str(dpi),
            "-f",
            str(page_number),
            "-l",
            str(page_number),
            str(pdf),
            str(prefix),
        ],
        check=True,
    )
    matches = sorted(tmpdir.glob("page-*.png"))
    if not matches:
        raise SystemExit("pdftoppm did not produce a page image")
    return matches[0]


def bbox_to_pixels(bbox, units, page_width, page_height, image_width, image_height, dpi):
    x0, y0, x1, y1 = bbox
    if units == "pdf":
        scale = dpi / 72.0
        left = x0 * scale
        right = x1 * scale
        top = (page_height - y1) * scale
        bottom = (page_height - y0) * scale
    elif units == "relative-top-left":
        left = x0 * image_width
        top = y0 * image_height
        right = x1 * image_width
        bottom = y1 * image_height
    elif units == "pixels":
        left, top, right, bottom = x0, y0, x1, y1
    else:
        raise SystemExit(f"Unsupported units: {units}")
    return int(round(left)), int(round(top)), int(round(right)), int(round(bottom))


def main():
    parser = argparse.ArgumentParser(description="Crop a figure, table, or display equation region from a PDF page.")
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--page", required=True, type=int)
    parser.add_argument("--bbox", required=True, type=parse_bbox, help="x0,y0,x1,y1")
    parser.add_argument("--out", required=True)
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument("--units", choices=["pdf", "relative-top-left", "pixels"], default="pdf")
    parser.add_argument("--pad-px", type=int, default=8)
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(str(pdf_path))
    page = reader.pages[args.page - 1]
    page_width = float(page.mediabox.width)
    page_height = float(page.mediabox.height)

    with tempfile.TemporaryDirectory() as tmp:
        image_path = render_page(pdf_path, args.page, args.dpi, Path(tmp))
        image = Image.open(image_path).convert("RGB")
        left, top, right, bottom = bbox_to_pixels(
            args.bbox,
            args.units,
            page_width,
            page_height,
            image.width,
            image.height,
            args.dpi,
        )
        left = max(0, left - args.pad_px)
        top = max(0, top - args.pad_px)
        right = min(image.width, right + args.pad_px)
        bottom = min(image.height, bottom + args.pad_px)
        if right <= left or bottom <= top:
            raise SystemExit("Computed crop is empty")
        crop = image.crop((left, top, right, bottom))
        crop.save(out_path)

    print(f"saved {out_path}")


if __name__ == "__main__":
    main()
