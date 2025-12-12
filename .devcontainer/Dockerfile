FROM mcr.microsoft.com/vscode/devcontainers/base:ubuntu-24.04

# ============================================================================
# Stage 1: Base packages (cached separately)
# ============================================================================
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ca-certificates curl wget git build-essential \
    bash-completion unzip zip jq locales gdb \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# Stage 2: Locale and timezone configuration
# ============================================================================
RUN sed -i 's/# *ja_JP.UTF-8/ja_JP.UTF-8/' /etc/locale.gen && locale-gen
ENV LANG=ja_JP.UTF-8 LANGUAGE=ja_JP:ja LC_ALL=ja_JP.UTF-8
RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
    && echo "Asia/Tokyo" > /etc/timezone
ENV TZ=Asia/Tokyo

# ============================================================================
# Stage 3: vscode user home setup
# ============================================================================
RUN mkdir -p /home/vscode/.local/bin \
    /home/vscode/.local/pipx \
    /home/vscode/.local/share/man \
 && chown -R vscode:vscode /home/vscode/.local

# ============================================================================
# Stage 4: Environment variables
# ============================================================================
USER vscode

ENV PIPX_HOME=/home/vscode/.local/pipx
ENV PIPX_BIN_DIR=/home/vscode/.local/bin
ENV PATH=/opt/atcoder/gcc/bin:/workspaces/atcoder:${PIPX_BIN_DIR}:${PATH}
ENV LD_LIBRARY_PATH=/opt/atcoder/gcc/lib64:/opt/atcoder/gcc/lib:${LD_LIBRARY_PATH:-}
