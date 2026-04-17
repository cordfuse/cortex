#!/bin/bash
set -e

VERSION=${1:-1.0.0}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
DIST_DIR="$SCRIPT_DIR/dist"
PKG_DIR="$SCRIPT_DIR/deb/cortex-setup_${VERSION}_amd64"

rm -rf "$PKG_DIR" && mkdir -p "$PKG_DIR/usr/local/bin" "$PKG_DIR/DEBIAN" "$DIST_DIR"

cp "$ROOT_DIR/cortex-setup-linux-x64" "$PKG_DIR/usr/local/bin/cortex-setup"
chmod +x "$PKG_DIR/usr/local/bin/cortex-setup"

cat > "$PKG_DIR/DEBIAN/control" << EOF
Package: cortex-setup
Version: $VERSION
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Cordfuse <hello@cordfuse.com>
Description: First-time setup wizard for Cortex
 Cortex is a private, AI-scribed record-keeping system.
 This wizard gets you from zero to first session in minutes.
 Homepage: https://github.com/cordfuse/cortex
EOF

dpkg-deb --build "$PKG_DIR" "$DIST_DIR/cortex-setup_${VERSION}_amd64.deb"
echo "Built: $DIST_DIR/cortex-setup_${VERSION}_amd64.deb"
