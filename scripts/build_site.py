"""Build GitHub Pages, enabling personal-file links only after upload."""

import argparse
from html import escape
from pathlib import Path
import shutil


def build(source, destination):
    source, destination = source.resolve(), destination.resolve()
    if destination == source or source.is_relative_to(destination):
        raise ValueError("Build output must not contain the source directory")
    destination.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "404.html", "robots.txt", ".nojekyll"):
        shutil.copy2(source / name, destination / name)
    for name in ("GRAD", "assets"):
        shutil.copytree(source / name, destination / name, dirs_exist_ok=True)

    homepage = (source / "index.html").read_text()
    cv = source / "CV.pdf"
    portrait = next((source / name for name in ("profile.jpg", "profile.png", "profile.webp")
                     if (source / name).is_file()), None)
    cv_link = ""
    photo = ""
    if cv.is_file():
        shutil.copy2(cv, destination / cv.name)
        cv_link = '<a href="CV.pdf"><i data-lucide="file-text" aria-hidden="true"></i>CV</a>'
    else:
        (destination / "CV.pdf").unlink(missing_ok=True)
    for name in ("profile.jpg", "profile.png", "profile.webp"):
        if portrait is None or name != portrait.name:
            (destination / name).unlink(missing_ok=True)
    if portrait:
        shutil.copy2(portrait, destination / portrait.name)
        photo = ('<img class="profile-photo" src="' + escape(portrait.name, quote=True)
                 + '" width="180" height="220" alt="Shengze Jiang">')
    homepage = homepage.replace("<!-- PROFILE_CV_LINK -->", cv_link)
    homepage = homepage.replace("<!-- PROFILE_PHOTO -->", photo)
    (destination / "index.html").write_text(homepage)
    print(f"Built {destination.name}: CV={'yes' if cv.is_file() else 'not uploaded'}, "
          f"portrait={'yes' if portrait else 'not uploaded'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    build(args.source, args.output or args.source / "_site")
