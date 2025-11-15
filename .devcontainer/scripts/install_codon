#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -eq 0 ]; then
    echo "[codon] Please run this script as a non-root user."
    exit 1
fi

CODON_VERSION="${CODON_VERSION:-0.19.3}"
CODON_HOME="${CODON_HOME:-$HOME/.local/share/codon}"
PROFILE_FILE="${PROFILE_FILE:-$HOME/.bashrc}"
LOCAL_BIN="${LOCAL_BIN:-$HOME/.local/bin}"
CODON_VARIANT="${CODON_VARIANT:-auto}"

CODON_BIN="${CODON_HOME}/bin/codon"
INSTALLED_VERSION=""
if [ -x "${CODON_BIN}" ]; then
    INSTALLED_VERSION="$("${CODON_BIN}" --version 2>/dev/null | awk '{print $2}' | head -n1 || true)"
fi

if [ "${INSTALLED_VERSION}" = "${CODON_VERSION}" ]; then
    echo "[codon] Codon ${CODON_VERSION} already installed at ${CODON_HOME}."
else
    OS_NAME="$(uname -s)"
    case "${OS_NAME}" in
        Linux) OS="linux" ;;
        Darwin) OS="darwin" ;;
        *)
            echo "[codon] Unsupported operating system: ${OS_NAME}"
            exit 1
            ;;
    esac

    ARCH_RAW="$(uname -m)"
    case "${OS}:${ARCH_RAW}" in
        linux:x86_64|linux:amd64)
            ARCH="x86_64"
            ;;
        linux:aarch64|linux:arm64)
            ARCH="aarch64"
            ;;
        darwin:x86_64|darwin:amd64)
            ARCH="x86_64"
            ;;
        darwin:arm64)
            ARCH="arm64"
            ;;
        *)
            echo "[codon] Unsupported architecture: ${ARCH_RAW}"
            exit 1
            ;;
    esac

    declare -a TAR_CANDIDATES=()
    if [ "${OS}" = "linux" ]; then
        case "${CODON_VARIANT}" in
            auto)
                TAR_CANDIDATES=("codon-linux-${ARCH}.tar.gz" "codon-manylinux2014-${ARCH}.tar.gz")
                ;;
            linux|manylinux2014)
                TAR_CANDIDATES=("codon-${CODON_VARIANT}-${ARCH}.tar.gz")
                ;;
            *)
                echo "[codon] Unsupported CODON_VARIANT: ${CODON_VARIANT}"
                exit 1
                ;;
        esac
    else
        TAR_CANDIDATES=("codon-${OS}-${ARCH}.tar.gz")
    fi

    if [ "${#TAR_CANDIDATES[@]}" -eq 0 ]; then
        echo "[codon] No download candidates determined for ${OS}/${ARCH_RAW}"
        exit 1
    fi

    TMP_DIR="$(mktemp -d)"
    trap 'rm -rf "${TMP_DIR}"' EXIT

    DOWNLOAD_BASE="https://github.com/exaloop/codon/releases/download/v${CODON_VERSION}"
    ARCHIVE_PATH="${TMP_DIR}/codon.tar.gz"
    DOWNLOAD_SUCCESS=false
    for TAR_NAME in "${TAR_CANDIDATES[@]}"; do
        URL="${DOWNLOAD_BASE}/${TAR_NAME}"
        echo "[codon] Downloading ${URL}"
        if curl -fsSL "${URL}" -o "${ARCHIVE_PATH}"; then
            DOWNLOAD_SUCCESS=true
            break
        else
            echo "[codon] Download failed for ${TAR_NAME}, trying next candidate..."
        fi
    done

    if [ "${DOWNLOAD_SUCCESS}" = false ]; then
        echo "[codon] Failed to download Codon ${CODON_VERSION} for ${OS_NAME}/${ARCH_RAW}"
        exit 1
    fi

    if [ -d "${CODON_HOME}" ]; then
        if [ -z "${CODON_HOME}" ] || [ "${CODON_HOME}" = "/" ]; then
            echo "[codon] Refusing to remove invalid CODON_HOME: ${CODON_HOME}"
            exit 1
        fi
        rm -rf "${CODON_HOME}"
    fi
    mkdir -p "${CODON_HOME}"
    tar -xzf "${ARCHIVE_PATH}" -C "${CODON_HOME}" --strip-components=1

    CODON_BIN="${CODON_HOME}/bin/codon"
fi

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

remove_line_containing() {
    local needle="$1"
    local file="$2"
    if [ -f "${file}" ]; then
        local tmp_file
        tmp_file="${file}.tmp.$$"
        grep -Fv "${needle}" "${file}" > "${tmp_file}" || true
        mv "${tmp_file}" "${file}"
    fi
}

remove_line_containing ".codon/bin" "${PROFILE_FILE}"
remove_line_containing "CODON_HOME" "${PROFILE_FILE}"
ensure_line "export CODON_HOME=\"${CODON_HOME}\"" "${PROFILE_FILE}"
ensure_line 'export PATH="$CODON_HOME/bin:$PATH"' "${PROFILE_FILE}"

mkdir -p "${LOCAL_BIN}"
if [ -d "${CODON_HOME}/bin" ]; then
    for binary in "${CODON_HOME}"/bin/*; do
        if [ -f "${binary}" ] && [ -x "${binary}" ]; then
            ln -sf "${binary}" "${LOCAL_BIN}/$(basename "${binary}")"
        fi
    done
fi

if [ -x "${CODON_BIN}" ]; then
    echo "[codon] Installed: $("${CODON_BIN}" --version)"
else
    echo "[codon] Installation completed but codon executable was not found at ${CODON_BIN}"
    exit 1
fi
