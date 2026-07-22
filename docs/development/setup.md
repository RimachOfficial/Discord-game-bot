# Development Setup

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — Fast Python package manager
- A Discord Bot Token ([Discord Developer Portal](https://discord.com/developers/applications))

## One-Time Setup

```bash
# Clone the repository
git clone https://github.com/RimachOfficial/Discord-game-bot.git
cd Discord-game-bot

# Create your environment config
cp .env.example .env
# Edit .env and add your DISCORD_TOKEN

# Sync dependencies
uv sync

# Install pre-commit hooks (optional but recommended)
uv run pre-commit install
```

## Running in Development

```bash
# Run the bot directly
uv run main.py
```

## Code Quality

```bash
# Lint
uv run ruff check .

# Format
uv run ruff format .

# Test
uv run pytest -v

# Type check
uv run mypy . --ignore-missing-imports
```

## Project Structure

```
.
├── main.py                 # Bot entry point
├── commands.py             # Fishing commands cog
├── market.py               # Market commands + price loop
├── inventory.py            # Inventory commands
├── karma_system.py         # Karma commands
├── shop.py                 # Shop commands
├── crew.py                 # Crew commands + paycheck loop
├── database.py             # Data access layer (SQLite)
├── constants.py            # Game data & configuration
├── engines/                # Business logic layer
│   ├── fishing_engine.py
│   ├── market_engine.py
│   ├── economy_engine.py
│   ├── item_engine.py
│   ├── crew_engine.py
│   └── market_chart_engine.py
├── tests/                  # Test suite
├── docs/                   # Documentation
└── .github/                # GitHub templates & CI