#!/usr/bin/env python3
"""Add Google Maps links to places in tokyo-2026-guide-light.html."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "tokyo-2026-guide-light.html"

GMAP_CSS = """
  a.gmap{
    display:inline-block;font-size:12px;font-weight:600;
    color:var(--acc2);text-decoration:none;
    border:1px solid rgba(58,143,159,.35);border-radius:6px;
    padding:0 6px;margin-left:4px;white-space:nowrap;
    vertical-align:baseline;line-height:1.5;
  }
  a.gmap:hover{border-color:var(--acc2);background:#eef7f9}
"""

# (visible text in HTML, Google Maps search query) — longest / most specific first
PLACES: list[tuple[str, str]] = [
    # 住宿・交通
    ("Hotel Crown Hills Ueno Premier", "ホテルクラウンヒルズ上野プレミア"),
    ("成田機場 T1/T2", "成田国際空港"),
    ("成田機場站", "成田空港駅"),
    ("京成上野站", "京成上野駅"),
    ("JR 上野站", "JR上野駅"),
    ("東京車站地下街", "東京駅一番街"),
    ("東京一番街", "東京駅一番街"),
    ("東京拉麵街", "東京ラーメンストリート"),
    # Stations / disambiguation (longest first)
    ("東武晴空塔站", "押上駅"),
    ("東武晴空塔線", "押上駅"),
    ("新杉田站", "新杉田駅"),
    ("葛西水族園", "葛西臨海水族園"),
    ("Aqua Park", "マクセル アクアパーク品川"),
    ("澀谷SKY", "SHIBUYA SKY"),
    ("Toriton", "回転寿司トリトン ソラマチ"),
    ("新宿光雕秀", "東京都庁 都民広場"),
    ("言問橋", "言問橋 隅田川花火"),
    ("駒形橋", "駒形橋 隅田川花火"),
    ("吾妻橋", "吾妻橋 隅田川花火"),
    ("東白鬚公園", "東白鬚公園"),
    ("汐入公園", "汐入公園 隅田川花火"),
    ("赤城神社", "赤城神社 神楽坂"),
    ("神楽坂上", "神楽坂上"),
    ("坂上交差点", "神楽坂上交差点"),
    ("三菱UFJ", "三菱UFJ銀行 神楽坂下"),
    ("飯田橋ラムラ", "飯田橋ラムラ"),
    ("赤城神社参道", "赤城神社参道"),
    ("赤城生涯学習館", "赤城生涯学習館"),
    ("神楽坂かぐら連", "神楽坂 神楽坂かぐら連"),
    ("神楽坂下", "神楽坂下 飯田橋"),
    ("神楽坂下交差點", "神楽坂下交差点 飯田橋"),
    ("毘沙門天 善國寺", "毘沙門天 善國寺"),
    ("善國寺", "毘沙門天 善國寺"),
    ("Starbucks 神楽坂下", "Starbucks 神楽坂下"),
    ("神楽坂駅", "神楽坂駅"),
    ("飯田橋駅西口", "飯田橋駅西口"),
    ("神楽坂通り", "神楽坂通り"),
    # Day1
    ("PARCO_ya", "PARCO_ya 上野"),
    ("上野恩賜公園", "上野恩賜公園"),
    ("不忍池", "不忍池"),
    ("阿美橫町", "アメ横"),
    ("うえの夏まつり", "上野の夏祭り 不忍池"),
    ("HARBS 上野店", "HARBS PARCO_ya 上野"),
    ("みはし 上野本店", "みはし 上野本店"),
    ("廚 otto e sette", "廚 otto e sette 上野"),
    ("鳥貴族 上野店", "鳥貴族 上野店"),
    ("とんかつ 山家", "とんかつ山家 御徒町"),
    ("天丼てんや 上野店", "天丼てんや 上野店"),
    # Day2 八景島
    ("八景島海洋之夢", "横浜・八景島シーパラダイス"),
    ("八景島站", "八景島駅"),
    ("新杉田站", "新杉田駅"),
    ("Seafood & Grill YAKIYA", "Seafood & Grill YAKIYA 八景島"),
    ("Bay Market", "横浜・八景島シーパラダイス ベイマーケット"),
    # Day2 秋葉原
    ("K-BOOKS", "K-BOOKS 秋葉原本館"),
    ("ラジオ会館", "秋葉原ラジオ会館"),
    ("ヨドバシカメラ マルチメディア Akiba", "ヨドバシカメラ マルチメディアAkiba"),
    ("ガシャポンのデパート", "ガシャポンのデパート 秋葉原"),
    ("アニメイト秋葉原", "アニメイト秋葉原"),
    ("まんだらけ 複合店", "まんだらけ 秋葉原"),
    ("アキバ・トリム", "アキバ・トリム"),
    ("ヨドバシ Akiba", "ヨドバシAkiba"),
    ("すし土風炉 秋葉原店", "すし土風炉 秋葉原"),
    ("焼肉トラジ 秋葉原店", "焼肉トラジ 秋葉原"),
    ("えん アトレヴィ秋葉原店", "手作り料理とお酒 えん アトレヴィ秋葉原"),
    ("まぐろ人", "まぐろ人 秋葉原"),
    ("但馬屋", "但馬屋 ヨドバシアキバ"),
    ("築地すし好 アキバトリム", "築地すし好 アキバトリム"),
    ("ウメ子の家 秋葉原", "ウメ子の家 秋葉原駅前店"),
    ("一風堂 秋葉原", "一風堂 秋葉原"),
    ("秋葉原站", "秋葉原駅"),
    # Day3
    ("上野動物園", "上野動物園"),
    ("國立科學博物館", "国立科学博物館"),
    ("澀谷 SKY", "SHIBUYA SKY"),
    ("Scramble Square", "渋谷スクランブルスクエア"),
    ("MEGA 唐吉訶德澀谷", "ドン・キホーテ 渋谷店"),
    ("teamLab Planets", "teamLab Planets TOKYO"),
    ("豐洲千客萬來", "豊洲市場 千客万来"),
    ("葛西臨海水族園", "葛西臨海水族園"),
    ("葛西臨海公園", "葛西臨海公園"),
    ("東京鐵塔", "東京タワー"),
    ("明治神宮", "明治神宮"),
    ("表參道", "表参道"),
    ("原宿", "原宿駅"),
    ("WEGO 原宿本店", "WEGO 原宿本店"),
    ("WEGO SHIBUYA109", "WEGO 渋谷109"),
    ("Park Side Cafe", "パークサイドカフェ 上野"),
    ("邁泉炸豬排", "まい泉 青山本店"),
    ("魚べい", "魚べい 渋谷道玄坂"),
    ("壽司郎 澀谷", "スシロー 渋谷"),
    ("博多風龍 澀谷店", "博多風龍 渋谷店"),
    ("思い出橫丁", "思い出横丁"),
    # Day4
    ("豐洲市場", "豊洲市場"),
    ("仲家", "仲家 豊洲市場"),
    ("神樂坂", "神楽坂"),
    ("神樂坂 鳥茶屋", "鳥茶屋 神楽坂"),
    ("神樂坂まつり 阿波舞", "神楽坂まつり 阿波踊り"),
    ("飯田橋站", "飯田橋駅"),
    ("名代 富士そば 飯田橋", "名代富士そば 飯田橋"),
    # Day5
    ("東京晴空塔", "東京スカイツリー"),
    ("晴空塔", "東京スカイツリー"),
    ("Solamachi", "東京ソラマチ"),
    ("墨田水族館", "すみだ水族館"),
    ("隅田公園", "隅田公園"),
    ("隅田川花火", "隅田川花火大会"),
    ("淺草文化觀光中心", "浅草文化観光センター"),
    ("トリトン", "回転寿司トリトン ソラマチ"),
    ("利久牛舌 Solamachi", "利久 東京ソラマチ"),
    ("利久 ソラマチ", "利久 東京ソラマチ"),
    # Day6
    ("品川神社", "品川神社"),
    ("Maxell Aqua Park 品川", "マクセル アクアパーク品川"),
    ("Aqua Park 品川", "マクセル アクアパーク品川"),
    ("Atre 品川", "アトレ品川"),
    ("ecute 品川", "ecute品川"),
    ("利久牛舌品川", "利久 品川"),
    ("味街道 五十三次", "味街道 五十三次 品川"),
    ("味街道 五十三次", "味街道 五十三次 品川"),
    ("T.Y.HARBOR", "T.Y.HARBOR"),
    ("天王洲運河", "天王洲運河"),
    ("高輪格蘭王子 Lounge Momiji", "高輪格蘭王子 ラウンジもみじ"),
    ("WEGO ルミネエスト新宿", "WEGO ルミネエスト新宿"),
    # Day7 / 共通
    ("不忍池", "不忍池"),
    ("二木の菓子", "二木の菓子 上野"),
    ("名代 富士そば 上野", "名代富士そば 上野"),
    ("都民廣場", "東京都庁 都民広場"),
    ("都廳前站", "都庁前駅"),
    ("東京都廳第一本廳舍", "東京都庁第一本庁舎"),
    ("新宿都廳", "東京都庁"),
    ("澀谷站", "渋谷駅"),
    ("新宿站", "新宿駅"),
    ("大統領", "大統領 上野"),
    ("とんかつ蓬莱屋 上野", "とんかつ蓬莱屋 上野"),
    ("焼肉ライク 上野", "焼肉ライク 上野"),
    ("ecute 上野", "ecute上野"),
    ("松屋", "松屋 上野"),
    ("すき家", "すき家 上野"),
    ("Beck's Coffee 上野", "ベックスコーヒーショップ 上野"),
    ("吉野家 上野站前", "吉野家 上野駅前"),
    ("天房", "天房 豊洲市場"),
    ("八千代", "八千代 豊洲市場"),
    ("蓬莱屋", "とんかつ蓬莱屋 上野"),
    ("焼肉ライク", "焼肉ライク 上野"),
    ("壽司郎", "スシロー 渋谷"),
    ("②トラジ", "焼肉トラジ 秋葉原"),
    ("⑥築地すし好", "築地すし好 アキバトリム"),
    ("③えん", "えん アトレヴィ秋葉原"),
    ("⑦ウメ子の家", "ウメ子の家 秋葉原駅前店"),
    ("PRONTO", "PRONTO 上野"),
    ("淺草", "浅草"),
    ("押上站", "押上駅"),
    ("大山", "串焼き・処 大山 上野"),
    ("富士そば", "名代富士そば"),
    ("@home cafe", "@home cafe 秋葉原"),
    ("いっぺこっぺ", "いっぺこっぺ 秋葉原"),
    ("teamLab", "teamLab Planets TOKYO"),
    ("國科博", "国立科学博物館"),
    ("淺草寺", "浅草寺"),
    ("雷門", "雷門 浅草"),
    ("VASARA", "VASARA 浅草"),
    ("千客萬來", "豊洲市場 千客万来"),
    ("東武晴空塔", "東京スカイツリー"),
    ("押上", "押上駅"),
    ("國立科學博物館", "国立科学博物館"),
    ("科博", "国立科学博物館"),
    ("拉麵街", "東京ラーメンストリート"),
    ("東京站", "東京駅"),
    ("御徒町", "御徒町駅"),
    ("品川站", "品川駅"),
    ("豐洲站", "豊洲駅"),
    ("押上／淺草", "押上駅"),
]


def gmap_url(query: str) -> str:
    return f"https://www.google.com/maps/search/?api=1&query={quote(query)}"


def gmap_link(query: str, label: str = "📍地圖") -> str:
    return (
        f'<a class="gmap" href="{gmap_url(query)}" target="_blank" '
        f'rel="noopener" title="Google Maps：{query}">{label}</a>'
    )


def inject_css(html: str) -> str:
    if "a.gmap{" in html:
        return html
    return html.replace("</style>", GMAP_CSS + "\n</style>", 1)


def convert_maps_codes(html: str) -> str:
    """Maps：<code>QUERY</code> → clickable link."""

    def repl(m: re.Match[str]) -> str:
        q = m.group(1).strip()
        return f'Maps：{gmap_link(q, q)}'

    return re.sub(r"Maps：<code>([^<]+)</code>", repl, html)


def _inside_html_tag(html: str, pos: int) -> bool:
    """True if pos is inside an HTML tag (element or attribute)."""
    before = html[:pos]
    last_lt = before.rfind("<")
    last_gt = before.rfind(">")
    return last_lt > last_gt


def _has_gmap_after(html: str, end: int, window: int = 140) -> bool:
    return 'class="gmap"' in html[end : end + window]


def insert_pins(html: str) -> str:
    """Append 📍地圖 after place names (skip if pin already nearby)."""
    places = sorted(PLACES, key=lambda x: len(x[0]), reverse=True)
    for text, query in places:
        pattern = re.compile(re.escape(text))

        def repl(m: re.Match[str], q: str = query) -> str:
            if _inside_html_tag(html, m.start()):
                return m.group(0)
            if _has_gmap_after(html, m.end()):
                return m.group(0)
            return m.group(0) + gmap_link(q)

        html = pattern.sub(repl, html)
    return html


def strip_duplicate_pins(html: str) -> str:
    """Remove redundant gmap links (same place pinned twice)."""
    gmap = r'<a class="gmap" href="[^"]+"[^>]*>📍地圖</a>'

    # Same URL back-to-back
    html = re.sub(
        rf"({gmap})\s*{gmap}",
        r"\1",
        html,
    )
    # Maps: label link + 📍地圖 duplicate
    html = re.sub(
        rf"({gmap})\s*{gmap}",
        r"\1",
        html,
    )
    # Link inside </b> then duplicate immediately after </b>
    html = re.sub(
        rf"({gmap}</b>){gmap}",
        r"\1",
        html,
    )
    # teamLab<a> Planets<a> (same venue)
    teamlab = re.escape(gmap_url("teamLab Planets TOKYO"))
    html = re.sub(
        rf'(<a class="gmap" href="{teamlab}"[^>]+>📍地圖</a>)\s*Planets<a class="gmap" href="{teamlab}"[^>]+>📍地圖</a>',
        r"\1 Planets",
        html,
    )
    # 押上<a>站<a> → 押上站<a>
    oshiage = re.escape(gmap_url("押上駅"))
    html = re.sub(
        rf'押上<a class="gmap" href="{oshiage}"[^>]+>📍地圖</a>站<a class="gmap" href="{oshiage}"[^>]+>📍地圖</a>',
        f'押上站{gmap_link("押上駅")}',
        html,
    )
    # 赤城神社<a>参道<a> → 赤城神社参道<a>
    sando = re.escape(gmap_url("赤城神社参道"))
    jinja = re.escape(gmap_url("赤城神社 神楽坂"))
    html = re.sub(
        rf'赤城神社<a class="gmap" href="{jinja}"[^>]+>📍地圖</a>参道<a class="gmap" href="{sando}"[^>]+>📍地圖</a>',
        f'赤城神社参道{gmap_link("赤城神社参道")}',
        html,
    )
    # 神楽坂下<a>交差点 + 神楽坂下交差点<a> → keep one at end of phrase
    shita = re.escape(gmap_url("神楽坂下 飯田橋"))
    shita_x = re.escape(gmap_url("神楽坂下交差点 飯田橋"))
    html = re.sub(
        rf'神楽坂下<a class="gmap" href="{shita}"[^>]+>📍地圖</a>交差點</b><br>（坡底起點）<a class="gmap" href="{shita_x}"[^>]+>📍地圖</a>',
        f'神楽坂下交差點</b><br>（坡底起點）{gmap_link("神楽坂下交差点 飯田橋")}',
        html,
    )
    html = re.sub(
        rf'神楽坂下<a class="gmap" href="{shita}"[^>]+>📍地圖</a>交差點</b><br>（坡底起點）<a class="gmap" href="{shita_x}"[^>]+>📍地圖</a>',
        f'神楽坂下交差點</b><br>（坡底起點）{gmap_link("神楽坂下交差点 飯田橋")}',
        html,
    )
    # 善國寺<a></b><a> duplicate after bold
    zenkoku = re.escape(gmap_url("毘沙門天 善國寺"))
    html = re.sub(
        rf'(<b>毘沙門天 善國寺<a class="gmap" href="{zenkoku}"[^>]+>📍地圖</a></b>){gmap}',
        r"\1",
        html,
    )
    html = re.sub(
        rf'(<b>毘沙門天 善國寺<a class="gmap" href="{zenkoku}"[^>]+>📍地圖</a>前</b><br>（祭典核心區）){gmap}',
        r"\1",
        html,
    )
    # 坂上交差点<a></b><a>
    sakaue = re.escape(gmap_url("神楽坂上交差点"))
    html = re.sub(
        rf'(<b>坂上交差点<a class="gmap" href="{sakaue}"[^>]+>📍地圖</a></b>){gmap}',
        r"\1",
        html,
    )
    # 三菱UFJ<a> 地下</b><a>
    mufg = re.escape(gmap_url("三菱UFJ銀行 神楽坂下"))
    html = re.sub(
        rf'(<b>三菱UFJ<a class="gmap" href="{mufg}"[^>]+>📍地圖</a> 地下</b>){gmap}',
        r"\1",
        html,
    )
    # Generic: any </a></b><a gmap> where previous gmap within 200 chars
    # (handled by </b> rule above for most cases)

    # Loop until stable for chained same-URL dups
    prev = None
    while prev != html:
        prev = html
        html = re.sub(rf"({gmap})\s*\1", r"\1", html)

    html = _strip_gmap_after_bold(html)
    html = _strip_station_suffix_dup(html)
    return html


def _strip_gmap_after_bold(html: str) -> str:
    """Drop gmap after </b> (or shortly after) when bold already has the same href."""
    pat = re.compile(
        r'(<b>(?:(?!</b>).)*<a class="gmap" href="([^"]+)"[^>]*>📍地圖</a>(?:(?!</b>).)*</b>)'
        r'(?:[^<]{0,40})?<a class="gmap" href="\2"[^>]*>📍地圖</a>'
    )
    return pat.sub(r"\1", html)


def _strip_station_suffix_dup(html: str) -> str:
    """飯田橋站<a>西口</b><a> → 飯田橋駅西口<a>；神楽坂下<a>Starbucks…"""
    rules = [
        (
            r'飯田橋站<a class="gmap" href="[^"]+"[^>]+>📍地圖</a>西口</b><a class="gmap" href="[^"]+"[^>]+>📍地圖</a>',
            f"飯田橋駅西口{gmap_link('飯田橋駅西口')}",
        ),
        (
            r'<b>Starbucks 神楽坂下<a class="gmap" href="[^"]+"[^>]+>📍地圖</a>店前十字路口</b><a class="gmap" href="[^"]+"[^>]+>📍地圖</a>',
            f"<b>Starbucks 神楽坂下店前十字路口{gmap_link('Starbucks 神楽坂下')}</b>",
        ),
        (
            r'<b>首選①神楽坂下<a class="gmap" href="[^"]+"[^>]+>📍地圖</a> Starbucks 前</b><a class="gmap" href="[^"]+"[^>]+>📍地圖</a>',
            f"<b>首選① Starbucks 神楽坂下店前{gmap_link('Starbucks 神楽坂下')}</b>",
        ),
        (
            r'赤城神社<a class="gmap" href="([^"]+)"[^>]+>📍地圖</a>鳥居前</b><a class="gmap" href="\1"[^>]+>📍地圖</a>',
            r'赤城神社鳥居前<a class="gmap" href="\1" target="_blank" rel="noopener" title="Google Maps：赤城神社 神楽坂">📍地圖</a>',
        ),
        (
            r'（6丁目会場）<a class="gmap" href="[^"]+"[^>]+>📍地圖</a></td>',
            "（6丁目会場）</td>",
        ),
    ]
    for pattern, repl in rules:
        html = re.sub(pattern, repl, html)
    return html


def add_maps_keyword_list(html: str) -> str:
    """Maps 關鍵字速查 block in 秋葉原導覽 — ensure ol items have pins."""
    ol_items = [
        ("K-BOOKS 秋葉原本館", "K-BOOKS 秋葉原本館"),
        ("ラジオ会館", "秋葉原ラジオ会館"),
        ("ヨドバシカメラ マルチメディア Akiba", "ヨドバシカメラ マルチメディアAkiba"),
        ("ガシャポンのデパート", "ガシャポンのデパート 秋葉原"),
        ("アニメイト秋葉原", "アニメイト秋葉原"),
        ("まんだらけ 複合店", "まんだらけ 秋葉原"),
    ]
    for label, query in ol_items:
        old = f"<b>{label}</b>"
        new = f"<b>{label}</b>{gmap_link(query)}"
        if old in html and new not in html:
            html = html.replace(old, new, 1)
    return html


def fix_contextual_links(html: str) -> str:
    """Correct links where a shorter place name matched the wrong branch."""
    solamachi = gmap_link("利久 東京ソラマチ")
    html = re.sub(
        r'利久牛舌<a class="gmap" href="[^"]+" target="_blank" '
        r'rel="noopener" title="Google Maps：利久 品川">📍地圖</a>\s*Solamachi',
        "利久牛舌" + solamachi + " Solamachi",
        html,
    )
    html = re.sub(
        r'或 利久牛舌<a class="gmap" href="[^"]+" target="_blank" '
        r'rel="noopener" title="Google Maps：利久 品川">📍地圖</a>）',
        "或 利久牛舌" + solamachi + "）",
        html,
    )
    # 東武晴空塔「站」應導向押上駅，不是晴空塔本體
    oshiage = gmap_link("押上駅")
    html = re.sub(
        r'東武晴空塔<a class="gmap" href="[^"]+" target="_blank" '
        r'rel="noopener" title="Google Maps：東京スカイツリー">📍地圖</a>站',
        "東武晴空塔" + oshiage + "站",
        html,
    )
    # 抵成田 duplicate pins → single 成田機場 link
    narita = gmap_link("成田国際空港")
    html = re.sub(
        r'抵成田<a class="gmap" href="[^"]+"[^>]+>📍地圖</a>，'
        r'<a class="gmap" href="[^"]+"[^>]+>📍地圖</a>',
        "抵成田機場" + narita + "，",
        html,
    )
    return html


def fix_overview_gaps(html: str) -> str:
    """Idempotent fixes for overview lines that auto-pin misses."""
    pairs = [
        (
            "HARBS 若排隊太長就直接改 <b>みはし / otto e sette</b>",
            f"HARBS{gmap_link('HARBS PARCO_ya 上野')} 若排隊太長就直接改 "
            f"<b>みはし{gmap_link('みはし 上野本店')} / otto e sette"
            f"{gmap_link('廚 otto e sette 上野')}</b>",
        ),
        (
            "JR 上野 → 橫濱 → 新杉田 → Seaside Line",
            f"JR 上野 → 橫濱 → 新杉田站{gmap_link('新杉田駅')} → Seaside Line",
        ),
        (
            "D1 上野：HARBS 下午茶",
            f"D1 上野：HARBS{gmap_link('HARBS PARCO_ya 上野')} 下午茶",
        ),
        (
            "12:25</span> 抵達成田 →",
            f"12:25</span> 抵達成田機場{gmap_link('成田国際空港')} →",
        ),
        (
            "Skyliner 成田 → 京成上野（",
            f"Skyliner 成田機場站{gmap_link('成田空港駅')} → 京成上野站{gmap_link('京成上野駅')}（",
        ),
        (
            "秋葉原半日 ACG 導覽",
            f"秋葉原{gmap_link('秋葉原駅')}半日 ACG 導覽",
        ),
    ]
    for old, new in pairs:
        if old in html:
            html = html.replace(old, new, 1)
    return html


def main() -> None:
    path = SOURCE
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    html = path.read_text(encoding="utf-8")
    html = inject_css(html)
    html = convert_maps_codes(html)
    html = insert_pins(html)
    html = strip_duplicate_pins(html)
    html = add_maps_keyword_list(html)
    html = fix_contextual_links(html)
    html = fix_overview_gaps(html)
    path.write_text(html, encoding="utf-8")
    count = len(re.findall(r'class="gmap"', html))
    print(f"Wrote {path.name} ({count} Google Maps links)")


if __name__ == "__main__":
    main()
