#!/usr/bin/env zsh
set -euo pipefail

# Create venv
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install backend deps
pip install -r backend/requirements.txt

# macOS: install tesseract via brew if not present
if ! command -v tesseract >/dev/null 2>&1; then
  echo "Installing tesseract via Homebrew..."
  if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew not found. Please install Homebrew from https://brew.sh and re-run." >&2
    exit 1
  fi
  brew install tesseract poppler
fi

echo "Setup complete. Activate: 'source .venv/bin/activate'"
