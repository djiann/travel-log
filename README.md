# travel-log

個人走過的旅遊地點與行程指南。

## 目錄

```
travel-log/
├── README.md
├── docs/                          ← GitHub Pages（Settings → /docs）
│   ├── index.html                 ← 旅程總索引
│   └── Japan/
│       └── 20260721_Tokyo/        ← 東京 2026 網站
└── Japan/
    └── 20260721_Tokyo/            ← 東京行程原始檔與建置腳本
        ├── tokyo-2026-guide-light.html   ← 唯一編輯來源
        ├── build-guides.py
        ├── build-site.py
        └── assets/
```

## 網址（GitHub Pages）

Repo 名稱設為 `travel-log` 時：

| 頁面 | URL |
|------|-----|
| 總索引 | `https://你的帳號.github.io/travel-log/` |
| 東京行程 | `https://你的帳號.github.io/travel-log/Japan/20260721_Tokyo/` |

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
