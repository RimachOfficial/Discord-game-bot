# 🎣 Discord Fishing Bot

A chaotic, heavily economy-driven Discord fishing game built with `discord.py` and `sqlite3`.
Fish, trade on a dynamic live market, manipulate stocks, collect illegal black market items, and build your net worth!

## 🏗️ Architecture

This project strictly adheres to a **3-Tier Architecture (Separation of Concerns)** to ensure high modularity and clean, scalable code:

1. **The Entry/Interface Layer (`commands.py`, `market.py`, `inventory.py`, `karma_system.py`, `shop.py`, `crew.py`)**

* Built as Discord Cogs.
* Parses Discord interactions and user inputs.
* Delegates all math and decision making to the Engine Layer.
* Returns stylized Discord Embeds and UI responses.

2. **The Business & Domain Logic Layer (`engines/*.py`)**

* `fishing_engine.py`: Handles RNG, Karma luck scaling, and passive item drop-rate manipulations.
* `market_engine.py`: Controls live market fluctuations, randomized news crashes/spikes, and buy/sell transaction limits.
* `economy_engine.py`: Processes live net worth evaluations and player portfolio generation based on fluctuating assets.
* `item_engine.py`: Governs the isolated effects of consumable items (e.g., throwing a car battery in the ocean).
* `crew_engine.py`: 🆕 Controls the algorithmic progression math, exponential level-up costs, and automated paycheck scaling for idle workers.

3. **The Data Access Layer (`database.py`)**

* Purely handles database schema creation, reading, updating, and deleting (CRUD).
* Contains exactly zero game logic, math, bounds checking, or item configurations.
* Serves strictly as a robust abstraction for `sqlite3`.

---

## 🌟 Features

* **Dynamic Market Economy:** Fish prices are not static. The market naturally fluctuates every 5-10 minutes. Mass selling a specific fish will crash its value, while mass buying will surge its value.
* **Joint-Stock Idle Crew Operations:** 🆕 Contract and employ your server friends to harvest the open ocean passively! Crew members work around the clock, delivering payouts directly to player balances every few minutes.
* **Live Stock Market Exposure:** 🆕 Hired crew members don't earn static wages. They actively extract fish from specific tiers. If an employee's targeted fish tiers crash on the live market, their efficiency plummets with it—forcing players to strategically buy, sell, or manipulate stock trends to maintain profits.
* **Breaking News Shocks:** Spontaneous events (like a Whale Conservation Act or a Crypto Crash) can instantly manipulate tier values and alert the server.
* **Karma System:** Release your caught fish back into the ocean (`/free`) to gain Karma. Karma permanently boosts your RNG chances to catch rare fish.
* **The Black Market:** Obtain illegal consumables and passive items to rig the game. Inhale Copium for a guaranteed God tier drop, use the Tax Evasion Manual to dump your inventory without crashing the market, or freeze prices with Mommy's Credit Card!
* **Live Portfolios:** The `/balance` command calculates your liquid cash alongside your inventory's live market asset value.

## ⚙️ Configuration

All game balance data is centrally stored in `constants.py`:

* `FISH_DATA` and `FISH_WEIGHTS` control base rarity and values.
* `ITEM_CATALOG` defines the descriptions and mechanics of the items.
* `CREW_CATALOG` 🆕 Governs individual base catch multipliers, targeted asset tiers, and exponential cost scaling limits for idle workers.

---

## 🛠️ Commands

### Fishing & Karma

* `/fish` - Cast your line into the water!
* `/free` - Release your entire inventory into the ocean for Karma luck points.
* `/karma` - View your permanent luck multipliers.
* `/chances` - View your exact personalized drop rates for every tier.

### Passive Idle Crew Management 🆕

* `/crew` - Open your corporate management dashboard. Displays your staff's live level tiers, personalized lore descriptions, live asset values, and dynamic hourly yields. Includes an interactive recruitment select dropdown.
* `/upgrade_crew <member>` - Level up an existing crew member that you already own to multiply their catch capacity. (Strictly locked to assets you have already acquired from the `/crew` dropdown).

### Economy & Market

* `/inventory` - View your stash and its live market performance vs. base value.
* `/balance` - View your total net worth and liquid cash.
* `/market` - View the live stock market prices and trends.
* `/sell <tier>` - Sell all fish of a specific tier to the market.
* `/sell_all` - Liquidate your entire inventory.
* `/buy <tier> <qty>` - Buy fish directly from the market (causes price surge).
* `/leaderboard` - Check the wealthiest players.

### Items

* `/items` - View the Black Market catalog.
* `/use <item>` - Consume an item from your inventory.
* `/give_item` *(Admin)* - Spawn a Black Market item.
* `/setnews` *(Admin)* - Register the channel for Market Shock alerts.

---

## 🚀 Getting Started / Installation

Want to host your own instance of the bot? We use [uv](https://docs.astral.sh/uv/), an extremely fast Python package and project manager, to keep things optimized.

### 1. Prerequisites

* Install Python 3.10+
* Install `uv` on your system.
* Create a Discord Bot on the [Discord Developer Portal](https://discord.com/developers/applications) and copy your **Bot Token**. Ensure you enable the required Gateway Intents (like `message_content` if needed).

### 2. Clone the Repository

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name

```

### 3. Secure Your API Token (Crucial!)

Never hardcode your Discord Bot token into your Python files! We use a `.env` file to keep it a secret.

1. Create a file named `.env` in the root folder of the project.
2. Add your token to the file like this:

```env
DISCORD_TOKEN=your_super_secret_token_here

```

3. **Important:** Make sure you have a `.gitignore` file in your root directory that includes `.env`. This prevents you from accidentally uploading your secret token to GitHub!
*Example `.gitignore`:*

```gitignore
.env
__pycache__/
*.db

```

### 4. Install Dependencies & Run

With `uv` installed and your `.env` configured, you can install everything and boot up the bot in one single command:

```bash
uv run main.py

```

`uv` will automatically create a virtual environment, install the required packages (like `discord.py` and `python-dotenv`), and start the bot. You should see the successful boot sequence in your terminal!