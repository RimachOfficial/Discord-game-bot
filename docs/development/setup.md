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
uv run code/main.py
```

## Code Quality

```bash
# Lint
uv run ruff check code/

# Format
uv run ruff format code/

# Test
uv run pytest code/tests/ -v

# Type check
uv run mypy code/ --ignore-missing-imports
```

## Project Structure

```
.
├── code/                   # All source code
│   ├── main.py             # Bot entry point
│   ├── commands.py         # Fishing commands cog
│   ├── market.py           # Market commands + price loop
│   ├── inventory.py        # Inventory commands
│   ├── karma_system.py     # Karma commands
│   ├── shop.py             # Shop commands
│   ├── crew.py             # Crew commands + paycheck loop
│   ├── database.py         # Data access layer (SQLite)
│   ├── constants.py        # Game data & configuration
│   ├── engines/            # Business logic layer
│   ├── tests/              # Test suite
│   └── documentation.md    # Developer documentation
├── docs/                   # Documentation
├── scripts/                # Utility scripts
├── .github/                # GitHub templates & CI
├── Dockerfile              # Docker build
├── docker-compose.yml      # Docker compose
├── pyproject.toml           # Project config & dependencies
└── README.md               # This file