"""Local-only browser checks. No server, publication, or external navigation."""

import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", required=True)
    parser.add_argument("--site-root", type=Path)
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    site = (args.site_root or source).resolve()
    output = source / "_qa"
    output.mkdir(exist_ok=True)
    report = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=args.browser,
                                              args=["--no-sandbox"])
        for width, height, label in ((1440, 1000, "desktop"), (390, 844, "mobile"),
                                     (320, 780, "small-mobile")):
            page = browser.new_page(viewport={"width": width, "height": height},
                                    reduced_motion="reduce")
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            for filename, name in (("index.html", "home"), ("GRAD/index.html", "grad")):
                page.goto((site / filename).as_uri(), wait_until="load")
                if name == "grad":
                    page.wait_for_function("[...document.querySelectorAll('video')].every(v => v.readyState >= 2)")
                page.locator("footer").scroll_into_view_if_needed()
                page.wait_for_timeout(250)
                page.evaluate("window.scrollTo(0, 0)")
                page.screenshot(path=str(output / f"{name}-{label}.png"), full_page=True)
                page.screenshot(path=str(output / f"{name}-{label}-viewport.png"))
                size = page.evaluate("({width:document.documentElement.clientWidth, scroll:document.documentElement.scrollWidth})")
                assert size["scroll"] <= size["width"], (name, label, size)
                missing = page.locator("main img").evaluate_all("els => els.filter(e => !e.complete || !e.naturalWidth).map(e => e.src)")
                assert not missing, missing
                assert page.locator("svg.lucide").count() > 0, "Icons did not load"
                report.append({"page": name, "viewport": label, "overflow": False,
                               "images_loaded": True})
                if name == "home":
                    cv_link = page.get_by_role("link", name="CV", exact=True)
                    if (site / "CV.pdf").is_file():
                        assert cv_link.get_attribute("href") == "CV.pdf"
                    else:
                        assert cv_link.count() == 0
                    assert page.get_by_role("link", name="LinkedIn", exact=True).get_attribute("href") == "https://www.linkedin.com/in/shengze-jiang/"
                else:
                    assert page.locator("video").count() == 2
                    for selector, duration in ((".opening-media video", 30), (".showcase-video", 22)):
                        video = page.locator(selector)
                        assert abs(video.evaluate("v => v.duration") - duration) < .1
                        video.evaluate("v => v.play()")
                        page.wait_for_timeout(600)
                        assert video.evaluate("v => v.currentTime") > .2
                        assert video.evaluate("v => v.playbackRate") == 1
                        video.evaluate("v => v.pause()")
                    page.locator(".figure-zoom").first.click()
                    assert page.locator("dialog").evaluate("d => d.open")
                    page.keyboard.press("Escape")
                    assert not page.locator("dialog").evaluate("d => d.open")
                    page.locator("#demos").scroll_into_view_if_needed()
                    page.screenshot(path=str(output / f"demos-{label}.png"))
            assert not errors, errors
            page.close()
        browser.close()
    (output / "browser-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"layouts": report, "video_playback": "passed",
                      "figure_dialog": "passed",
                      "cv_and_linkedin": "passed"}, indent=2))


if __name__ == "__main__":
    main()
