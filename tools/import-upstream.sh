#!/usr/bin/env bash
# Import GeoGebra's EUPL-1.2 source code into Locus without the parts that are
# not free software.
#
# GeoGebra GmbH licenses its source code under the EUPL 1.2, but its language
# files, documentation and user-interface images and style files (logos,
# icons, style sheets) are CC BY-NC-SA 4.0 (https://www.geogebra.org/license).
# Locus must stay fully free, so this script copies only the source code and
# deletes every file of the second kind. Locus ships its own strings, icons,
# styles and templates in their place.
#
# Usage: tools/import-upstream.sh <upstream-checkout> <target-dir>
# The upstream checkout must be a git clone of github.com/geogebra/geogebra.
# Files are copied from its HEAD commit, which is printed at the end.
set -euo pipefail

upstream=$(realpath "$1")
target=$(realpath "$2")
commit=$(git -C "$upstream" rev-parse HEAD)

staging=$(mktemp -d)
trap 'rm -rf "$staging"' EXIT
git -C "$upstream" archive --format=tar HEAD | tar -x -C "$staging"
cd "$staging"

# Desktop app (Swing, Classic 5): out of scope for a web app, and full of
# non-free images and fonts.
rm -rf source/desktop
# Developer documentation ("all GeoGebra documentation" is CC BY-NC-SA).
rm -rf doc README.md
# Language files: every .properties translation and the generated JS bundles.
rm -rf source/shared/common-jre/src/main/resources/org/geogebra/common/jre/properties
rm -f source/web/web/src/main/resources/org/geogebra/web/pub/js/properties_keys_*.js
# Style sheets and HTML templates.
rm -rf source/web/web/src/main/resources/scss
rm -rf source/web/web/src/main/resources/org/geogebra/web/resources/html
# Demo, test and partner pages served from the war directory.
rm -rf source/web/web/src/main/resources/org/geogebra/web/resources/war
# GeoGebra-branded fonts of unknown provenance.
rm -rf source/web/web/src/main/resources/org/geogebra/web/resources/font
# User-interface images. Fonts of the bundled JLaTeXMath renderer are
# third-party (GPL/OFL/Knuth) and are not images, so they stay.
find source \( -iname '*.png' -o -iname '*.svg' -o -iname '*.gif' \
  -o -iname '*.ico' -o -iname '*.jpg' -o -iname '*.jpeg' \) -type f -delete
# GeoGebra construction files are materials, not code.
find source \( -name '*.ggb' -o -name '*.ggs' \) -type f -delete
find source -type d -empty -delete

# Files that are Locus's own replace the removed ones; copy the tree over the
# target without touching Locus-only paths.
rsync -a "$staging"/ "$target"/
echo "Imported geogebra/geogebra@$commit"
