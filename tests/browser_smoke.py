"""Exercise the published tool at a project subpath in Chromium."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
import json
import tempfile
import threading
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    screenshots = ROOT / "browser-checks"
    screenshots.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        shutil.copytree(ROOT / "dist", Path(temporary) / "example-tool")
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=temporary))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={"width": 1280, "height": 1000})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(f"http://127.0.0.1:{server.server_port}/example-tool/")
                page.wait_for_selector("#content:visible")
                page.locator("#dollar-from option[value='1914']").wait_for(state="attached")
                page.select_option("#dollar-from","1914")
                page.select_option("#dollar-to","1914")
                expect(page.locator("#dollar-result")).to_have_text("$100.00")
                page.select_option("#dollar-to","latest")
                assert "monthly CPI" in page.locator("#dollar-explanation").inner_text()
                data=json.loads((ROOT/"web/data/dollars.json").read_text())
                last=data["latest_month"]["Canada"]["date"]
                if last[5:]!="12":
                    assert page.locator("#dollar-to option[value='"+last[:4]+"']").count()==0
                page.locator("#dollar-amount").fill("-1")
                assert page.locator("#dollar-export").is_disabled()
                page.locator("#dollar-amount").fill("4000000")
                with page.expect_download():page.click("#dollar-export")
                page.select_option("#geo","British Columbia")
                page.select_option("#from","2025-10")
                page.select_option("#to","2026-10")
                for i in range(8):
                    page.locator(f"#weight-{i}").fill("1" if i == 0 else "0")
                assert "2.37%" in page.locator("#cards .big").first.inner_text()
                assert "2.51%" in page.locator("#cards .big").last.inner_text()
                with page.expect_download():
                    page.click("#download")
                page.locator("#published").click()
                assert page.locator("#parts tbody tr").count()==8
                page.screenshot(path=str(screenshots / "desktop.png"), full_page=True)
                page.set_viewport_size({"width": 390, "height": 844})
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                page.screenshot(path=str(screenshots / "mobile.png"), full_page=True)
                assert not errors, errors
                # Exercise the direct search landing page in a fresh browser context.
                case_page = browser.new_page(viewport={'width': 390, 'height': 844})
                case_page.route('https://**/*', lambda route: route.abort())
                case_page.goto(f'http://127.0.0.1:{server.server_port}/example-tool/1970-dollars.html')
                case_page.wait_for_function("() => {const q=s=>document.querySelector(s);return q('#dollar-from').value==='1970' && q('#dollar-explanation').textContent.includes('1970');}")
                assert case_page.locator('link[rel="canonical"]').get_attribute('href') == 'https://coolcode.ca/inflation-basket/1970-dollars.html'
                assert case_page.locator('h1').inner_text() in case_page.title()
                assert case_page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
                browser.close()
            print("Browser checks passed: project subpath, published values, filters and mobile layout")
        finally:
            server.shutdown()


if __name__ == "__main__":
    main()
