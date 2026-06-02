# Deploy folder

Everything needed to host the bot on a Raspberry Pi under `systemd`.

## Contents

| File | Runs on | Purpose |
|------|---------|---------|
| `deploy.sh` | Mac | Copies app files to the Pi and runs the installer over SSH |
| `install.sh` | Pi | Creates venv, installs deps, installs/enables the systemd service |
| `bot.env.example` | — | Template for the secret token file (`bot.env`) |

## One-command deploy (from your Mac)

```bash
deploy/deploy.sh washer@<pi-ip>
```

This mirrors the repo layout on the Pi — `src/` (app code), `requirements.txt`,
and `deploy/` (service file + installer) under `/home/<user>/sport-check-bot` —
then runs `install.sh` there.

The first run will stop and tell you to do two things on the Pi (it can't do
them for you):

1. **Set the token** — edit `~/sport-check-bot/bot.env` and put your real
   `SPORT_BOT_TOKEN` in it.
2. **Generate `config.yaml`** — after every participant has sent a message in
   the group:

   ```bash
   cd ~/sport-check-bot
   set -a; source bot.env; set +a
   venv/bin/python src/init_config.py
   ```

Then start it:

```bash
sudo systemctl restart sport-check-bot
sudo systemctl status sport-check-bot
```

## Pushing code changes later

Just re-run the same command — `install.sh` is idempotent (it won't recreate
the venv or clobber `bot.env`/`config.yaml`) and will restart the service:

```bash
deploy/deploy.sh washer@<pi-ip>
```

## Logs

```bash
ssh washer@<pi-ip> "journalctl -u sport-check-bot -f"
```
