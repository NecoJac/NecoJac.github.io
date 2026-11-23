"""Check public output without using any personal documents."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from build_site import build


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.source = Path(self.directory.name) / "source"
        self.output = Path(self.directory.name) / "output"
        self.source.mkdir()
        for name in ("404.html", "robots.txt", ".nojekyll"):
            (self.source / name).write_text("")
        (self.source / "index.html").write_text(
            "<!-- PROFILE_PHOTO --><!-- PROFILE_CV_LINK -->")
        for name in ("GRAD", "assets", "scripts"):
            (self.source / name).mkdir()
        (self.source / "scripts/private-input.txt").write_text("test fixture")

    def test_missing_files_have_no_broken_links(self):
        build(self.source, self.output)
        self.assertEqual((self.output / "index.html").read_text(), "")
        self.assertFalse((self.output / "CV.pdf").exists())
        self.assertFalse((self.output / "scripts").exists())

    def test_uploaded_files_and_later_removal(self):
        for name in ("CV.pdf", "profile.png", "profile.jpg"):
            (self.source / name).write_bytes(b"test fixture")
        build(self.source, self.output)
        html = (self.output / "index.html").read_text()
        self.assertIn('href="CV.pdf"', html)
        self.assertIn('src="profile.jpg"', html)
        self.assertNotIn("profile.png", html)
        self.assertTrue((self.output / "CV.pdf").exists())
        for name in ("CV.pdf", "profile.png", "profile.jpg"):
            (self.source / name).unlink()
        build(self.source, self.output)
        self.assertEqual((self.output / "index.html").read_text(), "")
        self.assertFalse((self.output / "CV.pdf").exists())
        self.assertFalse((self.output / "profile.jpg").exists())

    def test_output_cannot_overwrite_source(self):
        with self.assertRaises(ValueError):
            build(self.source, self.source)
        with self.assertRaises(ValueError):
            build(self.source, self.source.parent)


if __name__ == "__main__":
    unittest.main()
