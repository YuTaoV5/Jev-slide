"""Verify Jev v4 slide navigation, offline controls, media, and slide layouts.

Run from any directory with Python, Playwright, Pillow, and local Chrome installed.
The verifier starts its own loopback-only HTTP server and blocks external requests.
It does not modify the HTML or generated materials.
"""
from __future__ import annotations

import json
import math
import threading
import time
import traceback
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, urlparse

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SLIDES = ROOT / "related_work/08-第30期-Jev-不生成文本的决策模型/slides"
OUT = HERE / "results/slides-v4"
REPORT = HERE / "results/slides-v4-check.json"
EXPECTED = {"deck-practice.html": 7, "deck.html": 60}
ACTIVE_INDEX = """() => [...document.querySelectorAll('section.slide')]
    .indexOf(document.querySelector('section.slide.active'))"""


from serve import MediaHandler


class QuietHandler(MediaHandler):
    def log_message(self, *args):
        pass


def contact(paths: list[Path], target: Path, columns: int = 4):
    width, height, gap, caption = 480, 270, 12, 24
    rows = math.ceil(len(paths) / columns)
    sheet = Image.new(
        "RGB", (columns * (width + gap) + gap, rows * (height + gap + caption) + gap),
        "#d2d2d7",
    )
    draw = ImageDraw.Draw(sheet)
    for i, path in enumerate(paths):
        x = gap + (i % columns) * (width + gap)
        y = gap + (i // columns) * (height + gap + caption)
        with Image.open(path) as source:
            sheet.paste(source.convert("RGB").resize((width, height), Image.Resampling.LANCZOS), (x, y))
        draw.text((x + 4, y + height + 4), path.stem, fill="#1d1d1f")
    sheet.save(target)


def expect_index(page, expected: int):
    page.wait_for_function(f"({ACTIVE_INDEX})() === {expected}", timeout=4000)
    assert page.locator("section.slide.active").count() == 1, "More than one active slide"
    assert page.evaluate("location.hash") == f"#{expected + 1}", "Hash and active slide disagree"


def blur(page):
    page.evaluate("document.activeElement?.blur()")


def jump(page, index: int):
    """Use the visible table-of-contents UI, without a presentation API."""
    item = page.locator(f'#deck-toc button[data-index="{index}"]')
    if not item.is_visible():
        page.locator("#deck-menu").click()
    item.click()
    expect_index(page, index)
    blur(page)


def owner_index(page, selector: str) -> int:
    return page.locator(selector).first.evaluate(
        "e => [...document.querySelectorAll('section.slide')].indexOf(e.closest('section.slide'))"
    )


def range_value(page, selector: str) -> float:
    return float(page.locator(selector).input_value())


def set_range(page, selector: str, value: float):
    page.locator(selector).evaluate(
        "(e,v) => { e.value=String(v); e.dispatchEvent(new Event('input',{bubbles:true})); }", value
    )


def swipe(page, x1: int, y1: int, x2: int, y2: int):
    session = page.context.new_cdp_session(page)
    try:
        session.send("Input.dispatchTouchEvent", {
            "type": "touchStart", "touchPoints": [{"x": x1, "y": y1}],
        })
        for step in range(1, 7):
            session.send("Input.dispatchTouchEvent", {
                "type": "touchMove", "touchPoints": [{
                    "x": round(x1 + (x2 - x1) * step / 6),
                    "y": round(y1 + (y2 - y1) * step / 6),
                }],
            })
        session.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
    finally:
        session.detach()


def layout_issues(page):
    return page.evaluate("""() => {
      const slide=document.querySelector('section.slide.active');
      const stage=slide.getBoundingClientRect();
      const result=[];
      for(const e of slide.querySelectorAll('h1,.sub,.kicker,article,pre,table,canvas,video,img,svg,button,input')){
        if(e.closest('svg')!==null && e.tagName.toLowerCase()!=='svg') continue;
        const r=e.getBoundingClientRect();
        if(!r.width||!r.height) continue;
        const label=e.tagName+': '+(e.id||e.textContent?.trim().slice(0,60)||e.getAttribute('src')||'');
        if(r.left<stage.left-2||r.top<stage.top-2||r.right>stage.right+2||r.bottom>stage.bottom+2)
          result.push({kind:'outside-slide',element:label,rect:{x:r.x,y:r.y,w:r.width,h:r.height}});
        const style=getComputedStyle(e);
        if(['H1','P','PRE','ARTICLE','TABLE'].includes(e.tagName) &&
           !['auto','scroll'].includes(style.overflowY) &&
           !['auto','scroll'].includes(style.overflowX) &&
           (e.scrollWidth>e.clientWidth+3||e.scrollHeight>e.clientHeight+3))
          result.push({kind:'content-overflow',element:label});
      }
      return result;
    }""")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "viewport": {"width": 1920, "height": 1080, "device_scale_factor": 1},
        "external_requests_blocked": [], "page_errors": [], "http_errors": [],
        "request_failures": [], "checks": [], "renders": {}, "layout_issues": [],
        "test_method": "UI navigation, native keyboard/wheel, CDP touch, DOM/media assertions; external requests blocked",
    }
    missing = [name for name in EXPECTED if not (SLIDES / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Generate the decks before running verification: {missing}")
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_port}/"
    started = time.monotonic()

    def save_report():
        report["elapsed_seconds"] = round(time.monotonic() - started, 2)
        report["passed"] = (
            all(c["passed"] for c in report["checks"])
            and not report["external_requests_blocked"] and not report["page_errors"]
            and not report["http_errors"] and not report["request_failures"]
            and not report["layout_issues"]
        )
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    def check(label, callback, page):
        start = time.monotonic()
        record = {"name": label}
        try:
            callback()
            record["passed"] = True
        except Exception as exc:
            record.update(passed=False, error=f"{type(exc).__name__}: {exc}")
            try:
                failure = OUT / (label.replace("/", "-").replace(":", "-") + "-failure.png")
                page.screenshot(path=str(failure))
                record["screenshot"] = str(failure)
            except Exception:
                pass
        record["seconds"] = round(time.monotonic() - start, 2)
        report["checks"].append(record)
        print(("PASS " if record["passed"] else "FAIL ") + label, flush=True)
        save_report()

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                channel="chrome", headless=True,
                args=["--no-proxy-server", "--autoplay-policy=no-user-gesture-required"],
            )
            context = browser.new_context(viewport={"width": 1920, "height": 1080},
                                          device_scale_factor=1, has_touch=True)

            def guard(route):
                parsed = urlparse(route.request.url)
                if parsed.scheme in {"http", "https"} and parsed.hostname not in {"127.0.0.1", "localhost"}:
                    report["external_requests_blocked"].append(route.request.url)
                    route.abort()
                else:
                    route.continue_()

            context.route("**/*", guard)
            page = context.new_page()
            page.set_default_timeout(6000)
            page.on("pageerror", lambda error: report["page_errors"].append({"page": page.url, "error": str(error)}))
            page.on("response", lambda response: report["http_errors"].append({"url": response.url, "status": response.status})
                    if response.status >= 400 and not response.url.endswith("favicon.ico") else None)
            page.on("requestfailed", lambda request: report["request_failures"].append({"url": request.url, "error": request.failure})
                    if request.failure != "net::ERR_ABORTED" else None)

            for name, count in EXPECTED.items():
                path = SLIDES / name
                http_url = base + quote(path.relative_to(ROOT).as_posix())
                practice_offset = 0 if name == "deck-practice.html" else 38
                for mode, url in (("http", http_url), ("file", path.as_uri())):
                    prefix = f"{path.stem}/{mode}"

                    def load():
                        page.goto(url + "#1", wait_until="load")
                        expect_index(page, 0)
                        assert page.locator("section.slide").count() == count
                        for selector in ["#deck-prev", "#deck-next", "#deck-menu", "#deck-count"]:
                            assert page.locator(selector).is_visible(), selector + " is not visible"
                        assert str(count) in page.locator("#deck-count").inner_text()

                    check(prefix + "/load-and-page-count", load, page)

                    def navigation():
                        jump(page, 0)
                        if page.locator("#deck-prev").is_enabled():
                            page.locator("#deck-prev").click()
                        expect_index(page, 0)
                        page.locator("#deck-next").click()
                        expect_index(page, 1)
                        blur(page)
                        for key, index in [("ArrowLeft", 0), ("Space", 1), ("ArrowDown", 2),
                                           ("ArrowUp", 1), ("PageDown", 2), ("PageUp", 1),
                                           ("End", count - 1), ("ArrowRight", count - 1), ("Home", 0)]:
                            page.keyboard.press(key)
                            expect_index(page, index)
                        page.keyboard.type(str(min(10, count)))
                        expect_index(page, min(9, count - 1))
                        jump(page, 5)
                        expect_index(page, 5)
                        page.locator("#deck-menu").click()
                        panel = page.locator("#deck-toc")
                        bounds = panel.bounding_box()
                        page.mouse.move(bounds["x"] + bounds["width"] / 2,
                                        bounds["y"] + min(bounds["height"] / 2, 200))
                        page.mouse.wheel(0, 480)
                        page.wait_for_timeout(150)
                        expect_index(page, 5)
                        page.keyboard.press("Escape")
                        assert not panel.is_visible(), "Escape did not close the table of contents"

                    check(prefix + "/buttons-keyboard-digits-toc-boundaries", navigation, page)

                    def hashes():
                        page.evaluate("location.hash='#4'")
                        expect_index(page, 3)
                        page.reload(wait_until="load")
                        expect_index(page, 3)
                        page.evaluate("location.hash='#999'")
                        expect_index(page, count - 1)
                        page.evaluate("location.hash='#1'")
                        expect_index(page, 0)

                    check(prefix + "/hashchange-refresh-clamping", hashes, page)

                    def wheel():
                        jump(page, 0)
                        page.mouse.move(1850, 800)
                        page.mouse.wheel(0, 1)
                        page.wait_for_timeout(100)
                        expect_index(page, 0)
                        page.mouse.wheel(0, 480)
                        expect_index(page, 1)
                        page.mouse.wheel(0, 480)
                        page.wait_for_timeout(180)
                        expect_index(page, 1)
                        page.wait_for_timeout(1100)
                        page.mouse.wheel(0, -480)
                        expect_index(page, 0)

                    check(prefix + "/wheel-threshold-inertia-and-reverse", wheel, page)

                    def touches():
                        jump(page, 0)
                        page.wait_for_timeout(1100)
                        swipe(page, 1550, 320, 700, 320)
                        expect_index(page, 1)
                        page.wait_for_timeout(300)
                        expect_index(page, 1)
                        page.wait_for_timeout(850)
                        swipe(page, 650, 320, 1500, 320)
                        expect_index(page, 0)

                    check(prefix + "/touch-swipe-without-double-advance", touches, page)

                    def maze():
                        index = owner_index(page, "#maze-play")
                        jump(page, index)
                        page.locator("#maze-reset").click()
                        start = range_value(page, "#maze-step")
                        page.locator("#maze-play").click()
                        page.wait_for_function("Number(document.querySelector('#maze-step').value)>" + str(start), timeout=4000)
                        page.locator("#maze-play").click()
                        expect_index(page, index)
                        slider = page.locator("#maze-step")
                        slider.focus()
                        before = range_value(page, "#maze-step")
                        page.keyboard.press("ArrowRight")
                        assert range_value(page, "#maze-step") > before, "Replay range cannot be adjusted by keyboard"
                        expect_index(page, index)
                        page.locator("#maze-reset").click()
                        assert range_value(page, "#maze-step") == float(slider.get_attribute("min") or 0)
                        canvases = page.locator("section.slide.active canvas")
                        assert canvases.count() == 2, "Replay should show two model canvases"
                        for canvas in canvases.all():
                            assert canvas.evaluate("e=>e.width>0&&e.height>0&&e.getContext('2d').getImageData(0,0,e.width,e.height).data.some(v=>v!==0)"), "Blank replay canvas"
                        expect_index(page, index)
                        blur(page)

                    check(prefix + "/maze-play-reset-scrub-and-canvases", maze, page)

                    def video(index):
                        jump(page, index)
                        element = page.locator("section.slide.active video").first
                        assert element.count() == 1, "Practice slide 3 needs the mechanism video"
                        assert element.evaluate("v=>v.muted&&v.loop&&v.controls&&v.autoplay"), "Video flags missing"
                        page.wait_for_function("document.querySelector('section.slide.active video')?.readyState>=2", timeout=20000)
                        page.wait_for_function("document.querySelector('section.slide.active video').currentTime>.1", timeout=6000)
                        assert not element.evaluate("v=>v.paused"), "Video is not playing"
                        element.evaluate("v=>v.currentTime=Math.min(5,v.duration/2)")
                        page.wait_for_function("document.querySelector('section.slide.active video').currentTime>=5", timeout=6000)
                        page.locator("#deck-next").click()
                        expect_index(page, index + 1)
                        assert page.locator("section.slide").nth(index).locator("video").first.evaluate("v=>v.paused"), "Video continues playing off-slide"
                        page.locator("#deck-prev").click()
                        expect_index(page, index)
                        assert element.evaluate("v=>v.currentTime<2"), "Video was not restarted on re-entry"
                        bounds = element.bounding_box()
                        page.mouse.click(bounds["x"] + 25, bounds["y"] + bounds["height"] - 20)
                        expect_index(page, index)
                        blur(page)

                    if name == "deck.html":
                        for vi in [24,25,26]:
                            check(prefix + f"/video-{vi+1}-load-play-pause-restart-and-controls", lambda vi=vi: video(vi), page)

                # Render clean default slide states through HTTP; every screenshot is 1920×1080.
                def render():
                    page.goto(http_url + "#1", wait_until="load")
                    paths = []
                    titles = []
                    for index in range(count):
                        if index:
                            page.locator("#deck-next").click()
                        expect_index(page, index)
                        page.wait_for_function("[...document.querySelectorAll('section.slide.active img')].every(i=>i.complete&&i.naturalWidth>0)", timeout=15000)
                        page.wait_for_timeout(100)
                        # Render a representative deterministic frame without changing document source.
                        for media in page.locator("section.slide.active video").all():
                            page.wait_for_function("document.querySelector('section.slide.active video').currentTime > 0.3", timeout=10000)
                            media.evaluate("""v => new Promise((resolve,reject)=>{
                              const timer=setTimeout(()=>reject(new Error('Video did not load for screenshot')),15000);
                              const seek=()=>{v.pause();const at=Math.min(19.5,v.duration-.5);
                                if(Math.abs(v.currentTime-at)<.05){clearTimeout(timer);resolve();return;}
                                v.addEventListener('seeked',()=>{clearTimeout(timer);resolve();},{once:true});
                                v.currentTime=at;};
                              if(v.readyState>=2)seek();else v.addEventListener('loadeddata',seek,{once:true});
                            })""")
                            page.wait_for_function("[...document.querySelectorAll('section.slide.active video')].every(v=>!v.seeking && Math.abs(v.currentTime-Math.min(19.5,v.duration-.5))<.1)")
                            page.wait_for_timeout(200)
                        image_path = OUT / f"{path.stem}-{index + 1:02d}.png"
                        page.screenshot(path=str(image_path))
                        paths.append(image_path)
                        titles.append(page.locator("section.slide.active").get_attribute("data-title"))
                        if True:
                            issues = layout_issues(page)
                            if issues:
                                report["layout_issues"].append({"deck": name, "slide": index + 1, "issues": issues})
                        if (index + 1) % 10 == 0:
                            print(f"RENDER {name}: {index + 1}/{count}", flush=True)
                    target = SLIDES / ("预览-实战新版.png" if name == "deck-practice.html" else "预览-全部页面.png")
                    contact(paths, target, columns=4)
                    report["renders"][name] = {"pages": count, "contact_sheet": str(target), "screenshots": [str(x) for x in paths], "titles": titles}

                check(path.stem + "/render-all-pages", render, page)
            context.close()
            browser.close()
    except Exception as exc:
        report["fatal_error"] = f"{type(exc).__name__}: {exc}"
        report["traceback"] = traceback.format_exc()
        report["checks"].append({"name": "verifier-fatal", "passed": False, "error": report["fatal_error"]})
    finally:
        server.shutdown()
        server.server_close()
        save_report()
    print(json.dumps({"passed": report["passed"], "checks": len(report["checks"]),
                      "failed": [c["name"] for c in report["checks"] if not c["passed"]],
                      "layout_issues": len(report["layout_issues"]), "report": str(REPORT)}, ensure_ascii=False), flush=True)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
