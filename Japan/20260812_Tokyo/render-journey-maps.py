#!/usr/bin/env python3
"""Render August 2026 Tokyo journey overview + daily maps as PNGs."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets"
W, H = 1024, 1536

PINGFANG = (
    "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/"
    "3419f2a427639ad8c8e139149a287865a90fa17e.asset/AssetData/PingFang.ttc"
)
EMOJI_FONT = "/System/Library/Fonts/Apple Color Emoji.ttc"
FALLBACK = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"

THEME = {
    1: ("#fff1f5", "#ff9db5", "#d7567c"),
    2: ("#ebfbff", "#71cbe8", "#2586a5"),
    3: ("#f5efff", "#b99df2", "#7756bc"),
    4: ("#eafff5", "#79d9ae", "#2b986b"),
    5: ("#fff5df", "#ffc46b", "#bd771d"),
    6: ("#eef7ff", "#8abcf4", "#3f78b8"),
    7: ("#effced", "#8fd38d", "#4e9d50"),
}

OVERVIEW = {
    "title": "東京 7 日清新旅程地圖",
    "subtitle": "2026/8/12 – 8/18｜上野基地｜每日路線・三餐・排隊提醒",
    "stations": [
        ("1", "8/12", "抵達・阿美橫", "✈️", "HARBS／海鮮丼"),
        ("2", "8/13", "八景島海洋", "🐬", "海鮮BBQ／秋葉原"),
        ("3", "8/14", "原宿・澀谷", "🌃", "邁泉／魚べい"),
        ("4", "8/15", "葛西・teamLab", "✨", "豐洲海鮮丼"),
        ("5", "8/16", "深川・晴空塔", "🗼", "トリトン／叙々苑"),
        ("6", "8/17", "品川水族館", "🌊", "利久牛舌"),
        ("7", "8/18", "上野文化・返家", "🏛️", "上野定食／機場"),
    ],
    "tips": [
        "Suica/ICOCA 單嗶最彈性",
        "餐廳排隊超過30分就切備案",
        "光雕秀日先倒推回程時間",
        "8月午後以室內和冷氣動線優先",
    ],
}

DAYS = [
    {
        "id": 1,
        "date": "8/12(三)",
        "title": "抵達・上野下午茶・阿美橫町",
        "subtitle": "成田進東京｜輕鬆收心",
        "stops": [
            ("12:25", "成田機場抵達", "VJW掃碼、領行李；人多不用衝車", "✈️"),
            ("14:10", "Skyliner → 京成上野", "直達約41分；現場買來回票較省", "🚄"),
            ("15:00", "飯店 Check-in/寄行李", "京成上野步行約5–8分", "🏨"),
            ("15:30", "上野下午茶", "HARBS若排太久改みはし/otto e sette", "🍰"),
            ("16:30", "阿美橫町逛街", "藥妝、零食、海鮮乾貨；先看價再買", "🛍️"),
            ("18:00", "阿美橫晚餐", "アメ横食堂主線；不排久候名店", "🍱"),
            ("20:30", "超市/便利店補給", "買宵夜與Day2早餐；21:00回飯店", "🛒"),
        ],
        "meals": [
            ("下午茶", "HARBS PARCO_ya 上野", "15:30前到；排>30分改みはし"),
            ("晚餐", "アメ横食堂/山家/天丼てんや", "18:00左右；排隊長就換店"),
            ("宵夜", "OK店/便利店/松屋", "20:30–21:00補明日早餐"),
        ],
        "notes": ["入境後先買Skyliner來回", "第一天不排遠點", "現金零錢可在便利店找開"],
        "alts": ["雨天：PARCO_ya/atre室內", "甜點備案：みはし、otto e sette"],
    },
    {
        "id": 2,
        "date": "8/13(四)",
        "title": "橫濱八景島海洋之夢",
        "subtitle": "大型水族館避暑｜傍晚二選一",
        "stops": [
            ("07:30", "上野早餐外帶", "ecute/Andersen；車上吃最省時", "🥐"),
            ("08:00", "上野 → 八景島", "JR+金澤海岸線約70–90分", "🚃"),
            ("10:00", "Aqua Museum大水槽", "入館直奔；沙丁魚秀前10–15分卡位", "🐟"),
            ("11:30", "Dolphin Fantasy", "拱形水槽走動參觀，不需久等", "🐬"),
            ("12:00", "園內午餐", "YAKIYA/美食街；12:30後易排長", "🦐"),
            ("13:00", "Animal Life Live", "4Fライブスタジアム提前20–30分坐", "🎪"),
            ("14:00", "Fureai Lagoon", "企鵝、近距離海豚；看當日表演表", "🐧"),
            ("16:00", "傍晚分岔", "A東京站輕鬆；B秋葉原ACG", "🔀"),
        ],
        "meals": [
            ("早餐", "Andersen/ecute 上野", "07:30外帶，避免找座位"),
            ("午餐", "YAKIYA海鮮BBQ/園內美食街", "12:00前入座；排>30分改輕食"),
            ("晚餐", "東京拉麵街/秋葉原8選1", "依A/B備案；20:45後秋葉原吃"),
        ],
        "notes": ["表演時間以官網為準", "午餐與Live座位要倒推", "16:00車上決定東京站或秋葉原"],
        "alts": ["A：東京站拉麵街＋一番街", "B：秋葉原ACG＋日式晚餐"],
    },
    {
        "id": 3,
        "date": "8/14(五)",
        "title": "明治神宮・原宿・澀谷避暑",
        "subtitle": "午餐後直往澀谷｜19:30光雕秀",
        "stops": [
            ("08:30", "上野 → 原宿", "山手線約28分；先買水", "🚃"),
            ("09:00", "明治神宮短走", "只到主殿與鳥居；10:15前離開", "⛩️"),
            ("10:30", "原宿WEGO/竹下通", "進店吹冷氣；不戶外慢逛", "🛍️"),
            ("11:30", "表參道・青山午餐", "邁泉主推；排太久改室內餐廳", "🍱"),
            ("13:00", "直往澀谷", "取消表參道Hills停留，保留後段時間", "🚇"),
            ("13:30", "澀谷室內商場", "Hikarie/PARCO/Scramble Square挑1–2棟", "🏬"),
            ("15:30", "澀谷SKY", "搶15:30–16:00票；17:00前下樓", "🌆"),
            ("17:15", "澀谷早晚餐", "魚べい/壽司郎；16:45前App抽號", "🍣"),
            ("18:35", "澀谷 → 新宿都廳", "19:10前到都民廣場卡位", "🚃"),
            ("19:30", "都廳光雕秀", "看完直接回上野，約20:30–21:00", "✨"),
        ],
        "meals": [
            ("午餐", "まい泉青山本店", "建議訂位；現場11:00–11:30排"),
            ("午餐備", "東急プラザ/青山室內餐廳", "邁泉排>30分即改"),
            ("晚餐", "魚べい/壽司郎/博多風龍", "16:45抽號；18:15未入座改拉麵"),
        ],
        "notes": ["午餐後直往澀谷", "18:35前必離開澀谷", "19:30光雕秀優先不延後"],
        "alts": ["澀谷室內：Hikarie/PARCO多逛", "新宿備案：無SKY票改都廳展望"],
    },
    {
        "id": 4,
        "date": "8/15(六・山の日)",
        "title": "葛西・豐洲・teamLab＋週末光雕秀",
        "subtitle": "teamLab只排今天｜新宿秀前晚餐",
        "stops": [
            ("08:30", "上野出發", "帶毛巾、輕便鞋；夏日補水", "🏨"),
            ("09:30", "葛西臨海水族園", "水族館約2小時；不硬排戶外太久", "🐟"),
            ("12:00", "豐洲市場午餐", "海鮮丼主線；熱門店排久就改美食街", "🍣"),
            ("14:00", "teamLab Planets", "短褲/可捲褲管；赤腳入場", "🌈"),
            ("16:15", "豐洲 → 新宿/都廳前", "約35–50分，先抓寬", "🚇"),
            ("17:15", "新宿秀前晚餐", "19:00前離開餐廳去都民廣場", "🍜"),
            ("19:30", "都民廣場光雕秀", "週末/山の日優先對TIMETABLE", "✨"),
            ("21:15", "回上野", "宵夜改便利店/ライク；不排陽山道", "🏨"),
        ],
        "meals": [
            ("早餐", "上野便利店/飯店早餐", "08:30前完成"),
            ("午餐", "豐洲海鮮丼/美食街", "12:00前後；排>30分換店"),
            ("晚餐", "新宿思い出橫丁/西口拉麵", "17:15–19:00，秀前吃完"),
        ],
        "notes": ["不訂陽山道19:00", "不排燈籠流/とよす夏祭", "teamLab與光雕秀都要倒推"],
        "alts": ["光雕秀19:30或21:00依官網", "晚餐快速：新宿站西口拉麵/定食"],
    },
    {
        "id": 5,
        "date": "8/16(日)",
        "title": "深川水かけ＋晴空塔・Solamachi",
        "subtitle": "上午祭典｜午後室內避暑｜上野慶祝晚餐",
        "stops": [
            ("06:50", "上野 → 門前仲町", "早出避人潮；帶毛巾與防水袋", "🚃"),
            ("07:30", "深川水かけ祭", "主看神輿；10:00前離場避擁擠", "🎏"),
            ("10:30", "移動晴空塔", "先吹冷氣、整理濕衣物", "🚇"),
            ("11:00", "Solamachi午餐取號", "トリトン先取號；排久改利久/美食街", "🍣"),
            ("13:00", "室內選配", "Pokemon/千葉工大/郵政博物館擇一", "📮"),
            ("15:30", "淺草或Solamachi續逛", "酷熱就不去淺草，留室內", "🏯"),
            ("18:30", "回上野", "叙々苑19:00；建議先訂", "🚃"),
            ("19:00", "叙々苑晚餐", "慶祝晚餐；不去とよす夏祭", "🥩"),
        ],
        "meals": [
            ("早餐", "便利店輕食", "06:30前買好，邊移動邊吃"),
            ("午餐", "トリトンSolamachi/利久", "11:00取號；排>60分改利久"),
            ("晚餐", "叙々苑上野", "建議訂19:00；18:30前回上野"),
        ],
        "notes": ["祭典會濕，手機防水", "10:00前離深川", "午後以Solamachi室內為主"],
        "alts": ["墨田水族館可加但不硬排", "淺草只陰涼/體力好才快閃"],
    },
    {
        "id": 6,
        "date": "8/17(一)",
        "title": "品川 Aqua Park＋平日光雕秀",
        "subtitle": "日間＋夜間雙秀｜品川冷氣日",
        "stops": [
            ("09:30", "上野 → 品川", "山手線約25分；先到Atre", "🚃"),
            ("10:30", "利久牛舌排隊", "11:00入座最佳；排久改味街道/站內", "🥩"),
            ("12:15", "Aqua Park日間館內", "先看館內與日間海豚秀；時間看官網", "🐬"),
            ("15:00", "Atre/ecute冷氣休息", "補咖啡、伴手禮；保留再入場體力", "🛍️"),
            ("17:30", "再入園卡位", "夜間雷射海豚秀前入場就座", "🌊"),
            ("19:30", "品川 → 新宿都廳", "看20:30/21:00場，出發前對表", "🚃"),
            ("20:30", "都廳光雕秀", "平日可能非寶可夢；以官網為準", "✨"),
            ("21:30", "回上野宵夜", "大山/ライク/便利店，隔天早退房", "🏨"),
        ],
        "meals": [
            ("早餐", "飯店/ecute上野", "09:00前簡單吃"),
            ("午餐", "利久牛舌Atre品川", "10:30排；排>40分改味街道"),
            ("宵夜", "上野大山/焼肉ライク/松屋", "21:30後快速補食"),
        ],
        "notes": ["買可再入場票", "海豚秀時間每日查官網", "光雕秀平日作品需對TIMETABLE"],
        "alts": ["品川神社可縮短", "購物優先可放棄夜間水族秀"],
    },
    {
        "id": 7,
        "date": "8/18(二)",
        "title": "上野文化半日・返家",
        "subtitle": "20:40成田起飛｜午後Skyliner",
        "stops": [
            ("07:30", "早餐＋不忍池晨散", "荷花早上最舒服；09:20前回飯店", "🪷"),
            ("09:30", "退房寄行李", "行李寄飯店，貴重物隨身", "🧳"),
            ("10:15", "東京國立博物館", "常設展抓2小時；不要貪館", "🏛️"),
            ("12:30", "上野午餐", "定食/蕎麥/炸豬排；不排久候名店", "🍜"),
            ("13:30", "最後採買", "阿美橫/PARCO_ya/ecute擇一", "🛍️"),
            ("15:00", "飯店取行李", "15:30前完成整裝", "🧳"),
            ("16:00", "Skyliner → 成田", "最晚16:30左右離京成上野", "🚄"),
            ("17:00", "成田機場", "報到、托運、安檢後晚餐免稅", "✈️"),
            ("20:40", "起飛返台", "機場晚餐不在市區拖時間", "🛫"),
        ],
        "meals": [
            ("早餐", "Andersen/富士そば/飯店", "07:30前後，輕食即可"),
            ("午餐", "上野定食/蕎麥/炸豬排", "12:30–13:30；避免排隊名店"),
            ("晚餐", "成田機場安檢後", "18:00後吃，保留托運安檢時間"),
        ],
        "notes": ["退房後先寄行李", "15:00回飯店取行李", "最晚16:30離上野"],
        "alts": ["不逛博物館：淺草半日", "低體力：PARCO_ya/ecute室內採買"],
    },
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    # PingFang.ttc: prefer TC Regular / Semibold indices (often 2/5 or nearby)
    for idx in ((5, 2) if bold else (2, 0, 1)):
        try:
            return ImageFont.truetype(PINGFANG, size, index=idx)
        except OSError:
            continue
    return ImageFont.truetype(FALLBACK, size)


def emoji_font(size: int = 64) -> ImageFont.FreeTypeFont:
    # Apple Color Emoji only accepts specific pixel sizes
    allowed = (20, 32, 40, 48, 64, 96, 160)
    size = min(allowed, key=lambda s: abs(s - size))
    return ImageFont.truetype(EMOJI_FONT, size)


def rounded_rect(draw: ImageDraw.ImageDraw, xy, fill, radius=18, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def draw_text_center(draw, xy, text, fnt, fill, embedded_color=False):
    tw, th = text_size(draw, text, fnt)
    kwargs = {"embedded_color": True} if embedded_color else {}
    draw.text((xy[0] - tw / 2, xy[1] - th / 2), text, font=fnt, fill=fill, **kwargs)


def draw_emoji(im: Image.Image, xy, emoji: str, size: int = 40):
    """Paste a color emoji centered at xy onto RGBA-capable image."""
    ef = emoji_font(size)
    # render on transparent tile
    tile = Image.new("RGBA", (size + 8, size + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    # Apple emoji glyph is square; draw at origin
    d.text((4, 0), emoji, font=ef, embedded_color=True)
    # crop non-empty
    bbox = tile.getbbox()
    if not bbox:
        return
    glyph = tile.crop(bbox)
    gx, gy = xy[0] - glyph.width // 2, xy[1] - glyph.height // 2
    base = im.convert("RGBA")
    base.alpha_composite(glyph, (int(gx), int(gy)))
    im.paste(base.convert("RGB"))


def soft_bg(im: Image.Image, accent: str):
    base = im.convert("RGBA")
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for i in range(14):
        x = int((i * 139 + 90) % W)
        y = int((i * 211 + 60) % H)
        r = 80 + (i * 23) % 115
        c = accent if i % 2 == 0 else "#d9f5ff"
        rgb = tuple(int(c.lstrip("#")[j : j + 2], 16) for j in (0, 2, 4))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(*rgb, 55))
    wash = Image.new("RGBA", (W, H), (255, 253, 246, 80))
    out = Image.alpha_composite(Image.alpha_composite(base, layer), wash)
    im.paste(out.convert("RGB"))


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt, max_width: int, max_lines: int = 3) -> list[str]:
    if not text:
        return []
    lines: list[str] = []
    current = ""
    for ch in text:
        candidate = current + ch
        if text_size(draw, candidate, fnt)[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = ch
            if len(lines) == max_lines - 1:
                break
    if current and len(lines) < max_lines:
        lines.append(current)
    if len(lines) == max_lines and len("".join(lines)) < len(text):
        lines[-1] = lines[-1].rstrip("，；、 ") + "…"
    return lines


def draw_wrapped(draw, xy, text: str, fnt, fill, max_width: int, line_gap: int = 4, max_lines: int = 3):
    y = xy[1]
    for line in wrap_text(draw, text, fnt, max_width, max_lines=max_lines):
        draw.text((xy[0], y), line, font=fnt, fill=fill)
        y += fnt.size + line_gap
    return y


def draw_stop(im: Image.Image, x, y, time, title, note, icon, color):
    draw = ImageDraw.Draw(im)
    r = 28
    draw.ellipse((x - r + 3, y - r + 4, x + r + 3, y + r + 4), fill="#d9dde6")
    draw.ellipse((x - r, y - r, x + r, y + r), fill="#ffffff", outline=color, width=4)
    draw_emoji(im, (x, y), icon, size=32)
    draw = ImageDraw.Draw(im)  # refresh after paste
    card_x, card_y = x + 46, y - 38
    card_w, card_h = 310, 82
    if card_x + card_w > W - 38:
        card_x = x - 46 - card_w
    rounded_rect(draw, (card_x, card_y, card_x + card_w, card_y + card_h), fill="#fffffb", radius=14, outline="#e8dfd6", width=2)
    draw.rounded_rectangle((card_x + 10, card_y + 10, card_x + 82, card_y + 36), radius=8, fill=color)
    draw_text_center(draw, (card_x + 46, card_y + 23), time, font(13, bold=True), "#ffffff")
    draw.text((card_x + 92, card_y + 9), title, font=font(17, bold=True), fill="#4f3d3d")
    draw_wrapped(draw, (card_x + 14, card_y + 42), note, font(12), "#6e625d", card_w - 28, max_lines=2)


def render_overview() -> Image.Image:
    im = Image.new("RGB", (W, H), "#fffdf7")
    soft_bg(im, "#e9f7ff")
    draw = ImageDraw.Draw(im)

    rounded_rect(draw, (34, 28, W - 34, 138), fill="#fffffb", radius=28, outline="#b8e7ff", width=3)
    draw_text_center(draw, (W / 2, 66), OVERVIEW["title"], font(34, bold=True), "#4f3d3d")
    draw_text_center(draw, (W / 2, 108), OVERVIEW["subtitle"], font(18), "#6e625d")

    coords = [(170, 260), (460, 390), (270, 560), (650, 705), (350, 895), (690, 1065), (480, 1250)]
    for idx in range(len(coords) - 1):
        draw.line([coords[idx], coords[idx + 1]], fill="#ffffff", width=34)
        draw.line([coords[idx], coords[idx + 1]], fill=THEME[idx + 1][1], width=21)

    rounded_rect(draw, (355, 250, 650, 330), fill="#ffffff", radius=22, outline="#ffc46b", width=3)
    draw_emoji(im, (395, 290), "🏨", size=40)
    draw = ImageDraw.Draw(im)
    draw.text((430, 267), "上野基地", font=font(22, bold=True), fill="#bd771d")
    draw.text((430, 300), "每日回到同一住宿圈", font=font(14), fill="#6e625d")

    for (day_no, date, label, icon, food), (x, y) in zip(OVERVIEW["stations"], coords):
        light, main, dark = THEME[int(day_no)]
        draw.ellipse((x - 46 + 4, y - 46 + 6, x + 46 + 4, y + 46 + 6), fill="#dce4ec")
        draw.ellipse((x - 46, y - 46, x + 46, y + 46), fill=light, outline=dark, width=4)
        draw_emoji(im, (x, y - 8), icon, size=38)
        draw = ImageDraw.Draw(im)
        draw_text_center(draw, (x, y + 24), f"D{day_no}", font(15, bold=True), dark)
        box_w = 270
        bx = min(max(x - box_w // 2, 40), W - box_w - 40)
        by = y + 58
        rounded_rect(draw, (bx, by, bx + box_w, by + 78), fill="#fffffb", radius=16, outline=main, width=2)
        draw_text_center(draw, (bx + box_w / 2, by + 23), f"{date} {label}", font(16, bold=True), "#4f3d3d")
        draw_text_center(draw, (bx + box_w / 2, by + 52), f"三餐重點：{food}", font(13), "#6e625d")

    rounded_rect(draw, (50, 1378, W - 50, 1490), fill="#fffffb", radius=22, outline="#b8e7ff", width=3)
    draw.text((74, 1396), "共通提醒", font=font(22, bold=True), fill="#2586a5")
    y = 1432
    for tip in OVERVIEW["tips"]:
        draw.text((82, y), f"• {tip}", font=font(15), fill="#4f3d3d")
        y += 24
    return im


def road_points(n: int, top=205, bottom=930) -> list[tuple[float, float]]:
    pts = []
    left, right = 86, 790
    mid = (left + right) / 2
    amp = (right - left) / 2 - 54
    for i in range(n):
        t = i / max(n - 1, 1)
        y = top + t * (bottom - top)
        phase = math.sin(t * math.pi * 3.2 + 0.3)
        x = mid + phase * amp
        x += -26 if i % 2 == 0 else 26
        x = max(left + 40, min(right - 40, x))
        pts.append((x, y))
    return pts


def render_day(day: dict) -> Image.Image:
    light, main, dark = THEME[day["id"]]
    im = Image.new("RGB", (W, H), "#fffdf7")
    soft_bg(im, light)
    draw = ImageDraw.Draw(im)

    rounded_rect(draw, (30, 26, W - 30, 142), fill="#fffffb", radius=28, outline=main, width=3)
    draw.rounded_rectangle((54, 48, 156, 96), radius=16, fill=dark)
    draw_text_center(draw, (105, 72), f"DAY {day['id']}", font(18, bold=True), "#ffffff")
    draw.text((176, 44), day["title"], font=font(26, bold=True), fill="#4f3d3d")
    draw.text((176, 86), f"{day['date']}　{day['subtitle']}", font=font(16), fill="#6e625d")

    stops = day["stops"]
    pts = road_points(len(stops), top=205, bottom=905 if len(stops) >= 9 else 830)
    seg_colors = [main, dark, "#ffd6a5", "#9be7c9", "#9fdcff"]
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill="#ffffff", width=28)
        draw.line([pts[i], pts[i + 1]], fill=seg_colors[i % len(seg_colors)], width=17)

    for (time, title, note, icon), (x, y) in zip(stops, pts):
        draw_stop(im, x, y, time, title, note, icon, dark)

    draw = ImageDraw.Draw(im)
    y0 = 980
    rounded_rect(draw, (36, y0, W - 36, y0 + 250), fill="#fffffb", radius=22, outline=main, width=3)
    draw.rounded_rectangle((58, y0 + 18, 200, y0 + 58), radius=13, fill=main)
    draw_text_center(draw, (129, y0 + 38), "三餐備案", font(17, bold=True), "#ffffff")
    yy = y0 + 72
    for meal, place, queue in day["meals"]:
        draw.text((62, yy), f"{meal}", font=font(16, bold=True), fill=dark)
        draw.text((142, yy), place, font=font(15, bold=True), fill="#4f3d3d")
        yy = draw_wrapped(draw, (142, yy + 24), queue, font(13), "#6e625d", 780, max_lines=2) + 6

    y1 = 1252
    rounded_rect(draw, (36, y1, W - 36, y1 + 190), fill="#fffffb", radius=22, outline="#b8e7ff", width=3)
    draw.text((62, y1 + 20), "注意事項", font=font(20, bold=True), fill=dark)
    yy = y1 + 58
    for note in day["notes"]:
        yy = draw_wrapped(draw, (72, yy), f"• {note}", font(14), "#4f3d3d", 420, max_lines=2)
        yy += 7
    draw.text((536, y1 + 20), "備案/切換", font=font(20, bold=True), fill="#2586a5")
    yy = y1 + 58
    for alt in day["alts"]:
        yy = draw_wrapped(draw, (548, yy), f"• {alt}", font(14), "#4f3d3d", 390, max_lines=2)
        yy += 8

    rounded_rect(draw, (36, 1462, W - 36, 1518), fill="#fffffb", radius=16, outline="#e8dfd6", width=2)
    draw.text((62, 1480), "實線＝主線時間軸｜餐廳排隊超過30分即切備案｜住宿基地：上野｜與 tokyo-2026-08-guide 同步", font=font(13), fill="#6e625d")

    return im


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # clean test artifact
    test = OUT / "_emoji-test.png"
    if test.exists():
        test.unlink()

    print("Rendering overview…")
    render_overview().save(OUT / "overview.png", optimize=True)
    print("  -> assets/overview.png")

    for day in DAYS:
        print(f"Rendering Day {day['id']}…")
        path = OUT / f"day-{day['id']:02d}.png"
        render_day(day).save(path, optimize=True)
        print(f"  -> {path.relative_to(ROOT)}")

    print("Done.")


if __name__ == "__main__":
    main()
