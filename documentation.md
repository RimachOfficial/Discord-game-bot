# 📚 Bipbob Developer Documentation

This document outlines the internal architecture, database schema, and economic math driving the Bipbob Discord Bot.

## 🏗️ Project Architecture

The bot uses `discord.py`'s Cog architecture to keep code modular and clean, adhering to a **3-Tier Architecture** (Separation of Concerns).

* `main.py`: The entry point. Handles bot initialization, loading environment variables via `.env`, syncing slash commands, and loading extensions.
* `database.py`: The Data Access Layer (DAL). Hand-pures SQLite queries, table creation, and transaction safety. Contains exactly zero game logic, math, bounds checking, or item configurations.
* `commands.py` / `market.py` / `inventory.py` / `karma_system.py` / `shop.py`: The Interface/Entry Layer. Built as Discord Cogs. Parses interactions, handles UI formatting via embeds, and passes execution data directly to the engines.
* `engines/*.py`: The Business Logic Layer. Houses `fishing_engine.py`, `market_engine.py`, `economy_engine.py`, and `item_engine.py`. Governs all math, transaction safety, and RNG calculations isolated from the data layer.

---

## 🗄️ Database Schema

SQLite3 is used for lightweight, file-based data storage (`fishing_game.db`). All numerical fields tracking balances, values, and quantities use `REAL` to handle precision slippage, infinite scaling numbers, and floating-point math smoothly.

### 1. `players`

Tracks player identification and liquid currency.

* `user_id` (TEXT PRIMARY KEY)
* `username` (TEXT)
* `cash` (REAL) — *Upgraded to REAL to track accurate transaction fractions.*

### 2. `inventory`

Tracks individual fish ownership by specific species.

* `user_id` (TEXT)
* `fish_name` (TEXT) — *Stores specific species names (e.g., "Atlantic Cod", "Whale Shark").*
* `quantity` (REAL) — *Upgraded to REAL to support hyper-scaled mass bulk transactions.*
* *Primary Key:* Composite of `(user_id, fish_name)`

### 3. `market`

Tracks the current shifting live price of every tier.

* `tier_name` (TEXT PRIMARY KEY)
* `current_price` (REAL) — *Upgraded to REAL to support exact market trends.*

### 4. `server_settings`

Stores server-specific configurations for the global broadcast network.

* `guild_id` (TEXT PRIMARY KEY)
* `news_channel_id` (TEXT)

---

## ⚖️ Economy & Math Mechanics

### 1. Drop Rates (The Catch)

When a user types `/fish`, a tier is selected based on the following weighted probabilities before rolling a species with equal distribution within that tier:

* **Bozo ⚪:** 35%
* **Common 🔘:** 25%
* **Uncommon 🔵:** 15%
* **El Bozo 🟢:** 10%
* **Your Mother 🟣:** 8%
* **Legendary 🟡:** 5%
* **Rimach 🔴:** 1.5%
* **Gay 🌈:** 0.4%
* **Divine ⚪🟣:** 0.09%
* **God ✨:** 0.01%

### 2. Natural Market Fluctuations

Every 5 minutes, a background loop ticks in `market.py`.

* Each tier's price is adjusted by a random percentage between **-15% and +20%**.
* **Hard Bounds:** Enforced using floor/ceiling factors. Prices can never drop below 5% (`weight_floor`) of their base value, nor exceed 1000% (`weight_ceiling`) of their base value.

### 3. Supply & Demand (Slippage & Anti-Exploit)

When selling (`/sell` or `/sell_all`) or buying (`/buy`), transactions cause dynamic market movement evaluated across floating-point bounds.

* **Price Crash Formula:** `Price Drop = Quantity * (Base Price * 0.005)`
* **🌟 Slippage Protection:** To prevent exploiters from reaping full-peak value right before a massive dump, players are paid the **average unit price** across the crash curve:

$$
\text{Average Unit Price} = \frac{\text{Current Price} + \text{New Price}}{2.0}
$$


$$
\text{Total Payout} = \text{Average Unit Price} \times \text{Quantity}
$$



### 4. Black Market Modifiers & Market Shocks

* **Market Shocks (30% Chance per loop):** Triggers breaking news items that force a tier to spike or crash via multipliers (ranging from`weight_floor` to `weight_ceiling`).
* **📄 Tax Evasion Manual:** Bypasses global market impact when selling. The market price remains frozen (`actual_drop = 0.0`), hiding transactions from global tracking.
* **📱 Burner Phone (Bogdanoff Short Squeeze):** Triples the player's downward market impact ($3.0 \times \text{normal drop}$), aggressively obliterating a tier's market value for everyone else while paying the user normal slippage rates.
* **💳 Mommy's Credit Card:** Acts as an instant market freeze on buying. Bypasses the standard upward slippage penalty, allowing the player to buy limitless volume at a flat market rate to fund systems like mass releasing.

---

## 🛡️ Anti-Lag Measures (Deferring)

To comply with Discord's strict 3-second interaction window, all core interaction commands (`/fish`, `/inventory`, `/sell`, `/sell_all`, `/market`, `/buy`, `/setnews`) immediately invoke `await interaction.response.defer()`. This converts the 3-second timeout into a safe 15-minute execution window, completely eliminating `Error 10062: Unknown interaction` from blocking heavy database execution or complex calculations under high workloads.

---

## 🎣 Karma System: Dynamic Catch Rates

The Karma System introduces personalized, dynamic RNG to the fishing mechanics. A player's catch probabilities scale directly with the amount of fish they have released back into the wild via the `/free` command.

### 🛠️ Core Execution Protocol

**1. Safe Variable Extraction**
When a player initiates a command modifying or evaluating Karma, database rows are parsed into memory via a safe static dictionary format:

```python
raw_karma = dict(current_karma)
total_available_karma = sum(float(points) for points in raw_karma.values())
```

This protects iterable query structures from premature memory consumption and guarantees seamless loop utility across engine logic.

**2. Building the Dynamic Dice**
The fishing engine iterates through every available fish tier to generate an adjusted weight mapping before casting lines:

* The core formula grants a **+1% luck bonus to the base weight for every 100 Karma points** in a specific tier.
* **The Math:**

$$
\text{Luck Bonus Pct} = \frac{\text{Karma Points}}{100.0}
$$


$$
\text{Adjusted Weight} = \text{Base Weight} \times \left(1 + \frac{\text{Luck Bonus Pct} / 100.0}{1.0}\right)
$$



**3. Rolling Modified Probabilities**
`random.choices` executes using the player's personalized `dynamic_weights` mapping array, giving hard-grinding players massive custom advantages over rare tiers.