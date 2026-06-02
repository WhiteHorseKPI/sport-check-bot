#!/usr/bin/env bash
#
# Ship the Sport Check Bot to a Raspberry Pi and run the installer.
# Run this from your Mac, from anywhere in the repo.
#
# Usage:
#   deploy/deploy.sh washer@192.168.1.50
#   deploy/deploy.sh washer@raspberrypi.local
#
# What it does:
#   1. scp's the app files + installer to /home/<user>/sport-check-bot on the Pi
#   2. runs install.sh over SSH (sets up venv, deps and the systemd service)
#
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <user@pi-host>" >&2
  echo "Example: $0 washer@192.168.1.50" >&2
  exit 1
fi

REMOTE="$1"                       # e.g. washer@192.168.1.50
REMOTE_DIR="sport-check-bot"      # relative to the remote user's home

# Repo root = parent of this script's directory.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Application code (mirrors the repo's src/ on the Pi).
SRC_FILES=(
  bot.py
  storage.py
  constants.py
  init_config.py
)

# Deploy artifacts (mirrors the repo's deploy/ on the Pi).
DEPLOY_FILES=(
  install.sh
  sport-check-bot.service
  bot.env.example
)

echo "==> Creating directory layout on $REMOTE"
ssh "$REMOTE" "mkdir -p ~/$REMOTE_DIR/src ~/$REMOTE_DIR/deploy"

echo "==> Copying source files"
for f in "${SRC_FILES[@]}"; do
  scp "$ROOT_DIR/src/$f" "$REMOTE:$REMOTE_DIR/src/"
done

echo "==> Copying requirements.txt"
scp "$ROOT_DIR/requirements.txt" "$REMOTE:$REMOTE_DIR/"

echo "==> Copying deploy files"
for f in "${DEPLOY_FILES[@]}"; do
  scp "$SCRIPT_DIR/$f" "$REMOTE:$REMOTE_DIR/deploy/"
done

# Ship a local config.yaml if you already have one; otherwise generate it on
# the Pi with src/init_config.py.
if [[ -f "$ROOT_DIR/config.yaml" ]]; then
  echo "==> Copying config.yaml"
  scp "$ROOT_DIR/config.yaml" "$REMOTE:$REMOTE_DIR/"
else
  echo "==> No local config.yaml — generate it on the Pi after deploy"
fi

echo "==> Running installer on the Pi"
ssh -t "$REMOTE" "cd ~/$REMOTE_DIR && bash deploy/install.sh"

echo "==> Done."
