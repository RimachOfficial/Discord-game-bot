# 📚 Bipbob Developer Documentation

This document outlines the internal architecture, database schema, and economic math driving the Bipbob Discord Bot.

## 🏗️ Project Architecture

The bot uses `discord.py`'s Cog architecture to keep code modular and clean.

* `main.py`: The entry point. Handles bot initialization, syncing slash commands, and loading extensions.
* `database.py`: The SQLite database manager. Handles all queries, table creation, and transaction safety. Stores global configurations (like `FISH_DATA`).
* `commands.py`: Contains the core `/fish` command and its RNG logic.
* `inventory.py`: Contains the `/inventory` command, utilizing Discord Embed inline fields for UI layout.
* `market.py`: The beating heart of the economy. Contains the `/market`, `/sell`, and `/setnews` commands, alongside the `discord.ext.tasks` background loop for price shifts and news broadcasts.

---

## 🗄️ Database Schema

SQLite3 is used for lightweight, file-based data storage (`fishing_game.db`).

### 1. `players`
Tracks player wealth.
* `user_id` (TEXT PRIMARY KEY)
* `username` (TEXT)
* `cash` (INTEGER)

### 2. `inventory`
Tracks individual fish ownership.
* `user_id` (TEXT)
* `fish_tier` (TEXT) - Stores the specific species name (e.g., "Blobfish 👁️👄👁️").
* `quantity` (INTEGER)
* *Primary Key:* Composite of `(user_id, fish_tier)`

### 3. `market`
Tracks the live price of every tier.
* `tier_name` (TEXT PRIMARY KEY)
* `current_price` (INTEGER)

### 4. `server_settings`
Stores server-specific configurations for the global broadcast network.
* `guild_id` (TEXT PRIMARY KEY)
* `news_channel_id` (TEXT)

---

## ⚖️ Economy & Math Mechanics

### 1. Drop Rates (The Catch)
When a user types `/fish`, a tier is selected based on the following weighted probabilities:
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

Once a tier is selected, a specific species within that tier is chosen at random with equal distribution.

### 2. Natural Market Fluctuations
Every 5 minutes, a background loop ticks in `market.py`.
* Each tier's price is adjusted by a random percentage between **-15% and +20%**.
* **Hard Caps:** Prices can never drop below 40% of their base value, nor exceed 250% of their base value.

### 3. Supply & Demand (Player Impact)
When a player uses `/sell`, they crash the market value of the sold tier.
* **Math:** `Price Drop = Quantity Sold * (Base Price * 0.005)`
* Selling 100 fish will drop the price by 50% of the tier's base value.
* This logic ensures the market reacts dynamically to hoarding and mass liquidations.

### 4. Market Shocks
During the 5-minute tick, there is a **15% chance** to trigger a Market Shock.
* A random event is selected (e.g., "Whale Conservation Act").
* The affected tier instantly applies a massive multiplier (e.g., x2.0 or x0.4).
* The bot loops through the `server_settings` table and broadcasts a breaking news embed to all configured `news_channel_id`s.

---

## 🛡️ Anti-Lag Measures (Deferring)
To comply with Discord's strict 3-second interaction window, all major commands (`/fish`, `/inventory`, `/sell`, `/market`) immediately invoke `await interaction.response.defer()`. This converts the 3-second timeout into a 15-minute window, allowing database queries and GIF loading to complete without triggering `Error 10062: Unknown interaction` during network spikes.
