#!/usr/bin/env bash
# Build Locus and deploy the static site to Cloudflare Workers.
# Needs CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID in the environment.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${CLOUDFLARE_API_TOKEN:?set CLOUDFLARE_API_TOKEN}" "${CLOUDFLARE_ACCOUNT_ID:?set CLOUDFLARE_ACCOUNT_ID}"
./gradlew -p source/web :web:cleanWar :web:gwtCompile :web:copyHtml -Pgmodule=org.geogebra.web.SuperWeb
python3 tools/build-translations.py --check
npx --yes wrangler@4 deploy
