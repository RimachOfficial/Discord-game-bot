import sqlite3
import random

FISH_DATA = {
    "Bozo ⚪": {
        "value": 10,
        "species": ["Old Boot", "Wet Cardboard", "Plastic Bottle"],
        "gif": "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExaXZycDRqY3k1cHBiOWhmbGxmNTN3bTI4cmpybXZmM25xN24zaXRiYiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/n6z0sYdK2qIUI6Uf8g/giphy.gif" # Clown putting on makeup
    },
    "Common 🔘": {
        "value": 25,
        "species": ["Atlantic Cod", "River Carp", "Pond Tilapia"],
        "gif": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZHN6amt4Y3JwdmM2MWx4aTFkY21wNTFoeXZsa2hsanhueXlsZ3kzZSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/lPuW5AlR9AeWzSsIqi/giphy.gif" # Low-res spinning fish
    },
    "Uncommon 🔵": {
        "value": 50,
        "species": ["Sockeye Salmon", "Rainbow Trout", "Red Snapper"],
        "gif": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZHN6amt4Y3JwdmM2MWx4aTFkY21wNTFoeXZsa2hsanhueXlsZ3kzZSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/7eVp9MHlNI90c/giphy.gif" # Cat slapping a fish
    },
    "El Bozo 🟢": {
        "value": 100,
        "species": ["Mako Shark (1,221 lbs)", "Hammerhead Shark (1,280 lbs)", "Sixgill Shark (1,298 lbs)"],
        "gif": "https://media.tenor.com/x8v1oNUOmg4AAAAM/clown-makeup.gif" # RIP Bozo dance
    },
    "Your Mother 🟣": {
        "value": 500,
        "species": ["Whale Shark (41,000 lbs - Absolute Unit)"],
        "gif": "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3aTQ5NHBucjV0MndsaG50a3dvbHFwczgzN3pheW1lMGxtbXZtcGticSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/dJeVcFUo10kcU/giphy.gif" # Massive whale splash
    },
    "Legendary 🟡": {
        "value": 1000,
        "species": ["Pacific Blue Marlin (1,376 lbs)", "Atlantic Blue Marlin (1,402 lbs)", "Black Marlin (1,560 lbs)"],
        "gif": "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3c2RjNXlldjcwYndxeDVycTgwZjU5dHFucmV2bXZrNXI5eDFzY2swZSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/wWXH3OgwPGXlJdZw26/giphy.gif" # Hype fishing freakout
    },
    "Rimach 🔴": {
        "value": 5000,
        "species": ["Greenland Shark (1,708 lbs)", "Tiger Shark (1,785 lbs)"],
        "gif": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZnVreXRoNHo5MGQ3bzljeHN1ODZ6ODQ0OG0zYnd5YjE3NjNremNieCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/ZNLKLh8vlfRrWnL4mj/giphy.gif" # GigaChad nodding
    },
    "Gay 🌈": {
        "value": 20000,
        "species": ["Blobfish 👁️👄👁️", "Ocean Sunfish 🐋", "Goblin Shark 👺"],
        "gif": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaWx4MHpnM2J0enZpYmt3YnBuNzlvdDVxbDNoeGdhc2dyajVkYThmdyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/W5NrtmMTEBP3pTKr1L/giphy.gif" # Rainbow dancing Blobfish
    },
    "Divine ⚪🟣": {
        "value": 100000,
        "species": ["Great White Shark (2,664 lbs - Alfred Dean Record)"],
        "gif": "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3ajhtZWk0NmhwMXlzZngxM2J2YXp5MDMxbDJmczN0YTIyN29leGV0eSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/ai0YLvAS4kbTy/giphy.gif" # Ascending holy fish
    },
    "God ✨": {
        "value": 1000000,
        "species": ["The Legendary Kraken 🦑", "Poseidon's Goldfish 🔱"],
        "gif": "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdnhjdTljdTZtYXVvMTA0Y3p6N2NpYmxhZzUxamJlNTN3YzEyazNoZSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/NWqFfIIxiJyAE/giphy.gif" # Galaxy spinning fish
    }
}

