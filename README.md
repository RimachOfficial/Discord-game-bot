# 🎣 Bipbob: Discord Fishing & Economy Bot

Bipbob is a fully-featured Discord bot that combines RNG fishing mechanics with a living, highly dynamic stock market. Players catch fish, hold them in their inventory, and sell them for profit—but the market reacts to their actions. If everyone dumps the same fish, the price crashes. If they hold, natural fluctuations and random market shocks can send prices to the moon!

## ✨ Features

* **🎣 Interactive Fishing (`/fish`)**
  * Roll for different tiers of fish ranging from *Bozo* to *God* tier.
  * Every catch displays a beautiful Discord embed complete with tier-specific meme GIFs.
  * 30-second cooldown to prevent spamming.

* **🎒 Dynamic Inventory (`/inventory`)**
  * Clean, side-by-side layout grouping fish by their tiers.
  * Automatically calculates the live wealth of your current stash based on base values.

* **📈 Slime Rancher-Style Economy (`/sell` & `/market`)**
  * **Live Market:** Prices shift naturally every 5 minutes.
  * **Supply & Demand:** Selling massive quantities of a single tier will actively crash its market value for the entire server.
  * **Hoarding Rewarded:** Prices slowly heal over time, encouraging players to buy low and sell high.

* **📰 Global News Network (`/setnews`)**
  * 15% chance every 5 minutes for a **Market Shock** (e.g., "Crypto Crash" or "Whale Conservation Act").
  * Shocks instantly skyrocket or crash a specific tier's price.
  * Admins can set a news channel to receive global breaking news broadcasts automatically.

## 🚀 Installation & Setup

### Prerequisites
* Python 3.8 or higher.
* A Discord Bot Token (grab one from the [Discord Developer Portal](https://discord.com/developers/applications)).

### Installation
1. Clone the repository to your local machine.
2. Install the required Python libraries:
   ```bash
   pip install discord.py
   ```
3. Insert your Bot Token inside `main.py` (or load it via environment variables).
4. Run the bot:
   ```bash
   python main.py
   ```
*Note: The SQLite database (`fishing_game.db`) will automatically generate itself upon the first boot.*

## 📜 Commands List

| Command | Description | Permissions |
| :--- | :--- | :--- |
| `/fish` | Cast your line! Catches a random fish based on tier drop rates. | @everyone |
| `/inventory` | View your caught fish, sorted by tier and calculated value. | @everyone |
| `/market` | View the live stock market prices for all fish tiers. | @everyone |
| `/sell [tier]` | Liquidates all fish in a specific tier for cash, impacting the market. | @everyone |
| `/setnews [channel]`| Sets the channel for Market Shock news broadcasts. | Administrator/Manage Server |

---
*Built with ❤️ using `discord.py` and SQLite.*
