<div align="center">

# 🎣 Bipbob — Discord Fishing Bot

**A chaotic, economy-driven Discord fishing game with a live stock market, black market items, and idle crew management.**

[![License: MIT+Attribution](https://img.shields.io/badge/License-MIT%20%2B%20Attribution-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![discord.py](https://img.shields.io/badge/discord.py-2.7%2B-5865F2?logo=discord&logoColor=white)](https://discordpy.readthedocs.io/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://docs.astral.sh/uv/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

**[Features](#-features) • [Commands](#-commands) • [Quick Start](#-quick-start) • [Architecture](#%EF%B8%8F-architecture) • [Contributing](CONTRIBUTING.md) • [Docs](docs/)**

</div>

---

## 📖 Overview

Bipbob is a **heavily economy-driven Discord fishing simulator** where nothing is static. Fish prices fluctuate like a real stock market, your actions directly impact global pricing, and you can rig the system with illegal black market items. Hire your friends as crew members, manipulate stock trends, and build your net worth.

**The economy is the game.** Every `/fish`, `/sell`, and `/buy` ripples through the market.

---

## ✨ Features

### 🎣 Dynamic Fishing
- **12 rarity tiers** — from `Correction 1️⃣` to `P-Ban 3️⃣`
- **Karma system** — release fish for permanent luck boosts to rare tiers
- **Passive item modifiers** — change your drop rates with black market gear

### 📈 Live Stock Market
- Prices fluctuate **every 5 minutes** with natural drift
- **Supply & demand** — mass selling crashes prices, mass buying surges them
- **Breaking News shocks** — random events (Crypto Crash, Whale Act, Shark Week) that instantly manipulate prices
- **Live price charts** — `/market` shows matplotlib-generated trend charts

### 🏪 Black Market Items
| Item | Type | Effect |
|------|------|--------|
| 🍼 Copium Inhaler | Consumable | 1% chance for P-Ban 3️⃣ on next cast |
| 🧼 Gamer Girl Bathwater | Lure | Next 3 catches from rare tiers only |
| 🔋 Car Battery | Consumable | Pull 15 fish instantly (costs 50 karma) |
| 📄 Tax Evasion Manual | Passive | Sell without crashing the market |
| 📱 Bogdanoff's Burner Phone | Consumable | 3x market crash on sell |
| 💳 Mommy's Credit Card | Passive | Buy without price surge |
| ♻️ Discord Mod Application | Passive | Blocks Wet Cardboard, doubles Correction 2️⃣ |
| 🧢 Boyfriend Repellent | Passive | Blocks Warning 1️⃣ tier entirely |

### 👥 Idle Crew Operations
- Hire 6 unique crew members with **real player-inspired lore**
- Each crew member targets **specific fish tiers**
- Their efficiency fluctuates with **live market prices**
- Level them up for exponential yield increases

### 🛡️ Anti-Exploit Design
- **Slippage pricing** — you're paid the average price across the crash curve
- **Hard price floors/ceilings** — prevents total market collapse or infinite inflation
- **Cooldowns** — `/fish` has a 30s cooldown to prevent spam

---

## 🛠️ Commands

### Fishing & Karma
| Command | Description |
|---------|-------------|
| `/fish` | Cast your line! 30s cooldown |
| `/free` | Release all fish into the ocean for karma |
| `/karma` | View your permanent luck multipliers |
| `/chances` | See your personalized drop rates |

### Economy & Market
| Command | Description |
|---------|-------------|
| `/market` | View live stock prices + trend chart |
| `/inventory` | Check your fish stash with live valuation |
| `/balance` | View net worth (cash + inventory value) |
| `/sell <tier>` | Liquidate a specific tier |
| `/sell_all` | Dump everything on the market |
| `/buy <tier> <qty>` | Buy fish (drives prices up) |
| `/leaderboard` | Richest players on the server |

### Crew Management
| Command | Description |
|---------|-------------|
| `/crew` | Open the crew dashboard + recruitment |
| `/upgrade_crew <member>` | Level up a hired crew member |

### Black Market
| Command | Description |
|---------|-------------|
| `/shop` | Open the Black Market shop |
| `/items` | View item catalog |
| `/use <item>` | Consume an item |
| `/toggle <item>` | Enable/disable passive items |

### Admin
| Command | Description |
|---------|-------------|
| `/setnews` | Set channel for market shock alerts |
| `/give_item` | Spawn items for testing |

---

## 🚀 Quick Start

### Prerequisites
- **[Python](https://python.org) 3.12+**
- **[uv](https://docs.astral.sh/uv/)** (fast Python package manager)
- A **Discord Bot Token** from the [Developer Portal](https://discord.com/developers/applications)

### One-Command Setup

```bash
# Clone
git clone https://github.com/RimachOfficial/Discord-game-bot.git
cd Discord-game-bot

# Configure your token
echo "DISCORD_TOKEN=your_token_here" > .env

# Run (uv handles everything — venv + deps + execution)
uv run code/main.py
```

> ⚠️ **Never commit your `.env` file!** It's already in `.gitignore`.

### Docker Setup

```bash
cp .env.example .env   # Edit with your token
docker compose up -d
```

### Detailed Installation

See the **[Installation Guide](docs/deployment/hosting.md)** for:
- Systemd service setup (Linux)
- Docker deployment
- Resource requirements
- Monitoring tips

---

## 🏗️ Architecture

This project adheres to a strict **3-Tier Architecture**:

```
┌──────────────────────────────────────┐
<<<<<<< HEAD
│      INTERFACE LAYER (Cogs)         │
│  code/commands.py · code/market.py  │
│  code/shop.py · code/inventory.py   │
│  code/karma_system.py · code/crew.py│
├──────────────────────────────────────┤
│      BUSINESS LOGIC (Engines)       │
│  code/engines/fishing_engine.py     │
│  code/engines/market_engine.py      │
│  code/engines/economy_engine.py     │
│  code/engines/item_engine.py        │
│  code/engines/crew_engine.py        │
│  code/engines/market_chart_engine.py│
├──────────────────────────────────────┤
│      DATA ACCESS (Database)         │
│  code/database.py                   │
│  (Pure SQLite CRUD — zero logic)    │
=======
│      INTERFACE LAYER (Cogs)          │
│  commands.py · market.py · shop.py   │
│  inventory.py · karma_system.py      │
│  crew.py                             │
├──────────────────────────────────────┤
│      BUSINESS LOGIC (Engines)        │
│  engines/fishing_engine.py           │
│  engines/market_engine.py            │
│  engines/economy_engine.py           │
│  engines/item_engine.py              │
│  engines/crew_engine.py              │
│  engines/market_chart_engine.py      │
├──────────────────────────────────────┤
│      DATA ACCESS (Database)          │
│  database.py                         │
│  (Pure SQLite CRUD — zero logic)     │
>>>>>>> acd7f462be6213052b9773bda8fd9a5471d08921
└──────────────────────────────────────┘
```

Each layer has strict responsibilities:
- **Interface**: Discord interactions, embeds, UI — no math or game logic
- **Engines**: All game mechanics, calculations, RNG — pure Python
- **Database**: SQLite CRUD operations — no business logic

> For a deep dive, see the [Architecture Document](docs/architecture.md).

---

## 🧪 Tech Stack

| Component | Technology |
|-----------|------------|
| Runtime | Python 3.12+ |
| Discord API | discord.py 2.7+ |
| Database | SQLite3 |
| Package Manager | uv |
| Charts | matplotlib |
| Linting | ruff |
| Testing | pytest |

---

## 🫂 Contributing

**Contributions are welcome!** Check out the [Contributing Guide](CONTRIBUTING.md) for:

- Development setup instructions
- Coding standards (PEP 8, type hints, ruff)
- Commit message conventions
- PR process and checklist

### Quick Start for Contributors

```bash
git clone https://github.com/RimachOfficial/Discord-game-bot.git
cd Discord-game-bot
uv sync
uv run pre-commit install
uv run code/main.py
```

---

## 📄 License

This project is licensed under the **MIT License with Attribution** — you are free to use, modify, and distribute the code, provided you credit the original author.

See the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with chaos and ❤️ by [RimachOfficial](https://github.com/RimachOfficial)**

[![GitHub stars](https://img.shields.io/github/stars/RimachOfficial/Discord-game-bot?style=social)](https://github.com/RimachOfficial/Discord-game-bot/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/RimachOfficial/Discord-game-bot?style=social)](https://github.com/RimachOfficial/Discord-game-bot/network/members)

</div>
