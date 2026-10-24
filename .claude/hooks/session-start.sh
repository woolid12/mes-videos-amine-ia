#!/bin/bash
set -euo pipefail

# Uniquement dans les sessions cloud (Claude Code sur le web)
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# yt-dlp : téléchargement de vidéos
if ! command -v yt-dlp >/dev/null 2>&1; then
  pip install -q yt-dlp
fi
