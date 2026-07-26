#!/usr/bin/env python3
"""Build August 8/12–8/18 guide from July source, strip July festivals, mark free slots."""
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "20260721_Tokyo" / "tokyo-2026-guide.html"
OUT = Path(__file__).resolve().parent / "tokyo-2026-08-guide.html"
OLD_OUT = Path(__file__).resolve().parent / "tokyo-2026-guide.html"

DATE_MAP = {
    "2026/7/21–7/27": "2026/8/12–8/18",
    "2026/7/21(二) – 7/27(一)": "2026/8/12(三) – 8/18(二)",
    "7/21(二)": "8/12(三)",
    "7/22(三)": "8/13(四)",
    "7/23(四)": "8/14(五)",
    "7/24(五)": "8/15(六)",
    "7/25(六)": "8/16(日)",
    "7/26(日)": "8/17(一)",
    "7/27(一)": "8/18(二)",
    "7/21": "8/12",
    "7/22": "8/13",
    "7/23": "8/14",
    "7/24": "8/15",
    "7/25": "8/16",
    "7/26": "8/17",
    "7/27": "8/18",
}

FREE_SLOTS_SECTION = """
<!-- ============ 待安排空檔 ============ -->
<section id="free">
<h2>🕳️ 待一起安排的空檔（已移除七月慶典）</h2>
<div class="warnbox">
七月版行程中的<b>上野夏祭、神樂坂阿波舞、隅田川花火</b>皆不在 8/12–8/18 這段日期，已先拿掉。下列時段目前<b>刻意留白</b>，方便填入八月慶典或其他活動（可參考同資料夾 <a href="tokyo-2026-08-festivals-research.html">八月慶典調查</a>）。
</div>
<table>
<tr><th>日期</th><th>空檔時段</th><th>原七月安排</th><th>建議用途</th></tr>
<tr><td><b>Day4</b><br>8/15(六)<br><span class="pill w">山の日</span></td><td><span class="time">16:00–21:00</span><br><span class="muted">（約 5 小時）</span></td><td>神樂坂阿波舞＋專程晚餐</td><td>teamLab 後直接留白；可豐洲晚餐回上野，或移動至八月慶典（<b>不必去神樂坂</b>）</td></tr>
<tr><td><b>Day5</b><br>8/16(日)</td><td><span class="time">16:10–21:00</span><br><span class="muted">（約 5 小時）</span></td><td>花火野餐＋隅田川花火＋步行回上野</td><td>晴空塔展望台、淺草夜逛、Solamachi 晚餐、或八月花火／祭典</td></tr>
</table>
<div class="okbox">
<b>合計約 10 小時待排空檔</b>（Day4 5hr＋Day5 5hr）。Day1 傍晚已排<b>阿美橫町逛街＋晚餐＋採買</b>。國高生逛街見 <a href="tokyo-2026-08-ueno-local-guide.html#teen">上野手冊</a>；家電／Apple 見 <a href="tokyo-2026-08-ueno-local-guide.html#electronics">家電電子專章</a>。
</div>
</section>
"""

DAY1_SCHEDULE = """<p><span class="time">16:30–18:00</span> <b>阿美橫町<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E3%82%A2%E3%83%A1%E6%A8%AA" target="_blank" rel="noopener" title="Google Maps：アメ横">📍地圖</a>逛街</b>（药妆、零食、海鮮乾貨；見下「阿美橫町・在地生活」）。</p>
<p><span class="time">18:00–19:00</span> <b>晚餐：アメ横食堂<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E3%82%A2%E3%83%A1%E6%A8%AA%E9%A3%9F%E5%A0%82" target="_blank" rel="noopener" title="Google Maps：アメ横食堂">📍地圖</a></b>（主線推薦；阿美橫町內海鮮丼／定食，備案見下）。</p>
<p><span class="time">19:00–20:30</span> 阿美橫町<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E3%82%A2%E3%83%A1%E6%A8%AA" target="_blank" rel="noopener" title="Google Maps：アメ横">📍地圖</a>／御徒町周邊續逛（二刷攤位、室內藥妝店）。</p>
<p><span class="time">20:30–21:00</span> <b>超市<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=OK%E5%BA%97%20%E4%B8%8A%E9%87%8E" target="_blank" rel="noopener" title="Google Maps：OK店 上野">📍地圖</a>／便利店</b>採買宵夜＋<b>明日早餐</b>（回飯店前<b>必做</b>；見下）。</p>
<p><span class="time">21:00</span> 步行回飯店。</p>"""

