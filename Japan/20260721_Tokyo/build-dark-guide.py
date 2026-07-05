#!/usr/bin/env python3
"""Build dark-theme guide from light source (itinerary content stays identical)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "tokyo-2026-guide-light.html"
TEMPLATE = ROOT / "tokyo-2026-guide.html"
OUTPUT = ROOT / "tokyo-2026-guide.html"

DARK_ACCBOX = """<div class="noprint accbox" style="margin-top:14px">
  🗺️ <b>冒險地圖</b>：開啟 <a href="journey-maps.html"><b>旅程地圖（8 張插畫風）</b></a>，可存 PNG 帶著走。<br>
  📱 <b>存成 PDF 帶著走</b>：手機用 Safari/Chrome 開此檔 → 分享/列印 → <b>「儲存為 PDF」</b>。電腦 <code>Cmd/Ctrl+P</code> → 目的地選 PDF。列印時所有折疊區塊會自動展開。
</div>
<a class="map-link" href="assets/overview.png" target="_blank" rel="noopener"><img src="assets/overview.png" alt="旅程總覽地圖（點擊開啟高畫質原圖）" class="map-img" loading="lazy" decoding="async"></a>"""

DARK_FOOTER = """<div class="footer">
產生於 2026/6/28　｜　所有時間/票價/營業時間以官方與 Google Maps 當日資訊為準。祝旅途愉快 🎌<br>
本檔可用瀏覽器「列印 → 儲存為 PDF」帶著走（離線可看）。清新版：<code>tokyo-2026-guide-light.html</code>
</div>

</div>
</body>
</html>
"""

MAP_LIGHT_RE = re.compile(
    r'<a href="(assets/[^"]+)" target="_blank" rel="noopener" style="display:block; line-height:0;">'
    r'<img src="\1" alt="([^"]*)"(?: loading="lazy" decoding="async")? style="[^"]+"></a>'
)

PROMPT_PRE_LIGHT = '<pre class="prompt-pre">'
PROMPT_PRE_DARK = (
    '<pre style="white-space:pre-wrap;font-size:13px;line-height:1.5;color:#dfe6ee">'
)


def extract_head(template: str) -> str:
    end = template.index("</head>") + len("</head>")
    return template[:end]


def extract_body_content(light: str) -> str:
    start = light.index('<nav class="toc">')
    end = light.index('<div class="footer">')
    return light[start:end]


def light_maps_to_dark(html: str) -> str:
    return MAP_LIGHT_RE.sub(
        r'<a class="map-link" href="\1" target="_blank" rel="noopener">'
        r'<img src="\1" alt="\2" class="map-img" loading="lazy" decoding="async"></a>',
        html,
    )


def build_dark_html() -> str:
    light = SOURCE.read_text(encoding="utf-8")
    template = TEMPLATE.read_text(encoding="utf-8")

    header_end = light.index("</header>") + len("</header>")
    header = light[:header_end]

    body = extract_body_content(light)
    body = light_maps_to_dark(body)
    body = body.replace(PROMPT_PRE_LIGHT, PROMPT_PRE_DARK)

    return (
        extract_head(template)
        + "\n<body>\n"
        + header
        + "\n\n<div class=\"wrap\">\n\n"
        + DARK_ACCBOX
        + "\n\n"
        + body
        + DARK_FOOTER
    )


def main() -> None:
    html = build_dark_html()
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUTPUT.name} ({OUTPUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
