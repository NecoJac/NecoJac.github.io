"""Render saved figures for the website without changing the sources."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil

import pymupdf as fitz


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--grad-repo", required=True, type=Path)
    args = parser.parse_args()
    site = Path(__file__).resolve().parents[1]
    images = site / "assets/images"
    docs = site / "assets/docs"
    for folder in (images, docs, args.grad_repo / "assets"):
        folder.mkdir(parents=True, exist_ok=True)
    provenance = []
    figures = [("GRAD_overview.pdf", "grad-overview.png"),
               ("stage1_road_features.pdf", "road-features.png"),
               ("adapter_safety_compact.pdf", "adapter-cases.png")]
    for source_name, output_name in figures:
        source = args.source_root / "figures" / source_name
        with fitz.open(source) as document:
            page = document[0]
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2600 / page.rect.width,
                                                      2600 / page.rect.width),
                                     alpha=False)
            pixmap.save(images / output_name)
            provenance.append({"source": source_name, "sha256": digest(source),
                               "output": output_name,
                               "size": [pixmap.width, pixmap.height]})
    shutil.copy2(args.source_root / "figures/GRAD_overview.pdf", docs / "grad-overview.pdf")
    shutil.copy2(images / "grad-overview.png", args.grad_repo / "assets/overview.png")

    (site / "scripts/document-manifest.json").write_text(
        json.dumps(provenance, indent=2) + "\n")
    print(json.dumps(provenance, indent=2))


if __name__ == "__main__":
    main()