DAY1_AMEYOKO_DETAILS = """<details>
<summary>🏪 阿美橫町・在地生活（逛街＋晚餐＋採買）</summary>
<div class="card">
<p class="muted">抵達日不趕景點，<b>16:30 起一條龍搞定逛街、晚餐、補給</b>。完整上野夜間攻略見 <a href="tokyo-2026-08-ueno-local-guide.html"><b>上野在地生活手冊</b></a>（每店附 📍地圖）。阿美橫町小攤／部分老店只收現金。</p>
<p><span class="tag d">逛街推薦（16:30–18:00 ＋ 晚餐後續逛）</span></p>
<ul>
<li><b>药妆</b>：マツモトキヨシ<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E3%83%9E%E3%83%84%E3%83%A2%E3%83%88%E3%82%AD%E3%83%A8%E3%82%B7%20%E4%B8%8A%E9%87%8E%E5%BE%A1%E5%BE%92%E7%94%BA" target="_blank" rel="noopener" title="Google Maps：マツモトキヨシ 上野御徒町">📍地圖</a>／ウエルシア<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E3%82%A6%E3%82%A8%E3%83%AB%E3%82%B7%E3%82%A2%20%E4%B8%8A%E9%87%8E" target="_blank" rel="noopener" title="Google Maps：ウエルシア 上野">📍地圖</a> — 防曬、牙刷、濕紙巾、小孩用品</li>
<li><b>零食乾貨</b>：二木の菓子<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E4%BA%8C%E6%9C%A8%E3%81%AE%E8%8F%93%E5%AD%90%20%E4%B8%8A%E9%87%8E" target="_blank" rel="noopener" title="Google Maps：二木の菓子 上野">📍地圖</a>（批發價零食）、堅果／乾果攤、T 恤一條街<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E3%82%A2%E3%83%A1%E6%A8%AA%E3%82%BB%E3%83%B3%E3%82%BF%E3%83%BC%E8%A1%97" target="_blank" rel="noopener" title="Google Maps：アメ横センター街">📍地圖</a>（¥500–1,000）</li>
<li><b>海鮮攤</b>：先問清總價再買；小孩可看章魚燒、炒麵小攤當點心（¥500–800）</li>
<li><b>ドン・キホーテ 上野店<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E3%83%89%E3%83%B3%E3%83%BB%E3%82%AD%E3%83%9B%E3%83%BC%E3%83%86%20%E4%B8%8A%E9%87%8E" target="_blank" rel="noopener" title="Google Maps：ドン・キホーテ 上野">📍地圖</a></b> — 室內吹冷氣，雜貨／零食／伴手禮（較晚也可逛）</li>
</ul>
<p><span class="tag d">晚餐備案（主線排最推薦①；擇一即可）</span></p>
<p><b>① アメ横食堂<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E3%82%A2%E3%83%A1%E6%A8%AA%E9%A3%9F%E5%A0%82" target="_blank" rel="noopener" title="Google Maps：アメ横食堂">📍地圖</a></b> ⭐ <b>主線</b> — 就在阿美橫町內，海鮮丼／定食，市場氛圍最對味。¥1,000–1,800，<b>不訂位</b>，排隊但翻桌快；帶小孩最順。</p>
<p><b>② 天丼てんや 上野店<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E5%A4%A9%E4%B8%BC%E3%81%A6%E3%82%93%E3%82%84%20%E4%B8%8A%E9%87%8E%E5%BA%97" target="_blank" rel="noopener" title="Google Maps：天丼てんや 上野店">📍地圖</a></b> — 天婦羅丼連鎖，出餐快、口味穩。¥800–1,200，<b>不訂位</b>；① 客滿或不想排隊時首選。</p>
<p><b>③ とんかつ 山家<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E3%81%A8%E3%82%93%E3%81%8B%E3%81%A4%E5%B1%B1%E5%AE%B6%20%E5%BE%A1%E5%BE%92%E7%94%BA" target="_blank" rel="noopener" title="Google Maps：とんかつ山家 御徒町">📍地圖</a>（御徒町）</b> — 在地炸豬排名店，份量大 CP 高。¥1,000–1,500，<b>不訂位</b>，17:30 後常排隊；想吃飽選這家。</p>
<p><b>④ 燒肉／拉麵／壽司（擇一，避開居酒屋）</b></p>
<ul>
<li><b>焼肉ライク 上野<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E7%84%BC%E8%82%89%E3%83%A9%E3%82%A4%E3%82%AF%20%E4%B8%8A%E9%87%8E" target="_blank" rel="noopener" title="Google Maps：焼肉ライク 上野">📍地圖</a></b> — 一人燒肉小烤爐，無菸味、小孩可吃白飯＋烤肉。¥1,000–1,500，<b>不訂位</b>。</li>
<li><b>スシロー 上野店<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E3%82%B9%E3%82%B7%E3%83%AD%E3%83%BC%20%E4%B8%8A%E9%87%8E" target="_blank" rel="noopener" title="Google Maps：スシロー 上野">📍地圖</a></b> — 迴轉壽司，平板點餐、翻桌快。¥1,000–1,800，官方 App 抽號或現場排。</li>
<li><b>煮干しラーメン 玉 上野店<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E7%85%AE%E5%B9%B2%E3%81%97%E3%83%A9%E3%83%BC%E3%83%A1%E3%83%B3%20%E7%8E%89%20%E4%B8%8A%E9%87%8E" target="_blank" rel="noopener" title="Google Maps：煮干しラーメン 玉 上野">📍地圖</a></b> — 在地人排隊的煮干拉麵（非觀光連鎖）。¥900–1,200，<b>不訂位</b>，券機點餐。</li>
</ul>
<p><span class="tag d">回飯店前必買（20:30–21:00）</span></p>
<p><b>明日早餐</b>：飯糰、牛奶、優格、布丁、麵包（まいばすけっと<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E3%81%BE%E3%81%84%E3%81%B0%E3%81%99%E3%81%91%E3%81%A3%E3%81%A8%20%E4%B8%8A%E9%87%8E" target="_blank" rel="noopener" title="Google Maps：まいばすけっと 上野">📍地圖</a>／OK ストア 上野店<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=OK%E5%BA%97%20%E4%B8%8A%E9%87%8E" target="_blank" rel="noopener" title="Google Maps：OK店 上野">📍地圖</a>）</p>
<p><b>宵夜／房內補給</b>：限定零食、飲料、冰品、泡麵（セブン<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E3%82%BB%E3%83%96%E3%83%B3%E3%82%A4%E3%83%AC%E3%83%96%E3%83%B3%20%E4%B8%8A%E9%87%8E" target="_blank" rel="noopener" title="Google Maps：セブン-イレブン 上野">📍地圖</a>／ファミマ<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E3%83%95%E3%82%A1%E3%83%9F%E3%83%AA%E3%83%9E%E3%83%BC%E3%88%8A%20%E4%B8%8A%E9%87%8E" target="_blank" rel="noopener" title="Google Maps：ファミマ 上野">📍地圖</a> 24h）</p>
<p><b>實用</b>：瓶裝水、垃圾袋（日本街上垃圾桶少）</p>
<p class="okbox">💡 <b>親子小任務</b>：晚餐後讓小孩各選一樣「只有日本有的零食」＋一個飯糰當明日早餐；回飯店前確認冰箱有牛奶／飲料。</p>
</div>
</details>
"""

DAY1_DINNER_BLOCK = """<p><span class="tag d">晚餐（18:00｜阿美橫町一帶，擇一）</span></p>
<p class="muted">主路線已排 <b>① アメ横食堂</b>；以下為備案，都在阿美橫町／御徒町步行 5–10 分內。</p>
<p><b>① アメ横食堂<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E3%82%A2%E3%83%A1%E6%A8%AA%E9%A3%9F%E5%A0%82" target="_blank" rel="noopener" title="Google Maps：アメ横食堂">📍地圖</a></b> ⭐ <b>主線</b> — 海鮮丼／定食，¥1,000–1,800，<b>不訂位</b>，翻桌快。</p>
<p><b>② 天丼てんや 上野店<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E5%A4%A9%E4%B8%BC%E3%81%A6%E3%82%93%E3%82%84%20%E4%B8%8A%E9%87%8E%E5%BA%97" target="_blank" rel="noopener" title="Google Maps：天丼てんや 上野店">📍地圖</a></b> — 天婦羅丼，¥800–1,200，<b>不訂位</b>，最穩不排隊。</p>
<p><b>③ とんかつ 山家<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E3%81%A8%E3%82%93%E3%81%8B%E3%81%A4%E5%B1%B1%E5%AE%B6%20%E5%BE%A1%E5%BE%92%E7%94%BA" target="_blank" rel="noopener" title="Google Maps：とんかつ山家 御徒町">📍地圖</a>（御徒町）</b> — 炸豬排，¥1,000–1,500，<b>不訂位</b>。</p>
<p><b>④ 焼肉ライク 上野<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E7%84%BC%E8%82%89%E3%83%A9%E3%82%A4%E3%82%AF%20%E4%B8%8A%E9%87%8E" target="_blank" rel="noopener" title="Google Maps：焼肉ライク 上野">📍地圖</a>／スシロー 上野<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E3%82%B9%E3%82%B7%E3%83%AD%E3%83%BC%20%E4%B8%8A%E9%87%8E" target="_blank" rel="noopener" title="Google Maps：スシロー 上野">📍地圖</a>／煮干しラーメン 玉 上野<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E7%85%AE%E5%B9%B2%E3%81%97%E3%83%A9%E3%83%BC%E3%83%A1%E3%83%B3%20%E7%8E%89%20%E4%B8%8A%E9%87%8E" target="_blank" rel="noopener" title="Google Maps：煮干しラーメン 玉 上野">📍地圖</a></b> — 燒肉／壽司／在地拉麵。¥800–2,000，<b>不訂位</b>。更多店見 <a href="tokyo-2026-08-ueno-local-guide.html">上野手冊</a>。</p>"""

