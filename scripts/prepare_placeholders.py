"""Create clearly marked placeholders; never overwrite uploaded personal files."""

import argparse
from pathlib import Path

import pymupdf as fitz


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    folder = parser.parse_args().output
    folder.mkdir(parents=True, exist_ok=True)
    for name in ("CV.pdf", "profile.jpg"):
        if (folder / name).exists():
            raise FileExistsError(f"Refusing to overwrite {name}")

    with fitz.open() as document:
        page = document.new_page(width=595, height=842)
        page.insert_text((64, 92), "Shengze Jiang", fontsize=24, fontname="hebo",
                         color=(.10, .16, .20))
        page.insert_text((64, 125), "Curriculum Vitae", fontsize=15,
                         color=(.20, .28, .32))
        page.draw_line((64, 150), (531, 150), color=(.80, .85, .87), width=.7)
        page.insert_text((64, 194), "CV will be added soon.", fontsize=13)
        page.insert_text((64, 220), "This is a placeholder, not a curriculum vitae.",
                         fontsize=11, color=(.40, .45, .48))
        document.set_metadata({"title": "Shengze Jiang - CV placeholder",
                               "author": "Shengze Jiang"})
        document.save(folder / "CV.pdf")

    with fitz.open() as document:
        page = document.new_page(width=360, height=440)
        page.draw_rect(page.rect, fill=(.93, .96, .97), color=None)
        font = "hebo"
        size = 96
        width = fitz.get_text_length("SJ", fontname=font, fontsize=size)
        page.insert_text(((360 - width) / 2, 238), "SJ", fontname=font,
                         fontsize=size, color=(.16, .38, .46))
        page.insert_textbox((30, 285, 330, 310), "PHOTO COMING SOON",
                            fontsize=10, align=1, color=(.37, .48, .52))
        page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(folder / "profile.jpg")
    print("Created CV.pdf and profile.jpg placeholders")


if __name__ == "__main__":
    main()
