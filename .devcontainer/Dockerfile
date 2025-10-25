FROM mcr.microsoft.com/vscode/devcontainers/base:ubuntu-24.04

# 基本パッケージ
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ca-certificates curl wget git build-essential \
    bash-completion unzip zip jq locales \
    && rm -rf /var/lib/apt/lists/*

# ロケール & タイムゾーン
RUN sed -i 's/# *ja_JP.UTF-8/ja_JP.UTF-8/' /etc/locale.gen && locale-gen
ENV LANG=ja_JP.UTF-8 LANGUAGE=ja_JP:ja LC_ALL=ja_JP.UTF-8
RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
    && echo "Asia/Tokyo" > /etc/timezone
ENV TZ=Asia/Tokyo

# vscode ユーザーのホーム準備
RUN mkdir -p /home/vscode/.local/bin \
    /home/vscode/.local/pipx \
    /home/vscode/.local/share/man \
    /home/vscode/.local/share/online-judge-tools \
 && chown -R vscode:vscode /home/vscode/.local

USER vscode

# pipx 用の環境変数と PATH
ENV PIPX_HOME=/home/vscode/.local/pipx
ENV PIPX_BIN_DIR=/home/vscode/.local/bin
ENV PATH=${PIPX_BIN_DIR}:/home/vscode/.codon/bin:${PATH}
