#!/bin/bash
set -e

VERSION=${1:-1.0.0}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
DIST_DIR="$SCRIPT_DIR/dist"
RPM_BUILD="$SCRIPT_DIR/rpmbuild"

rm -rf "$RPM_BUILD" && mkdir -p "$RPM_BUILD"/{BUILD,RPMS,SOURCES,SPECS,SRPMS} "$DIST_DIR"

mkdir -p "$RPM_BUILD/SOURCES/cortex-setup-$VERSION/usr/local/bin"
cp "$ROOT_DIR/cortex-setup-linux-x64" "$RPM_BUILD/SOURCES/cortex-setup-$VERSION/usr/local/bin/cortex-setup"
chmod +x "$RPM_BUILD/SOURCES/cortex-setup-$VERSION/usr/local/bin/cortex-setup"
cd "$RPM_BUILD/SOURCES" && tar czf "cortex-setup-$VERSION.tar.gz" "cortex-setup-$VERSION" && cd "$SCRIPT_DIR"

cat > "$RPM_BUILD/SPECS/cortex-setup.spec" << EOF
Name:           cortex-setup
Version:        $VERSION
Release:        1
Summary:        First-time setup wizard for Cortex
License:        MIT
URL:            https://github.com/cordfuse/cortex
Source0:        cortex-setup-%{version}.tar.gz

%description
Cortex is a private, AI-scribed record-keeping system.
This wizard gets you from zero to first session in minutes.

%prep
%setup -q -n cortex-setup-%{version}

%install
mkdir -p %{buildroot}/usr/local/bin
cp usr/local/bin/cortex-setup %{buildroot}/usr/local/bin/cortex-setup
chmod +x %{buildroot}/usr/local/bin/cortex-setup

%files
/usr/local/bin/cortex-setup

%changelog
* $(date '+%a %b %d %Y') Cordfuse <hello@cordfuse.com> - $VERSION-1
- Release $VERSION
EOF

rpmbuild --define "_topdir $RPM_BUILD" -bb "$RPM_BUILD/SPECS/cortex-setup.spec"
cp "$RPM_BUILD/RPMS/x86_64/"*.rpm "$DIST_DIR/"
echo "Built: $DIST_DIR/cortex-setup-$VERSION-1.x86_64.rpm"
