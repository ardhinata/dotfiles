#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_DIR="${SCRIPT_DIR}/chezmoi-docs"
SPRIG_DEST_DIR="${SCRIPT_DIR}/sprig-docs"
SPRIG_REPO_URL="https://github.com/Masterminds/sprig.git"
SPRIG_BRANCH="master"

cleanup() {
  if [[ -n "${TMPDIR:-}" ]] && [[ -d "${TMPDIR}" ]]; then
    rm -rf "${TMPDIR}"
  fi
  if [[ -n "${SPRIG_CLONE_DIR:-}" ]] && [[ -d "${SPRIG_CLONE_DIR}" ]]; then
    rm -rf "${SPRIG_CLONE_DIR}"
  fi
}
trap cleanup EXIT INT TERM

err() {
  echo "[ERROR]" "$@" >&2
  exit 1
}

info() {
  echo "[INFO]" "$@"
}

# --- Chezmoi Docs ---

info "Detecting Chezmoi version..."

if ! command -v chezmoi &>/dev/null; then
  err "chezmoi is not found in PATH. Please install chezmoi first."
fi

VERSION="$(chezmoi --version 2>/dev/null | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+' | head -1)"

if [[ -z "${VERSION}" ]]; then
  err "Failed to parse chezmoi version from 'chezmoi --version' output."
fi

info "Detected chezmoi version: ${VERSION}"

ARCHIVE_URL="https://github.com/twpayne/chezmoi/archive/refs/tags/v${VERSION}.tar.gz"

TMPDIR="$(mktemp -d)"
info "Created temporary directory: ${TMPDIR}"

ARCHIVE_PATH="${TMPDIR}/chezmoi-${VERSION}.tar.gz"

info "Downloading archive from ${ARCHIVE_URL}..."

if command -v curl &>/dev/null; then
  curl -fsSL --retry 3 --retry-delay 5 -o "${ARCHIVE_PATH}" "${ARCHIVE_URL}" || err "Failed to download archive with curl."
elif command -v wget &>/dev/null; then
  wget -q --tries=3 --waitretry=5 -O "${ARCHIVE_PATH}" "${ARCHIVE_URL}" || err "Failed to download archive with wget."
else
  err "Neither curl nor wget is available. Please install one of them."
fi

info "Extracting archive..."
mkdir -p "${TMPDIR}/extracted"
tar -xzf "${ARCHIVE_PATH}" -C "${TMPDIR}/extracted" || err "Failed to extract archive."

EXTRACTED_DIR="${TMPDIR}/extracted/chezmoi-${VERSION}"
if [[ ! -d "${EXTRACTED_DIR}" ]]; then
  err "Extracted directory not found. Expected: ${EXTRACTED_DIR}"
fi

SOURCE_DOCS="${EXTRACTED_DIR}/assets/chezmoi.io"
if [[ ! -d "${SOURCE_DOCS}" ]]; then
  err "assets/chezmoi.io directory not found in the extracted archive."
fi

info "Copying docs to ${DEST_DIR}..."
rm -rf "${DEST_DIR}"
cp -r "${SOURCE_DOCS}" "${DEST_DIR}" || err "Failed to copy chezmoi docs."

info "Successfully downloaded chezmoi docs (v${VERSION}) to ${DEST_DIR}"

# --- Sprig Docs ---

info "Cloning sprig repository (${SPRIG_BRANCH} branch)..."

if ! command -v git &>/dev/null; then
  err "git is not found in PATH. Cannot clone sprig repository."
fi

SPRIG_CLONE_DIR="$(mktemp -d)"
info "Cloning into temporary directory: ${SPRIG_CLONE_DIR}"

git clone --depth 1 --branch "${SPRIG_BRANCH}" "${SPRIG_REPO_URL}" "${SPRIG_CLONE_DIR}" || err "Failed to clone sprig repository."

SPRIG_SOURCE_DOCS="${SPRIG_CLONE_DIR}/docs"
if [[ ! -d "${SPRIG_SOURCE_DOCS}" ]]; then
  err "docs directory not found in the sprig repository clone."
fi

info "Copying sprig docs to ${SPRIG_DEST_DIR}..."
rm -rf "${SPRIG_DEST_DIR}"
cp -r "${SPRIG_SOURCE_DOCS}" "${SPRIG_DEST_DIR}" || err "Failed to copy sprig docs."

info "Successfully cloned sprig docs (${SPRIG_BRANCH} branch) to ${SPRIG_DEST_DIR}"

info "All documentation fetched successfully."
