#!/usr/bin/env bash
# Compile the Locus style sheets into the war directory without Gradle, for
# fast iteration while the GWT build is busy. Gradle's compileSass task does
# the same during a full build.
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
sass="$root/source/web/.gradle/sass/web/1.54.0/dart-sass/sass"
[ -x "$sass" ] || { echo "Run a Gradle build once to download dart-sass" >&2; exit 1; }
"$sass" --no-source-map --style=compressed \
  "$root/source/web/web/src/main/resources/scss:$root/source/web/web/war/css"
# resources/war holds static files (fonts, favicon) that Gradle copies too
rsync -a "$root/source/web/web/src/main/resources/org/geogebra/web/resources/war/" "$root/source/web/web/war/"