FREED_D4_AFTER_TEAMLAB = """<p><span class="time">16:00</span> teamLab 出場（豐洲站一帶）。</p>
<p><span class="time">16:00–21:00</span> <b>🕳️ 待安排</b>（無阿波舞，<b>不必特別搭車去神樂坂</b>；見 <a href="#free">空檔總表</a>）。可先豐洲站內晚餐後回上野，或移動至八月慶典。</p>
<p><span class="time">~21:00</span> 回飯店休息。</p>"""

FREED_D4_DETAILS = """<details open>
<summary>🕳️ teamLab 後空檔（16:00–21:00｜待一起安排）</summary>
<div class="card accbox">
<p>七月版 teamLab 後會<b>專程搭車去神樂坂</b>看阿波舞（7/24 限定）。八月 8/15 無此祭典，<b>整段傍晚已留白</b>，不必為了晚餐繞去飯田橋。</p>
<ul>
<li><span class="time">16:00</span> teamLab 結束（豐洲）</li>
<li><span class="time">16:00–18:00</span> <b>待填</b>：豐洲千客萬来足湯、站內晚餐，或直接回上野</li>
<li><span class="time">18:00–21:00</span> <b>待填</b>：回上野 <span class="time">19–20 點</span> 燒肉（<a href="tokyo-2026-08-ueno-local-guide.html#yakiniku">上野手冊</a>）或八月慶典</li>
</ul>
</div>
</details>"""

DAY4_DINNER_BLOCK = """<p><span class="tag d">晚餐（16:00 後｜待排，建議豐洲或回上野）</span></p>
<p class="muted">無阿波舞，<b>不必去神樂坂</b>。以下依當日空檔安排擇一：</p>
<p><b>① 豐洲市場 千客萬来<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E8%B1%8A%E6%B4%B2%E5%B8%82%E5%A0%B4%20%E5%8D%83%E5%AE%A2%E4%B8%87%E6%9D%A5" target="_blank" rel="noopener" title="Google Maps：豊洲市場 千客万来">📍地圖</a></b> — 海鮮丼/小吃/足湯，¥1,500–3,000，<b>不訂位</b>，teamLab 出場後步行可達。</p>
<p><b>② 豐洲站 / 市場前站商場</b> — 定食、拉麵，¥800–1,500，<b>不訂位</b>。</p>
<p><b>③ 回上野後（~19:00）</b>：燒肉見 <a href="tokyo-2026-08-ueno-local-guide.html#yakiniku">上野手冊・燒肉</a>（<b>焼肉陽山道<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E7%87%92%E8%82%89%E9%99%BD%E5%B1%B1%E9%81%93%20%E4%B8%8A%E9%87%8E" target="_blank" rel="noopener" title="Google Maps：焼肉陽山道 上野">📍地圖</a></b>／<b>スタミナ苑</b>／<b>ライク</b>），或 Day1 備案。</p>"""

FREED_D5_SCHEDULE = """<p><span class="time">16:10–21:00</span> <b>🕳️ 待安排</b>（原花火野餐＋隅田川花火＋步行回上野；見 <a href="#free">空檔總表</a>）。</p>
<p class="muted">建議選項：登晴空塔展望台、Solamachi 購物＋晚餐、淺草仲見世夜景；若 <span class="time">19:00 前後</span> 回上野 → <a href="tokyo-2026-08-ueno-local-guide.html#yakiniku">燒肉／燒烤</a>（叙々苑、牛角 等）。</p>"""

FREED_D5_DETAILS = """<details open>
<summary>🕳️ 傍晚～夜晚空檔（16:10–21:00｜待一起安排）</summary>
<div class="card accbox">
<p>七月版此時段為<b>隅田川花火大會</b>（7/25 週六 19:00–20:30）。八月 8/16 無此場次，<b>約 5 小時</b>已留白——是全趟最大的可排程區塊。</p>
<ul>
<li><span class="time">16:10</span> 墨田水族館出館後起算</li>
<li><span class="time">16:30–18:00</span> <b>待填</b>：晴空塔 Tembo Deck、Solamachi 4F 購物等</li>
<li><span class="time">18:00–21:00</span> <b>待填</b>：晚餐＋夜景；回上野後見 <a href="tokyo-2026-08-ueno-local-guide.html#yakiniku">燒肉專章</a></li>
</ul>
</div>
</details>"""

BOOKING_ROW_YOSHINODO_JOJOEN_OLD = (
    '<tr><td><b>敘敘苑 / 燒肉陽山道 上野</b></td>'
    "<td>Day2 備案B 晚餐（犒賞）</td>"
    "<td>Hot Pepper / 一休</td>"
    "<td>18:00–20:00</td></tr>"
)
BOOKING_ROWS_YOSHINODO_JOJOEN = """<tr><td><b>焼肉陽山道 上野本店<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E7%87%92%E8%82%89%E9%99%BD%E5%B1%B1%E9%81%93%20%E4%B8%8A%E9%87%8E" target="_blank" rel="noopener" title="Google Maps：焼肉陽山道 上野">📍地圖</a></b></td><td>Day4 8/15(六) 晚餐（teamLab 後回上野）</td><td><a href="https://www.hotpepper.jp/">Hot Pepper</a> / 一休；出發前 <b>1 週</b></td><td><b>19:00</b>（山の日犒賞；滿席改ライク）</td></tr>
<tr><td><b>叙々苑 上野道玄坂店<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E5%8F%99%E5%8F%99%E8%8B%91%20%E4%B8%8A%E9%87%8E" target="_blank" rel="noopener" title="Google Maps：叙々苑 上野">📍地圖</a></b></td><td>Day5 8/16(日) 晚餐（晴空塔後回上野）</td><td>Hot Pepper / <a href="https://www.jojoen.co.jp/">官網</a>；<b>週日先訂</b></td><td><b>18:30–19:30</b>（慶祝晚餐）</td></tr>
<tr><td><b>焼肉陽山道 上野本店</b>（備案）</td><td>Day3 8/14 光雕秀日｜<b>18:00 早場</b>（秀前吃）</td><td>同上 Hot Pepper</td><td>18:00（秀後回上野改ライク）</td></tr>"""


