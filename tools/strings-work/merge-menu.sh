#!/usr/bin/env bash
# Temporary: combine the two menu string parts written in parallel into
# menu.properties and regenerate the web bundles.
set -euo pipefail
here=$(dirname "$0")
props="$here/../../source/shared/common-jre/src/main/resources/org/geogebra/common/jre/properties"
{
  echo "# Locus English strings (menu). SPDX-License-Identifier: EUPL-1.2"
  echo "# Copyright (c) Locus contributors"
  for part in "$here"/menu-part1.properties "$here"/menu-part2.properties; do
    [ -f "$part" ] && grep -v '^#' "$part" || true
  done
} > "$props/menu.properties"
python3 "$here/../build-translations.py"
