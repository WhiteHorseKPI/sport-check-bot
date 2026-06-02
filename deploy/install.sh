#!/usr/bin/env bash
#
# Set up the Sport Check Bot on a Raspberry Pi.
# Run this ON THE PI (deploy.sh runs it for you automatically).
#
# Idempotent: safe to re-run after pushing new code.
#
set -euo pipefail

# This script lives in <project>/deploy, so the project root is one level up.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SERVICE="sport-check-bot"
VENV="$PROJECT_DIR/venv"

cd "$PROJECT_DIR"

echo "==> Creating virtual environment"
if [[ ! -d "$VENV" ]]; then
  python3 -m venv "$VENV"
fi

echo "==> Installing dependencies"
"$VENV/bin/pip" install --upgrade pip >/dev/null
"$VENV/bin/pip" install -r requirements.txt

echo "==> Checking bot token"
if [[ ! -f "$PROJECT_DIR/bot.env" ]]; then
  cp "$SCRIPT_DIR/bot.env.example" "$PROJECT_DIR/bot.env"
  chmod 600 "$PROJECT_DIR/bot.env"
  echo "!! Created bot.env from template — edit it and set SPORT_BOT_TOKEN:"
  echo "     nano $PROJECT_DIR/bot.env"
  TOKEN_MISSING=1
elif grep -q "YOUR_BOT_TOKEN" "$PROJECT_DIR/bot.env"; then
  echo "!! bot.env still has the placeholder token — edit it:"
  echo "     nano $PROJECT_DIR/bot.env"
  TOKEN_MISSING=1
else
  TOKEN_MISSING=0
fi

echo "==> Installing systemd service"
sudo cp "$SCRIPT_DIR/$SERVICE.service" "/etc/systemd/system/$SERVICE.service"
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE"

if [[ ! -f "$PROJECT_DIR/config.yaml" ]]; then
  echo
  echo "!! config.yaml not found. Generate it once everyone has posted in the group:"
  echo "     set -a; source $PROJECT_DIR/bot.env; set +a"
  echo "     $VENV/bin/python $PROJECT_DIR/src/init_config.py"
  CONFIG_MISSING=1
else
  CONFIG_MISSING=0
fi

if [[ "${TOKEN_MISSING:-0}" -eq 0 && "${CONFIG_MISSING:-0}" -eq 0 ]]; then
  echo "==> Starting service"
  sudo systemctl restart "$SERVICE"
  sudo systemctl status "$SERVICE" --no-pager
else
  echo
  echo "==> Setup incomplete. After fixing the items above, start the bot with:"
  echo "     sudo systemctl restart $SERVICE"
  echo "     sudo systemctl status $SERVICE"
fi
