#!/usr/bin/env python3
"""Build static site under docs/Japan/20260721_Tokyo/ for GitHub Pages."""
import re
import shutil
import subprocess
import sys
from pathlib import Path

TRIP_SLUG = Path("Japan") / "20260721_Tokyo"
TRIP_ROOT = Path(__file__).resolve().parent
REPO_ROOT = TRIP_ROOT.parent.parent
DOCS = REPO_ROOT / "docs" / TRIP_SLUG
ASSETS_SRC = TRIP_ROOT / "assets"
MOBILE_SRC = TRIP_ROOT / "tokyo-2026-guide-mobile.html"

WEB_BANNER_OLD = """<div id="mobile-open-help" class="mobile-open-help">
  <b>📱 iPhone 必讀（折疊打不開 = 開錯 App）</b><br>
  ① 檔案 App <b>長按</b>此檔 → <b>分享 → 在 Safari 中打開</b>（勿直接點檔名）<br>
  ② Safari 開啟後 → 下方 <b>分享 → 加入主畫面</b>（之後從桌面圖示開，最穩）<br>
  <span class="muted" style="font-size:12px">iOS 無法把本機 HTML 預設用 Safari 開，只能手動分享或加主畫面。</span>
</div>"""

WEB_BANNER_NEW = """<div id="mobile-open-help" class="mobile-open-help web-ok">
  <b>✅ 網頁版</b>：已用 Safari / Chrome 開啟，<b>折疊區塊可點擊</b>。<br>
  建議：Safari 下方 <b>分享 → 加入主畫面</b>，之後像 App 一樣開，日本當地也能用。
</div>"""

WEB_BANNER_STYLE = """
.web-ok{background:#e8f5ee!important;border-color:#2d8a62!important;color:#1a4a32!important}
"""

MAP_NAMES = [
    "overview.png",
    *(f"day-{day:02d}.png" for day in range(1, 8)),
]


def use_external_map_images(html: str) -> str:
    """GitHub Pages serves assets/ alongside HTML — use full-res PNG, not embedded JPEG."""
    for name in MAP_NAMES:
        html = re.sub(
            rf'(<a[^>]*href="assets/{re.escape(name)}"[^>]*>\s*<img[^>]*src=")data:image/[^"]+(")',
            rf"\1assets/{name}\2",
            html,
            count=1,
        )
        html = re.sub(
            rf'(<img id="map-overview"[^>]*src=")data:image/[^"]+(")',
            rf"\1assets/{name}\2",
            html,
            count=1,
        ) if name == "overview.png" else html
    html = html.replace(
        ".map-img{width:100%;max-width:480px;",
        ".map-link{display:block;line-height:0}.map-img{width:100%;max-width:960px;height:auto;",
    )
    return html


def run_guide_builds() -> None:
    subprocess.run([sys.executable, str(TRIP_ROOT / "build-guides.py")], check=True)


def write_repo_index() -> None:
    """Root docs/index.html — trip catalog for GitHub Pages."""
    repo_docs = REPO_ROOT / "docs"
    repo_docs.mkdir(parents=True, exist_ok=True)
    trip_href = f"{TRIP_SLUG.as_posix()}/"
    index = REPO_ROOT / "docs" / "index.html"
    index.write_text(
        f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Travel Log</title>
<style>
  body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;max-width:640px;margin:2rem auto;padding:0 1rem;line-height:1.6}}
  h1{{font-size:1.5rem}}
  a{{color:#1a6b7a}}
  .trip{{border:1px solid #ddd;border-radius:10px;padding:1rem 1.25rem;margin:1rem 0}}
</style>
</head>
<body>
<h1>🧳 Travel Log</h1>
<p>個人走過的旅程行程與地圖。</p>
<div class="trip">
  <h2><a href="{trip_href}">Japan · Tokyo 2026</a></h2>
  <p>2026/7/21–7/27 · 7 日東京親子行程</p>
  <p><a href="{trip_href}">開啟行程指南 →</a></p>
</div>
</body>
</html>
""",
        encoding="utf-8",
    )


def build_docs() -> None:
    run_guide_builds()

    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir(parents=True)
    assets_dest = DOCS / "assets"
    assets_dest.mkdir()

    for name in [
        "overview.png",
        "day-01.png",
        "day-02.png",
        "day-03.png",
        "day-04.png",
        "day-05.png",
        "day-06.png",
        "day-07.png",
    ]:
        src = ASSETS_SRC / name
        if src.exists():
            shutil.copy2(src, assets_dest / name)

    mobile = MOBILE_SRC.read_text(encoding="utf-8")
    mobile = mobile.replace(WEB_BANNER_OLD, WEB_BANNER_NEW)
    mobile = mobile.replace("</style>\n<script>", WEB_BANNER_STYLE + "</style>\n<script>", 1)
    mobile = use_external_map_images(mobile)
    (DOCS / "index.html").write_text(mobile, encoding="utf-8")

    shutil.copy2(TRIP_ROOT / "journey-maps.html", DOCS / "maps.html")
    shutil.copy2(TRIP_ROOT / "tokyo-2026-guide-light.html", DOCS / "guide.html")

    maps = (DOCS / "maps.html").read_text(encoding="utf-8")
    maps = maps.replace('href="tokyo-2026-guide-light.html"', 'href="guide.html"')
    (DOCS / "maps.html").write_text(maps, encoding="utf-8")

    guide = (DOCS / "guide.html").read_text(encoding="utf-8")
    guide = guide.replace('href="journey-maps.html"', 'href="maps.html"')
    (DOCS / "guide.html").write_text(guide, encoding="utf-8")

    write_repo_index()

    pages_base = "https://你的帳號.github.io/travel-log"
    trip_url = f"{pages_base}/{TRIP_SLUG.as_posix()}/"
    print(f"Site ready: {DOCS}/")
    print(f"  index.html  ← 分享：{trip_url}")
    print("  maps.html   ← 插畫地圖分頁")
    print("  guide.html  ← 完整指南（清新版）")
    print(f"Repo index: {REPO_ROOT / 'docs' / 'index.html'}")


if __name__ == "__main__":
    build_docs()
