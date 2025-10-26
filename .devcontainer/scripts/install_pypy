#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -eq 0 ]; then
    echo "[pypy] Please run this script as a non-root user."
    exit 1
fi

PYPY_VERSION="${PYPY_VERSION:-7.3.16}"
INSTALL_DIR="$HOME/.local/pypy3"
PROFILE_FILE="${PROFILE_FILE:-$HOME/.bashrc}"

ALREADY_INSTALLED=false
if [ -x "${INSTALL_DIR}/bin/pypy3" ]; then
    echo "[pypy] PyPy already installed: $("${INSTALL_DIR}/bin/pypy3" --version)"
    ALREADY_INSTALLED=true
fi

ARCH="$(uname -m)"
case "${ARCH}" in
    x86_64|amd64)
        TARBALL="pypy3.10-v${PYPY_VERSION}-linux64.tar.bz2"
        ;;
    aarch64|arm64)
        TARBALL="pypy3.10-v${PYPY_VERSION}-aarch64.tar.bz2"
        ;;
    *)
        echo "[pypy] Unsupported architecture: ${ARCH}"
        exit 1
        ;;
esac

if [ "${ALREADY_INSTALLED}" = false ]; then
    TMP_DIR="$(mktemp -d)"
    trap 'rm -rf "${TMP_DIR}"' EXIT

    URL="https://downloads.python.org/pypy/${TARBALL}"
    echo "[pypy] Downloading ${URL}"
    curl -fsSL "${URL}" -o "${TMP_DIR}/pypy.tar.bz2"

    mkdir -p "${INSTALL_DIR}"
    tar -xjf "${TMP_DIR}/pypy.tar.bz2" -C "${INSTALL_DIR}" --strip-components=1
fi

"${INSTALL_DIR}/bin/pypy3" -m ensurepip
"${INSTALL_DIR}/bin/pypy3" -m pip install --upgrade pip setuptools wheel

cleanup_old_path_export() {
    local file="$1"
    if [ -f "${file}" ]; then
        sed -i '/\.local\/pypy3\/bin/d' "${file}"
    fi
}

ensure_line() {
    local line="$1"
    local file="$2"
    if [ ! -f "${file}" ]; then
        touch "${file}"
    fi
    if ! grep -Fxq "${line}" "${file}"; then
        echo "${line}" >> "${file}"
    fi
}

cleanup_old_path_export "${PROFILE_FILE}"
ensure_line "export PYPY_HOME=\"${INSTALL_DIR}\"" "${PROFILE_FILE}"

LOCAL_BIN="$HOME/.local/bin"
mkdir -p "${LOCAL_BIN}"
ln -sf "${INSTALL_DIR}/bin/pypy3" "${LOCAL_BIN}/pypy3"
ln -sf "${INSTALL_DIR}/bin/pypy3" "${LOCAL_BIN}/pypy"
if [ -x "${INSTALL_DIR}/bin/pip3" ]; then
    ln -sf "${INSTALL_DIR}/bin/pip3" "${LOCAL_BIN}/pypy3-pip"
fi

echo "[pypy] Installed: $("${INSTALL_DIR}/bin/pypy3" --version)"
