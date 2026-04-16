#!/usr/bin/env bash
# install-conftest.sh — Install Conftest CLI for OPA/Rego policy testing
#
# Usage:  ./infrastructure/scripts/install-conftest.sh [version]
# Default version: 0.56.0
#
# Installs to /usr/local/bin/conftest (requires sudo) or to ~/.local/bin
# if NO_SUDO=1 is set.

set -euo pipefail

VERSION="${1:-0.56.0}"
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"

case "$ARCH" in
  x86_64)  ARCH="x86_64" ;;
  arm64|aarch64) ARCH="arm64" ;;
  *) echo "Unsupported arch: $ARCH" >&2; exit 1 ;;
esac

case "$OS" in
  linux)  PKG="conftest_${VERSION}_Linux_${ARCH}.tar.gz" ;;
  darwin) PKG="conftest_${VERSION}_Darwin_${ARCH}.tar.gz" ;;
  *) echo "Unsupported OS: $OS" >&2; exit 1 ;;
esac

URL="https://github.com/open-policy-agent/conftest/releases/download/v${VERSION}/${PKG}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "Downloading $URL ..."
curl -sSL -o "$TMP/$PKG" "$URL"

echo "Extracting ..."
tar -xzf "$TMP/$PKG" -C "$TMP"

if [ "${NO_SUDO:-0}" = "1" ]; then
  DEST="$HOME/.local/bin"
  mkdir -p "$DEST"
  mv "$TMP/conftest" "$DEST/conftest"
  chmod +x "$DEST/conftest"
  echo "Installed to $DEST/conftest"
  echo "Make sure $DEST is in your PATH."
else
  sudo mv "$TMP/conftest" /usr/local/bin/conftest
  sudo chmod +x /usr/local/bin/conftest
  echo "Installed to /usr/local/bin/conftest"
fi

conftest --version