# Automatically extract lists for our RNG roller
FISH_TIERS = list(FISH_DATA.keys())
FISH_WEIGHTS = [35, 25, 15, 10, 8, 5, 1.5, 0.4, 0.09, 0.01]

# Automatically build a flat lookup dictionary for inventory.py to check values
FISH_VALUES = {}
for tier, info in FISH_DATA.items():
    for fish in info["species"]:
        FISH_VALUES[fish] = info["value"]



class DatabaseManager:
    def __init__(self, db_name="fishing_game.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.init_market() # Initialize market prices on startup if missing

    def create_tables(self):
        # Existing tables...
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                cash INTEGER DEFAULT 0
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                user_id TEXT,
                fish_tier TEXT,
                quantity INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, fish_tier)
            )
        ''')
        # NEW TABLE: Tracks the live market price of each tier
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS market (
                tier_name TEXT PRIMARY KEY,
                current_price INTEGER
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS server_settings (
                guild_id TEXT PRIMARY KEY,
                news_channel_id TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS karma (
                user_id TEXT,
                fish_tier TEXT,
                karma_points INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, fish_tier)
            )
        ''')
        self.conn.commit()
        self.conn.commit()

    def init_market(self):
        # If the market table is empty, populate it with base values from FISH_DATA
        self.cursor.execute("SELECT COUNT(*) FROM market")
        if self.cursor.fetchone()[0] == 0:
            for tier, info in FISH_DATA.items():
                self.cursor.execute(
                    "INSERT INTO market (tier_name, current_price) VALUES (?, ?)",
                    (tier, info["value"])
                )
            self.conn.commit()

    def add_fish(self, user_id: str, username: str, fish_tier: str, value: int):
        # 1. Ensure player exists in DB (and update their username if they changed it)
        self.cursor.execute('''
            INSERT INTO players (user_id, username) 
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE SET username = excluded.username
        ''', (user_id, username))
        
        # 2. Add 1 to their specific fish inventory
        self.cursor.execute('''
            INSERT INTO inventory (user_id, fish_tier, quantity) 
            VALUES(?, ?, 1) ON CONFLICT(user_id, fish_tier) DO UPDATE SET quantity = quantity + 1
        ''', (user_id, fish_tier))
        
        # 3. Add the fish's value to their total net worth (using the cash column for now)
        self.cursor.execute('UPDATE players SET cash = cash + ? WHERE user_id = ?', (value, user_id))
        self.conn.commit()

    def get_top_players(self, limit: int = 5):
        # Grabs the top players sorted by their cash/net worth
        self.cursor.execute('SELECT username, cash FROM players ORDER BY cash DESC LIMIT ?', (limit,))
        return self.cursor.fetchall()
    
    def get_inventory(self, user_id: str):
        # Grabs all fish the user owns, sorted by amount
        self.cursor.execute('''
            SELECT fish_tier, quantity FROM inventory 
            WHERE user_id = ? AND quantity > 0 
            ORDER BY quantity DESC
        ''', (user_id,))
        return self.cursor.fetchall()
    
    def get_market_prices(self):
        self.cursor.execute("SELECT tier_name, current_price FROM market")
        return self.cursor.fetchall()

    def update_market_price(self, tier_name, new_price):
        self.cursor.execute(
            "UPDATE market SET current_price = ? WHERE tier_name = ?",
            (new_price, tier_name)
        )
        self.conn.commit()

    def sell_fish_db(self, user_id, username, tier_name, quantity, total_payout):
        # 1. Safely add cash and create profile if missing
        self.cursor.execute(
            """
            INSERT INTO players (user_id, username, cash)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET cash = cash + ?
            """,
            (user_id, username, total_payout, total_payout),
        )

        # 2. Safely create inventory row if missing
        self.cursor.execute(
            """
            INSERT INTO inventory (user_id, fish_tier, quantity)
            VALUES (?, ?, 0)
            ON CONFLICT(user_id, fish_tier) DO NOTHING
            """,
            (user_id, tier_name),
        )

        # 3. Remove the sold fish
        self.cursor.execute(
            """
            UPDATE inventory
            SET quantity = quantity - ?
            WHERE user_id = ? AND fish_tier = ?
            """,
            (quantity, user_id, tier_name),
        )

        self.conn.commit()
    
    def sell_all_fish_db(self, user_id, username, total_payout):
        # 1. Safely give the player their massive payout
        self.cursor.execute(
            """
            INSERT INTO players (user_id, username, cash)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET cash = cash + ?
            """,
            (user_id, username, total_payout, total_payout),
        )

        # 2. Wipe their entire inventory back to 0
        self.cursor.execute(
            """
            UPDATE inventory
            SET quantity = 0
            WHERE user_id = ?
            """,
            (user_id,),
        )

        self.conn.commit()

    def execute_sell(self, user_id, fish_species_list, tier_name, total_payout, price_drop):
        # 1. Add cash to the player (and create player profile if missing)
        self.cursor.execute('''
            INSERT INTO players (user_id, cash) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET cash = cash + ?
        ''', (user_id, total_payout, total_payout))
        
        # 2. Zero out the quantities of these specific fish for this user
        for fish_name in fish_species_list:
            self.cursor.execute(
                "UPDATE inventory SET quantity = 0 WHERE user_id = ? AND fish_tier = ?",
                (user_id, fish_name)
            )
            
        # 3. 🛡️ THE FIX: Pull the real base price value from python
        base_price = FISH_DATA[tier_name]["value"]
        hard_floor = int(base_price * 0.4)

        # 4. Safely drop the price without letting it sink past the hard floor
        self.cursor.execute('''
            UPDATE market 
            SET current_price = CASE 
                WHEN (current_price - ?) < ? THEN ? 
                ELSE (current_price - ?) 
            END 
            WHERE tier_name = ?
        ''', (price_drop, hard_floor, hard_floor, price_drop, tier_name))
        
        self.conn.commit()

    def set_news_channel(self, guild_id, channel_id):
        self.cursor.execute('''
            INSERT INTO server_settings (guild_id, news_channel_id) 
            VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET news_channel_id = ?
        ''', (guild_id, channel_id, channel_id))
        self.conn.commit()

    def get_all_news_channels(self):
        self.cursor.execute("SELECT news_channel_id FROM server_settings")
        return [row[0] for row in self.cursor.fetchall()]

    def get_player_karma(self, user_id):
        self.cursor.execute("SELECT fish_tier, karma_points FROM karma WHERE user_id = ?", (user_id,))
        return self.cursor.fetchall()

    def add_karma_and_clear_inventory(self, user_id, karma_updates):
        """
        karma_updates is a list of tuples: (user_id, tier_name, points, points)
        """
        # 1. Clear player's inventory completely
        self.cursor.execute("DELETE FROM inventory WHERE user_id = ?", (user_id,))
        
        # 2. Add karma points (Upsert logic)
        for _, tier, points in karma_updates:
            self.cursor.execute('''
                INSERT INTO karma (user_id, fish_tier, karma_points)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, fish_tier) 
                DO UPDATE SET karma_points = karma_points + ?
            ''', (user_id, tier, points, points))
            
        self.conn.commit()

    def execute_buy(self, user_id, username, fish_name, tier_name, total_cost, price_bump):
        # 1. Deduct cash from the player
        self.cursor.execute(
            """
            UPDATE players 
            SET cash = cash - ? 
            WHERE user_id = ?
            """,
            (total_cost, user_id)
        )

        # 2. Add the bought fish to their inventory (UPSERT safe)
        self.cursor.execute(
            """
            INSERT INTO inventory (user_id, fish_tier, quantity)
            VALUES (?, ?, 1)
            ON CONFLICT(user_id, fish_tier) DO UPDATE SET quantity = quantity + 1
            """,
            (user_id, fish_name) # Note: If your inventory tracks species name, pass fish_name here
        )

        # 3. Drive the market price UP
        self.cursor.execute(
            """
            UPDATE market 
            SET price = price + ? 
            WHERE fish_tier = ?
            """,
            (price_bump, tier_name)
        )

        # Enforce the upper price ceiling (2.5x base price max, mirroring your loop)
        # We handle this inside the app code right before saving, or let the market loop clip it later.
        self.conn.commit()
