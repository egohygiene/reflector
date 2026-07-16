#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Generate first-page WebP preview images for publication PDFs."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def log(message: str) -> None:
    print(f"[generate-pdf-previews] {message}")


def log_error(message: str) -> None:
    print(f"[generate-pdf-previews] ERROR: {message}", file=sys.stderr)


def parse_preview_spec(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError(
            "Preview mappings must use NAME=PDF_PATH format."
        )
    name, pdf_path = value.split("=", 1)
    name = name.strip()
    pdf = Path(pdf_path.strip())
    if not name:
        raise argparse.ArgumentTypeError("Preview name cannot be empty.")
    if not pdf_path.strip():
        raise argparse.ArgumentTypeError("Preview PDF path cannot be empty.")
    return name, pdf


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate first-page WebP preview images from publication PDFs."
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where generated .webp previews will be written.",
    )
    parser.add_argument(
        "--preview",
        action="append",
        type=parse_preview_spec,
        required=True,
        metavar="NAME=PDF_PATH",
        help="Generate OUTPUT_DIR/NAME.webp from the first page of PDF_PATH.",
    )
    parser.add_argument(
        "--scale-to",
        type=int,
        default=1200,
        help="Longest-edge target used when rasterizing the first PDF page.",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=85,
        help="WebP quality to use when cwebp is available.",
    )
    return parser


def require_binary(name: str) -> str:
    resolved = shutil.which(name)
    if resolved is None:
        raise FileNotFoundError(name)
    return resolved


def render_first_page(pdftoppm: str, pdf_path: Path, png_path: Path, scale_to: int) -> None:
    subprocess.run(
        [
            pdftoppm,
            "-png",
            "-singlefile",
            "-f",
            "1",
            "-l",
            "1",
            "-scale-to",
            str(scale_to),
            str(pdf_path),
            str(png_path.with_suffix("")),
        ],
        check=True,
    )


def convert_to_webp(png_path: Path, output_path: Path, quality: int) -> None:
    cwebp = shutil.which("cwebp")
    if cwebp is not None:
        subprocess.run(
            [cwebp, "-quiet", "-q", str(quality), str(png_path), "-o", str(output_path)],
            check=True,
        )
        return

    magick = shutil.which("magick")
    if magick is not None:
        subprocess.run(
            [magick, str(png_path), "-quality", str(quality), str(output_path)],
            check=True,
        )
        return

    raise FileNotFoundError("cwebp or magick")


def generate_preview(
    name: str,
    pdf_path: Path,
    output_dir: Path,
    *,
    scale_to: int,
    quality: int,
    pdftoppm: str,
) -> Path:
    if not pdf_path.is_file():
        raise FileNotFoundError(str(pdf_path))

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{name}.webp"
    with tempfile.TemporaryDirectory(prefix="pdf-preview-") as tmp_dir:
        png_path = Path(tmp_dir) / name
        render_first_page(pdftoppm, pdf_path, png_path, scale_to)
        convert_to_webp(png_path.with_suffix(".png"), output_path, quality)

    log(f"Generated {output_path}")
    return output_path


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_dir = Path(args.output_dir)
    try:
        pdftoppm = require_binary("pdftoppm")
        generated = [
            generate_preview(
                name,
                pdf_path,
                output_dir,
                scale_to=args.scale_to,
                quality=args.quality,
                pdftoppm=pdftoppm,
            )
            for name, pdf_path in args.preview
        ]
    except FileNotFoundError as error:
        missing = Path(str(error)).name or str(error)
        log_error(
            f"Required dependency '{missing}' was not found. "
            "Install poppler-utils and either webp or ImageMagick."
        )
        return 1
    except subprocess.CalledProcessError as error:
        log_error(f"Preview generation failed while running: {' '.join(error.cmd)}")
        return error.returncode or 1

    log(f"Generated {len(generated)} preview(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
