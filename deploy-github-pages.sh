#!/bin/bash
# Build Tokyo trip site into docs/Japan/20260721_Tokyo/ and prepare git push
set -euo pipefail
cd "$(dirname "$0")"

python3 Japan/20260721_Tokyo/build-site.py

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  git init
  git branch -M main
fi

git add docs/ Japan/20260721_Tokyo/ README.md .gitignore deploy-github-pages.sh
git status

echo ""
echo "=== 接下來 ==="
echo "1. 到 https://github.com/new 建立 repo：travel-log"
echo "2. git remote add origin git@github.com-personal:你的帳號/travel-log.git"
echo "3. git commit -m \"Add Japan/20260721_Tokyo trip guide\""
echo "4. git push -u origin main"
echo "5. Settings → Pages → Branch: main / Folder: /docs"
echo "6. 東京行程網址："
echo "   https://你的帳號.github.io/travel-log/Japan/20260721_Tokyo/"
