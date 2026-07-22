# Self-Hosting Guide

## Option 1: Direct (uv)

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

### Steps

```bash
# Clone
git clone https://github.com/RimachOfficial/Discord-game-bot.git
cd Discord-game-bot

# Configure
cp .env.example .env
# Edit .env with your DISCORD_TOKEN

# Run
uv run main.py
```

For persistent hosting, use `tmux` or `screen`:

```bash
tmux new -s fishing-bot
uv run main.py
# Ctrl+B, D to detach
```

## Option 2: Docker

### Prerequisites
- Docker Engine 24+
- Docker Compose v2+

### Steps

```bash
# Clone
git clone https://github.com/RimachOfficial/Discord-game-bot.git
cd Discord-game-bot

# Configure
cp .env.example .env
# Edit .env with your DISCORD_TOKEN

# Build and run
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

### Data Persistence

The SQLite database is stored in `./data/fishing_game.db` (mounted as a Docker volume). To reset the database:

```bash
docker compose down
rm -rf data/
docker compose up -d
```

## Option 3: Systemd Service (Linux)

Create `/etc/systemd/system/fishing-bot.service`:

```ini
[Unit]
Description=Discord Fishing Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/Discord-game-bot
ExecStart=/usr/local/bin/uv run main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now fishing-bot
sudo systemctl status fishing-bot
```

## Resource Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU      | 1 vCPU  | 2 vCPU      |
| RAM      | 256 MB  | 512 MB      |
| Storage  | 100 MB  | 500 MB      |
| Network  | Any     | Any         |

## Monitoring

- Check bot logs: `docker compose logs -f` or `journalctl -u fishing-bot -f`
- Monitor database size: `ls -lh data/fishing_game.db`
- The bot prints status messages on every market cycle and fish catch.