def replace_dates(text: str) -> str:
    for old, new in DATE_MAP.items():
        text = text.replace(old, new)
    # weekday-only patterns like "7/24(五)" inside prose
    text = text.replace("7 月", "8 月")
    text = text.replace("7月", "8月")
    return text


def strip_festivals(text: str) -> str:
    # Header subtitle cleanup (gmap URLs are percent-encoded, not literal 隅田川)
    text = re.sub(
        r"、晚間空檔待排<a class=\"gmap\"[^>]*>📍地圖</a>",
        "、晚間空檔待排",
        text,
    )
    text = re.sub(
        r"含寶可夢光雕秀 ×2<a class=\"gmap\"[^>]*>📍地圖</a>",
        "含寶可夢光雕秀 ×2、晚間空檔待排",
        text,
    )

    # TOC link for free slots
    text = text.replace(
        '<a href="#d7">Day7</a>',
        '<a href="#d7">Day7</a>\n  <a href="#free">空檔</a>',
    )

    # Quick summary Day1
    text = text.replace(
        "Day1｜抵達東京・上野下午茶・夏日祭",
        "Day1｜抵達東京・上野下午茶・阿美橫町",
    )
    text = re.sub(
        r"<li>傍晚：.*?</li>",
        "<li><span class=\"time\">16:30 起</span> <b>阿美橫町逛街＋晚餐</b>（主線アメ横食堂）→ 續逛 → 回飯店前買宵夜／明日早餐。</li>",
        text,
        count=1,
        flags=re.DOTALL,
    )

    # Quick summary Day4
    text = re.sub(
        r"<summary>Day4｜葛西水族園.*?teamLab.*?神樂坂.*?</summary>\s*<ul>.*?</ul>",
        """<summary>Day4｜葛西水族園＋豐洲市場＋teamLab</summary>
<ul>
<li>上午：葛西臨海水族園（必看 10:45 企鵝餵食）→ 中午豐洲市場海鮮丼。</li>
<li><span class="time">14:00–16:00</span> teamLab Planets（<b>整趟只去一次</b>）。</li>
<li><span class="time">16:00–21:00</span> <b>待安排</b>（teamLab 後全傍晚留白，<b>不必去神樂坂</b>；見 <a href="#free">空檔</a>）。</li>
<li>帶小孩：午餐選管理設施棟定食最穩。</li>
</ul>""",
        text,
        count=1,
        flags=re.DOTALL,
    )

    # Quick summary Day5
    text = text.replace("＋隅田川花火", "＋傍晚空檔")
    text = re.sub(
        r"墨田水族館<a[^>]*>📍地圖</a><a class=\"gmap\"[^>]*隅田川[^>]*>📍地圖</a>",
        "墨田水族館",
        text,
    )
    text = re.sub(
        r"<li><span class=\"time\">16:10–17:30</span> 買好花火野餐.*?</li>\s*"
        r"<li><span class=\"time\">19:00–20:30</span> 花火大會.*?</li>\s*"
        r"<li>花火後：.*?。</li>",
        "<li><span class=\"time\">16:10–21:00</span> <b>待安排</b>（原花火時段，見 <a href=\"#free\">空檔</a>）。</li>",
        text,
        flags=re.DOTALL,
    )
    text = text.replace("7/25 週六：", "8/16 週日：")
    text = text.replace("8/16 週六：", "8/16 週日：")
    text = text.replace("花火週六", "週日")
    text = text.replace("（8/16 六）", "（8/16 日）")

    # Day6 quick: weekend -> weekday
    text = text.replace(
        "Day6｜品川 Aqua Park 雙秀＋週末寶可夢光雕秀",
        "Day6｜品川 Aqua Park 雙秀＋平日寶可夢光雕秀",
    )

    # Day1 section
    text = text.replace(
        "Day 1｜8/12(三)　抵達・上野下午茶・夏日祭典",
        "Day 1｜8/12(三)　抵達・上野下午茶・阿美橫町",
    )
    text = text.replace(
        "主題：輕鬆收心、在地祭典",
        "主題：輕鬆收心、阿美橫町初體驗",
    )
    text = text.replace(
        "主題：輕鬆收心、上野初探＋晚餐後在地生活小逛",
        "主題：輕鬆收心、阿美橫町初體驗",
    )
    text = text.replace(
        "主題：輕鬆收心、上野初探",
        "主題：輕鬆收心、阿美橫町初體驗",
    )
    text = re.sub(
        r"<p><span class=\"time\">16:30[^<]*</span>.*?</p>\s*"
        r"(?:<p><span class=\"time\">18:00[^<]*</span>.*?</p>\s*)?"
        r"(?:<p><span class=\"time\">18:45[^<]*</span>.*?</p>\s*)?"
        r"(?:<p><span class=\"time\">19:00[^<]*</span>.*?</p>\s*)?"
        r"(?:<p><span class=\"time\">19:30[^<]*</span>.*?</p>\s*)?"
        r"(?:<p><span class=\"time\">20:30[^<]*</span>.*?</p>\s*)?"
        r"<p><span class=\"time\">21:00</span> 步行回飯店。</p>",
        DAY1_SCHEDULE + "\n",
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<details>\s*<summary>🏪[^<]*</summary>.*?</details>",
        DAY1_AMEYOKO_DETAILS,
        text,
        count=1,
        flags=re.DOTALL,
    )
    if 'summary>🏪 阿美橫町・在地生活' not in text:
        text = text.replace(
            "</details>\n\n<details>\n<summary>🍽️ 三餐 ×3 備案</summary>",
            "</details>\n\n" + DAY1_AMEYOKO_DETAILS + "\n\n<details>\n<summary>🍽️ 三餐 ×3 備案</summary>",
            1,
        )
    text = re.sub(
        r"<p><span class=\"tag d\">晚餐（18:45）</span></p>\s*"
        r"<p><b>① 鳥貴族.*?</p>\s*"
        r"<p><b>② とんかつ 山家.*?</p>\s*"
        r"<p><b>③ 天丼てんや.*?</p>",
        DAY1_DINNER_BLOCK,
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<p><span class=\"tag d\">晚餐（18:00｜阿美橫町一帶，擇一）</span></p>\s*"
        r"<p class=\"muted\">主路線已排.*?</p>\s*"
        r"<p><b>① アメ横食堂.*?</p>\s*"
        r"<p><b>② 天丼てんや.*?</p>\s*"
        r"<p><b>③ とんかつ 山家.*?</p>\s*"
        r"<p><b>④ (?:肉の大山|焼肉ライク).*?</p>",
        DAY1_DINNER_BLOCK,
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = text.replace(
        "本日風格：<b>甜點下午茶 ＋ 居酒屋/炸物晚餐</b>（與其他天不重複）。",
        "本日風格：<b>甜點下午茶 ＋ 阿美橫町逛街晚餐</b>（與其他天不重複）。",
    )
    text = text.replace(
        "<br><span class=\"muted\">＋阿美橫町",
        "<br><span class=\"muted\">＋宵夜／明日早餐採買約 ¥500–1,000；阿美橫町",
    )
    text = text.replace("，夏祭當晚不想排隊時最穩。", "，不想排隊時最穩。")
    text = re.sub(
        r"<p><b>④ 屋台小吃</b>（上野夏祭）—.*?</p>\n",
        "",
        text,
        flags=re.DOTALL,
    )

    # Day4 section — teamLab 後留白，移除神樂坂專程
    text = re.sub(
        r"・神樂坂<a class=\"gmap\"[^>]*>📍地圖</a>",
        "",
        text,
    )
    text = re.sub(
        r"＋神樂坂<a class=\"gmap\"[^>]*>📍地圖</a>",
        "",
        text,
    )
    text = text.replace(
        "主題：海洋 + 頂級海鮮 + 沉浸藝術 + 神樂坂",
        "主題：海洋 + 頂級海鮮 + 沉浸藝術（傍晚空檔待排）",
    )
    text = re.sub(
        r"若 Day3 已去 teamLab<a class=\"gmap\"[^>]*>📍地圖</a>，今天就改下午直接神樂坂<a class=\"gmap\"[^>]*>📍地圖</a>或加排淺草<a class=\"gmap\"[^>]*>📍地圖</a>。",
        "若 Day3 已去 teamLab，今天就改下午加長豐洲千客萬来／站內休息，或提前回上野。",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"(teamLab<a class=\"gmap\"[^>]*>📍地圖</a>)阿波舞",
        r"\1",
        text,
    )
    text = text.replace(
        "主題：海洋 + 頂級海鮮 + 沉浸藝術 + 夏祭",
        "主題：海洋 + 頂級海鮮 + 沉浸藝術（傍晚空檔待排）",
    )
    text = re.sub(
        r'(<p><span class="time">14:00–16:00</span> <b>teamLab.*?涉水消暑。</p>\s*)'
        r'(?:<p[^>]*>.*?</p>\s*)+'
        r'(</div>\s*</details>)',
        lambda m: m.group(1) + FREED_D4_AFTER_TEAMLAB + "\n" + m.group(2),
        text,
        count=1,
        flags=re.DOTALL,
    )
    # 清除殘留的神樂坂專程（若替換漏網）
    text = re.sub(
        r'<p><span class="time">(?:16:30|17:30)</span> 神樂坂.*?</p>\s*',
        "",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r'<p><span class="time">19:00–21:00</span> <b>神樂坂.*?阿波舞大會</b>.*?</p>\s*',
        "",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<details open>\s*<summary>🎭 阿波舞觀賞攻略.*?</details>\s*",
        FREED_D4_DETAILS + "\n\n",
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<details open>\s*<summary>🕳️ 傍晚空檔（19:00–21:00｜待一起安排）</summary>.*?</details>\s*",
        FREED_D4_DETAILS + "\n\n",
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<p class=\"muted\">本日風格：<b>便利早餐 ＋ 豐洲海鮮丼午餐 ＋ 神樂坂.*?和食晚餐</b>.*?</p>",
        "<p class=\"muted\">本日風格：<b>便利早餐 ＋ 豐洲海鮮丼午餐 ＋ 傍晚空檔晚餐（待排）</b>（與其他天不重複）。</p>",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<p><span class=\"tag d\">晚餐（神樂坂.*?）</span></p>\s*"
        r"<p><b>① 神樂坂.*?不想等位時最快。</p>\n",
        DAY4_DINNER_BLOCK + "\n",
        text,
        flags=re.DOTALL,
    )

    # Day5 section
    text = text.replace("・🎆隅田川花火", "")
    text = re.sub(
        r"墨田水族館<a class=\"gmap\"[^>]*>📍地圖</a><a class=\"gmap\"[^>]*隅田川[^>]*>📍地圖</a>",
        "墨田水族館",
        text,
    )
    text = text.replace(
        "主題：室內冷氣避暑 + 日本最具代表性花火（19:00–20:30 確定）",
        "主題：室內冷氣避暑 + 晴空塔周邊（傍晚空檔待排）",
    )
    text = re.sub(
        r'<div class="warnbox">🔴 <b>全程最擠的一天</b>：花火.*?</div>\s*',
        '<div class="okbox">✅ <b>八月版</b>：已移除 7/25 隅田川花火，Day5 下午起有大段空檔可排新活動（見 <a href="#free">空檔總表</a>）。8/16 週日 Solamachi 仍可能人潮多，午餐建議 11:00 前取號。</div>\n',
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<p><span class=\"time\">16:10–17:30</span> 步行至隅田公園.*?。</p>\s*"
        r"<p><span class=\"time\">19:00–20:30</span> 🎆 隅田川花火.*?</p>\s*"
        r"<p><span class=\"time\">~20:40–21:20</span> 沿淺草.*?。</p>",
        FREED_D5_SCHEDULE,
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<details open>\s*<summary>🎆 花火觀賞攻略.*?</details>\s*",
        FREED_D5_DETAILS + "\n\n",
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = text.replace("花火日人潮爆，先買省排隊", "週日人潮多，先買省排隊")
    text = text.replace("（花火週六必守）", "（週日建議提早）")
    text = text.replace("花火週六 <b>11:00 前到取號</b>", "週日 <b>11:00 前到取號</b>")
    text = text.replace("花火日建議多吃一點。", "建議多吃一點。")
    text = text.replace("（週六最擠，午餐務必提早）。", "（週日人潮多，午餐務必提早）。")
    text = text.replace(
        "本日風格：<b>咖啡鬆餅早餐 ＋ 迴轉壽司午餐 ＋ 花火野餐晚餐</b>",
        "本日風格：<b>咖啡鬆餅早餐 ＋ 迴轉壽司午餐 ＋ 傍晚空檔晚餐（待排）</b>",
    )
    text = re.sub(
        r"<p><span class=\"tag d\">晚餐（花火野餐 17:00 前備好）</span></p>\s*"
        r'<p class="warnbox">🚫 <b>切勿在花火當晚訂餐廳</b>.*?</p>\s*'
        r"<p><b>① Solamachi.*?16:00 前買</b>，會場附近會被掃空。</p>",
        """<p><span class="tag d">晚餐（16:10 後｜待排）</span></p>
<p class="muted">原花火野餐時段已留白，可改 Solamachi 內餐廳、淺草小吃，或移動至其他八月活動地點。</p>
<p><b>① Solamachi 內餐廳</b>（トリトン二輪、利久、烏龍麵等）— ¥1,500–3,000，<b>現場排</b>。</p>
<p><b>② 淺草仲見世</b> — 人形燒、炸饅頭、天婦羅，¥800–1,500。</p>
<p><b>③ Solamachi B1 超市便當</b> — 帶回飯店或公園吃，¥500–1,500。</p>""",
        text,
        flags=re.DOTALL,
    )
    text = text.replace(
        "＋花火野餐 <span class=\"price\">¥2,000</span>",
        "＋晚餐 <span class=\"price\">¥2,500</span>",
    )

    # Day6: weekend -> weekday for projection mapping
    text = text.replace(
        "Day 6｜8/17(一)　品川海洋聲光 ＋ ⭐週末寶可夢光雕秀(+哥吉拉)",
        "Day 6｜8/17(一)　品川海洋聲光 ＋ ⭐平日寶可夢光雕秀",
    )
    text = text.replace(
        "主題：品川晨遊 ＋ Aqua Park 日間＋夜間雙秀 ＋ 週末光雕秀",
        "主題：品川晨遊 ＋ Aqua Park 日間＋夜間雙秀 ＋ 平日光雕秀",
    )
    text = text.replace(
        "<b>週末（含 Day6 週日）同場有超人氣哥吉拉光雕秀</b>，等於一次看兩種，週末去最賺。",
        "<b>8/17(一) 為平日</b>：哥吉拉等週末限定作品可能不播，出發前務必對官網 TIMETABLE。",
    )
    text = text.replace(
        "④ 🟡 寶可夢光雕秀 ×2（已幫你插入 Day3 平日 + Day6 週末）",
        "④ 🟡 寶可夢光雕秀 ×2（Day3 週五 + Day6 週一，皆平日場）",
    )

    text = re.sub(
        r"<tr><td><b>神樂坂<a class=\"gmap\"[^>]*>📍地圖</a> 鳥茶屋</b></td><td>Day4 晚餐</td>.*?</tr>\s*",
        "",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<li>Day4：上野→葛西臨海→豐洲→飯田橋（神樂坂<a class=\"gmap\"[^>]*>📍地圖</a>）→上野",
        "<li>Day4：上野→葛西臨海→豐洲→上野",
        text,
        flags=re.DOTALL,
    )
    text = text.replace("≈ <b>¥900–1,100</b>", "≈ <b>¥700–900</b>", 1)  # Day4 fare only first match risky
    text = re.sub(
        r"<li><b>Day4</b>：仲家.*?富士そば<a class=\"gmap\"[^>]*>📍地圖</a> 24h。</li>",
        "<li><b>Day4</b>：仲家海鮮丼、天房、八千代、管理設施棟定食（午餐）；晚餐見 Day4 待排空檔。</li>",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<li>☐ 邁泉青山本店 / 神樂坂<a class=\"gmap\"[^>]*>📍地圖</a> / 品川王子",
        "<li>☐ 邁泉青山本店 / 品川王子",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<li>☐ 確認 Day4 神樂坂<a class=\"gmap\"[^>]*>📍地圖</a>當年確切日期</li>",
        "<li>☐ 一起填寫 <a href=\"#free\">空檔</a>（Day4 teamLab後 / Day5 傍晚）</li>",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<li>☐ 一起填寫 <a href=\"#free\">晚間空檔</a>（Day1 / Day4 / Day5）</li>\s*",
        "",
        text,
    )
    text = text.replace(
        "<li>☐ 折疊傘+雨衣、水壺、野餐墊、購物袋</li>",
        "<li>☐ 折疊傘+雨衣、水壺、購物袋</li>",
    )
    text = re.sub(
        r"D4 葛西臨海水族園.*?teamLab<a class=\"gmap\"[^>]*>📍地圖</a> Planets→.*?（teamLab",
        "D4 葛西臨海水族園→豐洲市場午餐→teamLab Planets→（16:00後待排）（teamLab",
        text,
        flags=re.DOTALL,
    )
    text = text.replace(
        "Day6｜品川 Aqua Park 雙秀＋週末寶可夢光雕秀",
        "Day6｜品川 Aqua Park 雙秀＋平日寶可夢光雕秀",
    )
    text = re.sub(
        r"<li><b>Day4 / Day5 都用到 teamLab",
        "<li><b>Day4 teamLab 後 16:00–21:00 已留白</b>（不必去神樂坂）；若排八月慶典見 <a href=\"#free\">空檔</a>。</li>\n<li><b>Day4 / Day5 都用到 teamLab",
        text,
        count=1,
    )
    text = text.replace("D6（週末/週日）", "D6（週一）")
    text = text.replace("週末同場有哥吉拉", "8/17(一)為平日，哥吉拉等週末作品可能不播")
    text = text.replace(
        "<b>Day6 利久牛舌品川</b>：<b>10:30 到站排隊</b>，11:00 入座最理想；週日 12:00 後常等 30 分+。",
        "<b>Day6 利久牛舌品川</b>：<b>10:30 到站排隊</b>，11:00 入座最理想；週一 12:00 後仍可能排隊。",
    )
    text = text.replace(
        "本檔可用瀏覽器「列印 → 儲存為 PDF」帶著走（離線可看）。清新版：<code>tokyo-2026-guide-light.html</code>",
        "本檔可用瀏覽器「列印 → 儲存為 PDF」帶著走（離線可看）。八月版：<code>tokyo-2026-08-guide.html</code>｜七月版：<code>../20260721_Tokyo/tokyo-2026-guide.html</code>",
    )
    text = text.replace(
        "；<b>阿波舞祭當晚務必訂</b>",
        "",
    )
    text = text.replace("阿波舞祭當晚", "週末晚餐")
    text = text.replace("（祭典日爆滿）", "（週末建議訂）")
    text = re.sub(
        r"<p><b>④ 祭典屋台</b> —.*?</p>\n",
        "",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<li><b>祭典（上野夏祭.*?</li>\s*",
        "",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<li>三大夏祭（上野夏祭.*?</li>\s*",
        "",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<li><b>Day5 隅田川花火.*?</li>\s*",
        "<li><b>Day5 傍晚空檔（8/16 日）</b>：墨田水族館出館後約 16:10–21:00 待排，可參考 <a href=\"#free\">空檔總表</a> 與 <a href=\"tokyo-2026-08-festivals-research.html\">八月慶典調查</a>。</li>\n",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<tr><td>Day5 花火</td>.*?</tr>\s*",
        "<tr><td>Day5 傍晚空檔</td><td>改：晴空塔展望台、Solamachi 購物晚餐、淺草夜遊，或八月祭典／花火（見 <a href=\"tokyo-2026-08-festivals-research.html\">慶典調查</a>）</td></tr>\n",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"<li><b>隅田川花火.*?</li>\s*",
        "",
        text,
        flags=re.DOTALL,
    )
    text = text.replace("阿波舞祭（teamLab", "晚餐（teamLab")
    text = text.replace(
        "D5（週六）晴空塔",
        "D5（週日）晴空塔",
    )
    text = re.sub(
        r"→隅田川花火.*?步行回上野",
        "→（16:10 後傍晚空檔待排）",
        text,
        flags=re.DOTALL,
    )
    text = text.replace("8/13 週三平日", "8/13 週四平日")
    text = text.replace(
        "祭典屋台、阿美橫町",
        "路邊小攤、阿美橫町",
    )
    text = text.replace("祭典可帶/現場租<b>浴衣</b>（Day5 超應景）。", "")
    text = text.replace("野餐墊（Day5 花火/夏祭）、", "")
    text = text.replace(
        "<tr><td>Day1 上野公園/夏祭</td><td>改 PARCO_ya",
        "<tr><td>Day1 上野公園</td><td>改 PARCO_ya",
    )
    text = text.replace("、晚祭縮短", "")

    # Day7 lotus - still August has lotus
    text = text.replace("不忍池 7 月荷花盛開", "不忍池 8 月荷花")

    # AI prompt section at end
    text = re.sub(
        r"D1 上野：HARBS.*?$",
        "D1 上野：HARBS 下午茶→16:30起阿美橫町逛街→晚餐アメ横食堂→續逛→買宵夜早餐回飯店",
        text,
        count=1,
        flags=re.DOTALL | re.MULTILINE,
    )
    text = text.replace(
        "神樂坂阿波舞祭（teamLab",
        "神樂坂晚餐（teamLab",
    )

    # Insert free slots section before 省錢 section
    if 'id="free"' not in text:
        text = text.replace(
            "<!-- ============ 省錢 ============ -->",
            FREE_SLOTS_SECTION + "\n<!-- ============ 省錢 ============ -->",
        )

    # Final orphaned gmap cleanup (after all text substitutions)
    text = text.replace("雙秀＋週末寶可夢光雕秀", "雙秀＋平日寶可夢光雕秀")
    text = text.replace(
        "<li>☐ 一起填寫 <a href=\"#free\">晚間空檔</a>（Day1 / Day4 / Day5）</li>",
        "<li>☐ 一起填寫 <a href=\"#free\">空檔</a>（Day4 teamLab後 / Day5 傍晚）</li>",
    )
    text = re.sub(
        r"、隅田川花火<a class=\"gmap\"[^>]*>📍地圖</a>",
        "、晚間空檔待排",
        text,
    )
    text = re.sub(
        r"＋傍晚空檔<a class=\"gmap\"[^>]*>📍地圖</a>",
        "＋傍晚空檔",
        text,
    )
    text = text.replace(
        '  <a href="journey-maps.html">🗺️ 冒險地圖</a>',
        '  <a href="journey-maps.html">🗺️ 冒險地圖</a>\n  <a href="tokyo-2026-08-ueno-local-guide.html">🏮 上野手冊</a>',
    )
    if "上野・阿美橫町手冊" not in text:
        text = text.replace(
            '<div class="noprint accbox" style="margin-top:14px">\n  🗺️ <b>冒險地圖</b>：',
            '<div class="noprint accbox" style="margin-top:14px">\n  🏮 <b>上野在地生活</b>（連住 6 晚晚上不無聊）：<a href="tokyo-2026-08-ueno-local-guide.html"><b>上野・阿美橫町手冊</b></a>（吃逛買＋<a href="tokyo-2026-08-ueno-local-guide.html#electronics">家電電子</a>＋每店 📍地圖）<br>\n  🗺️ <b>冒險地圖</b>：',
            1,
        )
    text = text.replace(
        "（吃逛買＋每店 📍地圖）<br>\n  🗺️ <b>冒險地圖</b>：",
        "（吃逛買＋<a href=\"tokyo-2026-08-ueno-local-guide.html#electronics\">家電電子</a>＋每店 📍地圖）<br>\n  🗺️ <b>冒險地圖</b>：",
    )
    text = text.replace("・阿美橫町・阿美橫町", "・阿美橫町")

    # 訂位清單：陽山道 Day4、叙々苑 Day5（取代七月 Day2 合併列）
    text = text.replace(BOOKING_ROW_YOSHINODO_JOJOEN_OLD, BOOKING_ROWS_YOSHINODO_JOJOEN)
    text = text.replace(
        "<li>☐ 邁泉青山本店 / 品川王子 / 上野燒肉 訂位（依選擇）</li>",
        "<li>☐ <b>焼肉陽山道</b> Day4 <b>19:00</b>、<b>叙々苑</b> Day5 <b>19:00</b> 訂位（Hot Pepper；見 <a href=\"#book\">訂位清單</a>）</li>\n"
        "<li>☐ 邁泉青山本店 / 品川王子 訂位（依選擇）</li>",
    )
    text = text.replace(
        "<p class=\"muted\">敘敘苑 / 陽山道需<b>週日晚先訂</b>（¥3,000–5,000），光雕秀後時間偏晚。</p>",
        "<p class=\"muted\">光雕秀日（Day3/Day6）回上野常 21:30+，<b>陽山道／叙々苑</b>多已 L.O. → 改 <b>焼肉ライク</b> 或便利店；主線訂位見 <a href=\"#book\">Day4 陽山道 19:00</a>。</p>",
    )
    text = text.replace(
        "<li><b>Day4</b>：仲家海鮮丼、天房、八千代、管理設施棟定食（午餐）；晚餐見 Day4 待排空檔。</li>",
        "<li><b>Day4</b>：仲家海鮮丼、天房、八千代、管理設施棟定食（午餐）；晚餐建議訂 <a href=\"#book\">焼肉陽山道 19:00</a>（或見 <a href=\"#free\">空檔</a>）。</li>",
    )
    text = text.replace(
        "<li><b>Day5</b>：Doutor、コメダ、Solamachi<a class=\"gmap\" href=\"https://www.google.com/maps/search/?api=1&query=%E6%9D%B1%E4%BA%AC%E3%82%BD%E3%83%A9%E3%83%9E%E3%83%81\" target=\"_blank\" rel=\"noopener\" title=\"Google Maps：東京ソラマチ\">📍地圖</a> 美食街、超市野餐、屋台。</li>",
        "<li><b>Day5</b>：Doutor、コメダ、Solamachi<a class=\"gmap\" href=\"https://www.google.com/maps/search/?api=1&query=%E6%9D%B1%E4%BA%AC%E3%82%BD%E3%83%A9%E3%83%9E%E3%83%81\" target=\"_blank\" rel=\"noopener\" title=\"Google Maps：東京ソラマチ\">📍地圖</a> 美食街、超市野餐、屋台；晚餐建議訂 <a href=\"#book\">叙々苑 19:00</a>。</li>",
    )

    # 秋葉原：親子／國高生路線（避開女僕咖啡、MEN'S館、成人樓層）
    text = text.replace(
        "秋葉原本館 ＋ MEN'S館</td><td>⭐ 半日核心。本館＝中古漫畫・同人誌・小說；MEN'S館＝男性向 ACG／遊戲周邊。各逛 45–60 分。",
        "秋葉原本館のみ</td><td>⭐ 半日核心。<b>只逛本館</b>（少年漫・一般向周邊）。<b>不進 MEN'S館</b>（成人向）与同人社刊 R18 區。建議 60–90 分。",
    )
    text = re.sub(
        r"<li><b>K-BOOKS<a class=\"gmap\"[^>]*>📍地圖</a> 秋葉原本館</b> → 步行 2 分 → "
        r"<b>K-BOOKS<a class=\"gmap\"[^>]*>📍地圖</a> MEN'S館</b></li>",
        '<li><b>K-BOOKS<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=K-BOOKS%20%E7%A7%8B%E8%91%89%E5%8E%9F%E6%9C%AC%E9%A4%A8" target="_blank" rel="noopener" title="Google Maps：K-BOOKS 秋葉原本館">📍地圖</a> 秋葉原本館</b>（<b>只逛本館</b>，略過 MEN\'S館）</li>',
        text,
    )
    text = text.replace(
        "Radio Kaikan 1–3F</td><td>扭蛋、模型、卡牌、小周邊；小孩通常最開心。步行 3–5 分。多數店 <b>11:00–20:00</b>，優先逛。",
        "Radio Kaikan <b>1–3F のみ</b></td><td>扭蛋、模型、卡牌、小周邊。<b>勿上 4F 以上</b>（部分店成人向）。步行 3–5 分。多數店 <b>11:00–20:00</b>，優先逛。",
    )
    text = text.replace(
        "【アニメイト or まんだらけ】</b><br>快閃二選一</td><td><b>アニメイト秋葉原",
        "【アニメイト】</b><br>快閃</td><td><b>アニメイト秋葉原",
    )
    text = text.replace(
        "（旗艦，新番周邊）或 <b>まんだらけ 複合店<a class=\"gmap\" href=\"https://www.google.com/maps/search/?api=1&query=%E3%81%BE%E3%82%93%E3%81%A0%E3%82%89%E3%81%91%20%E7%A7%8B%E8%91%89%E5%8E%9F\" target=\"_blank\" rel=\"noopener\" title=\"Google Maps：まんだらけ 秋葉原\">📍地圖</a></b>（中古收藏）。時間不夠就跳過，回上野晚餐。",
        "（旗艦，新番周邊；<b>親子／國高生首選</b>）。時間不夠就跳過，回上野晚餐。",
    )
    text = re.sub(
        r"→ アニメイト or まんだらけ）",
        "→ アニメイト）",
        text,
    )
    text = re.sub(
        r"<li>→ 步行 3 分 → <b>アニメイト秋葉原<a class=\"gmap\"[^>]*>📍地圖</a></b> <b>或</b> "
        r"<b>まんだらけ 複合店<a class=\"gmap\"[^>]*>📍地圖</a></b>（二選一快閃）</li>",
        '<li>→ 步行 3 分 → <b>アニメイト秋葉原<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E3%82%A2%E3%83%8B%E3%83%A1%E3%82%A4%E3%83%88%E7%A7%8B%E8%91%89%E5%8E%9F" target="_blank" rel="noopener" title="Google Maps：アニメイト秋葉原">📍地圖</a></b>（旗艦快閃）</li>',
        text,
    )
    text = text.replace(
        '<p class="muted"><b>可跳過</b>：女僕咖啡（@home cafe<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%40home%20cafe%20%E7%A7%8B%E8%91%89%E5%8E%9F" target="_blank" rel="noopener" title="Google Maps：@home cafe 秋葉原">📍地圖</a> 等）親子不一定適合。WEGO 服飾改 Day3 原宿<a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E5%8E%9F%E5%AE%BF%E9%A7%85" target="_blank" rel="noopener" title="Google Maps：原宿駅">📍地圖</a>。</p>',
        '<p class="warnbox"><b>親子／國高生請避開</b>：女僕／執事咖啡、K-BOOKS <b>MEN\'S館</b>、同人社刊 R18 區、まんだらけ成人樓、電氣街拉客店。主線：<b>ラジオ会館 1–3F</b>・<b>アニメイト</b>・<b>ガシャポン</b>・<b>ヨドバシ玩具區</b>。更多見 <a href="tokyo-2026-08-ueno-local-guide.html#teen">上野手冊・國高生逛街</a>。WEGO 改 Day3 <a class="gmap" href="https://www.google.com/maps/search/?api=1&query=%E5%8E%9F%E5%AE%BF%E9%A7%85" target="_blank" rel="noopener" title="Google Maps：原宿駅">📍地圖</a>原宿。</p>',
    )

    text = text.replace(
        "<li><b>唐吉訶德/Bic/Yodobashi 出示護照免稅 8–10%</b> + APP/官網優惠券再折。藥妝店（松本清等）滿額免稅 + 折價券。</li>",
        "<li><b>唐吉訶德/Bic/Yodobashi 出示護照免稅 8–10%</b> + APP/官網優惠券再折。家電店・<a href=\"tokyo-2026-08-ueno-local-guide.html#electronics-compare\">比價工具</a>／<a href=\"tokyo-2026-08-ueno-local-guide.html#electronics-coupon\">折價券</a>見 <a href=\"tokyo-2026-08-ueno-local-guide.html#electronics\">上野手冊・家電電子</a>（⭐ 上野站前ヨドバシ）。藥妝店（松本清等）滿額免稅 + 折價券。</li>",
    )
    text = text.replace(
        "<b>合計約 10 小時待排空檔</b>（Day4 5hr＋Day5 5hr）。Day1 傍晚已排<b>阿美橫町逛街＋晚餐＋採買</b>。國高生逛街（避開女僕／成人向）見 <a href=\"tokyo-2026-08-ueno-local-guide.html#teen\">上野手冊</a>。",
        "<b>合計約 10 小時待排空檔</b>（Day4 5hr＋Day5 5hr）。Day1 傍晚已排<b>阿美橫町逛街＋晚餐＋採買</b>。國高生逛街見 <a href=\"tokyo-2026-08-ueno-local-guide.html#teen\">上野手冊</a>；家電／Apple 見 <a href=\"tokyo-2026-08-ueno-local-guide.html#electronics\">家電電子專章</a>。",
    )

    return text


def main() -> None:
    text = SRC.read_text(encoding="utf-8")
    text = replace_dates(text)
    text = strip_festivals(text)
    for old_title in (
        "<title>東京 7 日親子行 完整指南 2026/8/12–8/18</title>",
        "<title>東京 7 日親子行 完整指南 2026/8/12–8/18（清新版）</title>",
    ):
        text = text.replace(
            old_title,
            "<title>東京 8/12–8/18 親子行指南（八月版）</title>",
        )
    OUT.write_text(text, encoding="utf-8")
    if OLD_OUT.exists() and OLD_OUT != OUT:
        OLD_OUT.unlink()
    print(f"Wrote {OUT} ({len(text):,} chars)")


if __name__ == "__main__":
    main()
