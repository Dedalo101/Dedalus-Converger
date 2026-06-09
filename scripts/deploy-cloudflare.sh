#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="${CLOUDFLARE_PAGES_PROJECT:-dedalus-converger}"

if ! npx wrangler whoami >/dev/null 2>&1; then
  echo "Not logged in. Run: npx wrangler login" >&2
  exit 1
fi

npx wrangler pages deploy site --project-name="$PROJECT_NAME"
echo "Deployed to https://${PROJECT_NAME}.pages.dev"