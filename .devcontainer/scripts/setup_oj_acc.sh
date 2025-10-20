#!/usr/bin/env bash
set -euo pipefail

# 実行ユーザー確認
if [ "$(id -u)" -eq 0 ]; then
    echo "This script should not be run as root. Please run as a non-root user."
    exit 1
fi

python3 -m pip install --user --upgrade pip pipx
python3 -m pipx ensurepath

# online-judge-tools のインストール
pipx install online-judge-tools --include-deps
pipx inject online-judge-tools setuptools

# AtCoder CLI のインストール
if ! command -v npm >/dev/null 2>&1; then
    echo "[oj-acc] npm is not installed. Please install Node.js and npm first."
    exit 1
fi
npm install -g atcoder-cli

echo "[oj] $(oj --version) installed"
echo "[acc] $(acc --version) installed"