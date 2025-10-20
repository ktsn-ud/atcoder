#!/usr/bin/env bash
set -euo pipefail

# 実行ユーザー確認
if [ "$(id -u)" -eq 0 ]; then
    echo "This script should not be run as root. Please run as a non-root user."
    exit 1
fi

CODON_VERSION="${CODON_VERSION:-0.19.3}"
INSTALL_DIR="$HOME/.codon"

echo "[codon] Installing version ${CODON_VERSION}..."

# 既存インストールがある場合はスキップ
if command -v codon >/dev/null 2>&1; then
    echo "[codon] Codon is already installed. Skipping installation. version: $(codon --version)"
    exit 0
fi

# インストール
mkdir -p "$INSTALL_DIR"
curl -L "https://github.com/exaloop/codon/releases/download/v${CODON_VERSION}/codon-linux-aarch64.tar.gz" \
    -o /tmp/codon.tar.gz
tar -xzf /tmp/codon.tar.gz -C "$INSTALL_DIR" --strip-components=1
rm /tmp/codon.tar.gz

# パスを通す
echo 'export PATH="$HOME/.codon/bin:$PATH"' >> "$HOME/.bashrc"
source "$HOME/.bashrc"

echo "[codon] Installation completed. version: $(codon --version)"
