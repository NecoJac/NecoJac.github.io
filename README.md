# Shengze Jiang's website

Personal homepage at **https://necojac.github.io/**, with the first project page at **https://necojac.github.io/GRAD/**.

This is a self-contained static site. Open `index.html` directly for the personal homepage or `GRAD/index.html` for the project page. The archived course-blog implementation remains in Git history at commit `8c3a1b3`.

## Pages and assets

- `index.html`: biography, selected research, education, honors, and contact.
- `GRAD/index.html`: project explanation, matched-observation results, framework, and videos.
- `assets/css/site.css`, `assets/js/site.js`: shared styling and interactions.
- `assets/media/`: the 30-second real/raster multiview recording and a 22-second closed-loop showcase. The showcase joins the four original clips using FFmpeg stream copy; neither video is re-encoded.
- `assets/docs/grad-overview.pdf`: the author-provided framework figure.
- `scripts/`: reproducible preparation and validation utilities.

The homepage includes email, CV, GitHub, and LinkedIn links. `CV.pdf` and `profile.jpg` initially contain clearly marked placeholders, not the author's personal documents or photograph.

## Updating CV and photo

Replace these files through GitHub's **Add file > Upload files** at the repository root:

- `CV.pdf`: the public CV.
- `profile.jpg`: the portrait. To use `profile.png` or `profile.webp`, remove the JPG placeholder first; JPG takes priority if multiple versions are present.

Use these exact filenames, including capitalization. The homepage detects uploaded files and shows them only when available. No HTML editing is required. Uploaded files will be publicly accessible; upload only versions intended for public release.

## Publishing

GitHub Pages publishes the root of `master` through its existing branch-based deployment. Pushes and uploads update the site automatically. The `Check website` workflow validates personal-file handling, links, and video hashes. The optional local build produces `_site/` with only public pages and assets; it can also be used on other static hosts.

The [GRAD repository](https://github.com/NecoJac/GRAD) is maintained separately.

## Reproducible preparation

`scripts/prepare_documents.py` uses PyMuPDF to render saved figures from `--source-root`. `scripts/prepare_media.py` uses OpenCV and Pillow to copy original videos and extract posters. Both write source-hash manifests and require the original files as command-line inputs.

Run `python scripts/build_site.py` to build the public site, then `python scripts/check_assets.py --root _site` to check links and video hashes. `python -m unittest discover -s scripts -p 'test_*.py'` tests optional personal-file handling. `scripts/browser_check.py --site-root _site --browser /path/to/chromium` uses Playwright to check desktop and mobile layouts, video playback, image dialogs, and profile links. Screenshots and reports go to ignored `_qa/`.

## Design references

The personal homepage takes inspiration from [Jon Barron's academic homepage](https://jonbarron.info/). The concise project-page structure follows the [RAP project page](https://alan-lanfeng.github.io/RAP/#abstract), with recordings, an overview, results, and a method description. The HTML/CSS implementation is original; no template source or research imagery was copied from these projects. The three project-page images show the framework, road-prediction comparison, and controller-adaptation cases.

Icons are provided by [Lucide](https://lucide.dev/), bundled locally with its license. Scientific figures and videos come from GRAD assets and saved outputs. No AI-generated images were added for this site. There are no analytics, tracking scripts, remote fonts, or remote video players.
