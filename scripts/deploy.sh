#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
npm ci
npm run build
npx firebase-tools deploy --only hosting --project granted-ai-2026
