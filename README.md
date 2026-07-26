# travel-log

個人走過的旅遊地點與行程指南。

## 目錄

```
travel-log/
├── README.md
├── docs/                          ← GitHub Pages（Settings → /docs）
│   ├── index.html                 ← 旅程總索引
│   └── Japan/
│       ├── 20260721_Tokyo/        ← 東京 2026/7 網站
│       └── 20260812_Tokyo/        ← 東京 2026/8 + next-trip 網站
└── Japan/
    ├── 20260721_Tokyo/            ← 七月行程原始檔
    └── 20260812_Tokyo/            ← 八月行程 / next-trip 原始檔
```

## 網址（GitHub Pages）

帳號 `djiann`、Repo `travel-log`：

| 頁面 | URL |
|------|-----|
| 總索引 | `https://djiann.github.io/travel-log/` |
| 東京 7 月 | `https://djiann.github.io/travel-log/Japan/20260721_Tokyo/` |
| 東京 8 月索引 | `https://djiann.github.io/travel-log/Japan/20260812_Tokyo/` |
| 八月完整指南 | `https://djiann.github.io/travel-log/Japan/20260812_Tokyo/tokyo-2026-08-guide.html` |
| 下次深度行程 | `https://djiann.github.io/travel-log/Japan/20260812_Tokyo/tokyo-next-trip-guide-detailed.html` |

## 更新東京行程

```bash
cd Japan/20260721_Tokyo
# 只改 tokyo-2026-guide-light.html
python3 build-guides.py
python3 build-site.py

cd ../..
git add .
git commit -m "更新 Tokyo 2026 行程"
git push
```

## 新增另一趟旅程

1. 複製 `Japan/20260721_Tokyo/` 為新資料夾（例：`Japan/20251201_Osaka`）
2. 修改該夾內 `build-site.py` 的 `TRIP_SLUG`
3. 更新 `docs/index.html`（`build-site.py` 的 `write_repo_index()`）加入連結
