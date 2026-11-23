"""Validate local resource links and immutable source-video hashes."""

import hashlib
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit


class Document(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids = set()
        self.links = []
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            assert attrs["id"] not in self.ids, f"Duplicate ID: {attrs['id']}"
            self.ids.add(attrs["id"])
        for key in ("src", "href", "poster", "data-zoom"):
            if attrs.get(key):
                self.links.append(attrs[key])


def main():
    source = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=source)
    root = parser.parse_args().root.resolve()
    html = [root / path for path in ("index.html", "GRAD/index.html", "404.html")]
    documents = {path.resolve(): Document(path) for path in html}
    count = 0
    for path, document in documents.items():
        for link in document.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            target = (root / unquote(url.path).lstrip("/") if url.path.startswith("/")
                      else path.parent / unquote(url.path)) if url.path else path
            if target.is_dir():
                target /= "index.html"
            target = target.resolve()
            assert target.is_file(), f"Missing resource: {path.name} -> {link}"
            if url.fragment and target in documents:
                assert unquote(url.fragment) in documents[target].ids, link
            count += 1
    videos = json.loads((source / "scripts/media-manifest.json").read_text())
    for video in videos:
        path = root / "assets/media" / video["source"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == video["sha256"]
    for path in html:
        text = path.read_text().lower()
        assert "under review" not in text and "submitted to" not in text
        assert "google-analytics" not in text and "beautifuljekyll" not in text
    print(json.dumps({"valid_local_references": count, "verified_video_hashes": len(videos),
                      "public_page_checks": "passed"}, indent=2))


if __name__ == "__main__":
    main()
