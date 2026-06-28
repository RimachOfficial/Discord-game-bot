# 🎣 Discord Fishing Bot

A chaotic, heavily economy-driven Discord fishing game built with `discord.py` and `sqlite3`. 
Fish, trade on a dynamic live market, manipulate stocks, collect illegal black market items, and build your net worth!

## 🏗️ Architecture

This project strictly adheres to a **3-Tier Architecture (Separation of Concerns)** to ensure high modularity and clean, scalable code:

1. **The Entry/Interface Layer (`commands.py`, `market.py`, `inventory.py`, `karma_system.py`)**
   - Built as Discord Cogs.
   - Parses Discord interactions and user inputs.
   - Delegates all math and decision making to the Engine Layer.
   - Returns stylized Discord Embeds and UI responses.

2. **The Business & Domain Logic Layer (`engines/*.py`)**
   - `fishing_engine.py`: Handles RNG, Karma luck scaling, and passive item drop-rate manipulations.
   - `market_engine.py`: Controls live market fluctuations, randomized news crashes/spikes, and buy/sell transaction limits.
   - `economy_engine.py`: Processes live net worth evaluations and player portfolio generation based on fluctuating assets.
   - `item_engine.py`: Governs the isolated effects of consumable items (e.g., throwing a car battery in the ocean).

3. **The Data Access Layer (`database.py`)**
   - Purely handles database schema creation, reading, updating, and deleting (CRUD).
   - Contains exactly zero game logic, math, bounds checking, or item configurations.
   - Serves strictly as a robust abstraction for `sqlite3`.

---

## 🚀 Features

- **Dynamic Market Economy:** Fish prices are not static. The market naturally fluctuates every 10 minutes. Mass selling a specific fish will crash its value, while mass buying will surge its value.
- **Breaking News Shocks:** Spontaneous events (like a Whale Conservation Act or a Crypto Crash) can instantly manipulate tier values and alert the server.
- **Karma System:** Release your caught fish back into the ocean (`/free`) to gain Karma. Karma permanently boosts your RNG chances to catch rare fish.
- **The Black Market:** Obtain illegal consumables and passive items to rig the game. Inhale Copium for a guaranteed God tier drop or use the Tax Evasion Manual to dump your inventory without crashing the market.
- **Live Portfolios:** The `/balance` command calculates your liquid cash alongside your inventory's live market asset value.

## ⚙️ Configuration

All game balance data is centrally stored in `constants.py`:
- `FISH_DATA` and `FISH_WEIGHTS` control base rarity and values.
- `ITEM_CATALOG` defines the descriptions and mechanics of the items.

## 🛠️ Commands

### Fishing & Karma
- `/fish` - Cast your line into the water! 
- `/free` - Release your entire inventory into the ocean for Karma luck points.
- `/karma` - View your permanent luck multipliers.
- `/chances` - View your exact personalized drop rates for every tier.

### Economy & Market
- `/inventory` - View your stash and its live market performance vs. base value.
- `/balance` - View your total net worth and liquid cash.
- `/market` - View the live stock market prices and trends.
- `/sell <tier>` - Sell all fish of a specific tier to the market.
- `/sell_all` - Liquidate your entire inventory.
- `/buy <tier> <qty>` - Buy fish directly from the market (causes price surge).
- `/leaderboard` - Check the wealthiest players.

### Items
- `/items` - View the Black Market catalog.
- `/use <item>` - Consume an item from your inventory.
- `/give_item` *(Admin)* - Spawn a Black Market item.
- `/setnews` *(Admin)* - Register the channel for Market Shock alerts.
