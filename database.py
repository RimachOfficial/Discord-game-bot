import sqlite3
import time

class DatabaseManager:
    def __init__(self, db_name="fishing_game.db"):
        self.conn = sqlite3.connect(db_name,check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.init_market()

    def create_tables(self):
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
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_items (
                user_id TEXT,
                item_name TEXT,
                quantity INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, item_name)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_buffs (
                user_id TEXT,
                buff_name TEXT,
                buff_value TEXT,
                expires_at REAL,
                PRIMARY KEY (user_id, buff_name)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tier_name TEXT,
                price REAL,
                timestamp REAL
            )           
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_crew (
                user_id TEXT,
                crew_name TEXT,
                level INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, crew_name)
            )
        ''')
        self.conn.commit()

    def init_market(self):
        from constants import FISH_DATA
        self.cursor.execute("SELECT COUNT(*) FROM market")
        if self.cursor.fetchone()[0] == 0:
            for tier, info in FISH_DATA.items():
                self.cursor.execute(
                    "INSERT INTO market (tier_name, current_price) VALUES (?, ?)",
                    (tier, info["value"])
                )
            self.conn.commit()

    def add_fish(self, user_id: str, username: str, fish_tier: str, tier: str):
        self.cursor.execute('''
            INSERT INTO players (user_id, username)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE SET username = excluded.username
        ''', (user_id, username))
        self.cursor.execute('''
            INSERT INTO inventory (user_id, fish_tier, quantity)
            VALUES(?, ?, 1) ON CONFLICT(user_id, fish_tier) DO UPDATE SET quantity = quantity + 1
        ''', (user_id, fish_tier))
        self.conn.commit()

    def add_fish_bulk(self, user_id: str, fishes: list[dict]):
        """Aggregates fish by name and does one upsert per unique species — never loops N times."""
        counts: dict[str, int] = {}
        for f in fishes:
            counts[f["name"]] = counts.get(f["name"], 0) + 1
        self.cursor.executemany('''
            INSERT INTO inventory (user_id, fish_tier, quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, fish_tier) DO UPDATE SET quantity = quantity + excluded.quantity
        ''', [(user_id, name, qty) for name, qty in counts.items()])
        self.conn.commit()

    def update_player_cash(self, user_id: str, amount: int, username: str = None):
        # 1. Fetch current balance first and force convert it to a float
        self.cursor.execute("SELECT cash FROM players WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        current_cash = float(result[0]) if (result and result[0] is not None) else 0.0

        # 2. Add the new amount using floating point math
        new_cash = current_cash + float(amount)

        # 3. Save the float back into the database
        if username:
            self.cursor.execute('''
                INSERT INTO players (user_id, username, cash) VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET cash = ?, username = excluded.username
            ''', (user_id, username, new_cash, new_cash))
        else:
            self.cursor.execute('''
                INSERT INTO players (user_id, cash) VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET cash = ?
            ''', (user_id, new_cash, new_cash))
        self.conn.commit()

    def get_top_players(self, limit: int = 5):
        self.cursor.execute('SELECT username, cash FROM players ORDER BY cash DESC LIMIT ?', (limit,))
        return self.cursor.fetchall()

    def get_inventory(self, user_id: str):
        self.cursor.execute('''
            SELECT fish_tier, quantity FROM inventory
            WHERE user_id = ? AND quantity > 0
            ORDER BY quantity DESC
        ''', (user_id,))
        return self.cursor.fetchall()

    def clear_inventory(self, user_id: str):
        self.cursor.execute("UPDATE inventory SET quantity = 0 WHERE user_id = ?", (user_id,))
        self.conn.commit()

    def clear_specific_fish(self, user_id: str, fish_names: list[str]):
        for fish_name in fish_names:
            self.cursor.execute(
                "UPDATE inventory SET quantity = 0 WHERE user_id = ? AND fish_tier = ?",
                (user_id, fish_name)
            )
        self.conn.commit()

    def get_market_prices(self):
        self.cursor.execute("SELECT tier_name, current_price FROM market")
        return self.cursor.fetchall()

    def update_market_price(self, tier_name: str, new_price: int):
        self.cursor.execute(
            "UPDATE market SET current_price = ? WHERE tier_name = ?",
            (new_price, tier_name)
        )
        self.conn.commit()

    def update_market_prices_bulk(self, new_prices: dict[str, int]):
        self.cursor.executemany(
            "UPDATE market SET current_price = ? WHERE tier_name = ?",
            [(price, tier) for tier, price in new_prices.items()]
        )
        self.conn.commit()

    def set_news_channel(self, guild_id: str, channel_id: str):
        self.cursor.execute('''
            INSERT INTO server_settings (guild_id, news_channel_id)
            VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET news_channel_id = ?
        ''', (guild_id, channel_id, channel_id))
        self.conn.commit()

    def get_all_news_channels(self):
        self.cursor.execute("SELECT news_channel_id FROM server_settings")
        return [row[0] for row in self.cursor.fetchall()]

    def get_player_karma(self, user_id: str):
        self.cursor.execute("SELECT fish_tier, karma_points FROM karma WHERE user_id = ?", (user_id,))
        return self.cursor.fetchall()

    def add_karma_points(self, user_id: str, karma_updates: list):
        # 1. Pull current user karma into a python dictionary of floats
        self.cursor.execute("SELECT fish_tier, karma_points FROM karma WHERE user_id = ?", (user_id,))
        existing_rows = self.cursor.fetchall()
        current_karma = {row[0]: float(row[1]) for row in existing_rows}

        # 2. Accumulate adjustments in memory
        for tier, points in karma_updates:
            current_karma[tier] = current_karma.get(tier, 0.0) + float(points)

        # 3. Save the results cleanly back into SQLite
        prepare_data = [
            (user_id, tier, total_points, total_points) 
            for tier, total_points in current_karma.items()
        ]

        self.cursor.executemany('''
            INSERT INTO karma (user_id, fish_tier, karma_points) VALUES (?, ?, ?)
            ON CONFLICT(user_id, fish_tier) DO UPDATE SET karma_points = ?
        ''', prepare_data)
        
        self.conn.commit()

    def deduct_karma_points(self, user_id: str, deductions: list[tuple[str, int]]):
        for tier, points in deductions:
            self.cursor.execute(
                "UPDATE karma SET karma_points = karma_points - ? WHERE user_id = ? AND fish_tier = ?",
                (points, user_id, tier)
            )
        self.conn.commit()

    def get_player_balance(self, user_id: str) -> float:
        self.cursor.execute("SELECT cash FROM players WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        # Force the return value to be a float so it can handle cosmic amounts safely
        return float(row[0]) if (row and row[0] is not None) else 0.0

    def get_item_count(self, user_id: str, item_name: str) -> int:
        self.cursor.execute("SELECT quantity FROM player_items WHERE user_id = ? AND item_name = ?", (user_id, item_name))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def consume_item(self, user_id: str, item_name: str, amount: int = 1) -> bool:
        current = self.get_item_count(user_id, item_name)
        if current < amount:
            return False
        if current == amount:
            self.cursor.execute("DELETE FROM player_items WHERE user_id = ? AND item_name = ?", (user_id, item_name))
        else:
            self.cursor.execute("UPDATE player_items SET quantity = quantity - ? WHERE user_id = ? AND item_name = ?", (amount, user_id, item_name))
        self.conn.commit()
        return True

    def set_buff(self, user_id: str, buff_name: str, value: str = "1", duration_seconds: int = 0):
        expires_at = time.time() + duration_seconds if duration_seconds > 0 else 0
        self.cursor.execute('''
            INSERT INTO player_buffs (user_id, buff_name, buff_value, expires_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, buff_name) DO UPDATE SET buff_value = excluded.buff_value, expires_at = excluded.expires_at
        ''', (user_id, buff_name, value, expires_at))
        self.conn.commit()

    def get_buff(self, user_id: str, buff_name: str):
        self.cursor.execute("SELECT buff_value, expires_at FROM player_buffs WHERE user_id = ? AND buff_name = ?", (user_id, buff_name))
        result = self.cursor.fetchone()
        if result:
            value, expires_at = result
            if expires_at > 0 and time.time() > expires_at:
                self.clear_buff(user_id, buff_name)
                return None
            return value
        return None

    def clear_buff(self, user_id: str, buff_name: str):
        self.cursor.execute("DELETE FROM player_buffs WHERE user_id = ? AND buff_name = ?", (user_id, buff_name))
        self.conn.commit()

    def add_item(self, user_id: str, item_name: str, quantity: int = 1):
        self.cursor.execute('''
            INSERT INTO player_items (user_id, item_name, quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, item_name) DO UPDATE SET quantity = quantity + ?
        ''', (user_id, item_name, quantity, quantity))
        self.conn.commit()

    def get_crew_level(self, user_id: str, crew_name: str) -> int:
        """Returns the current level of a specific crew member for a player."""
        self.cursor.execute(
            "SELECT level FROM player_crew WHERE user_id = ? AND crew_name = ?", 
            (user_id, crew_name)
        )
        row = self.cursor.fetchone()
        return row[0] if row else 0

    def set_crew_level(self, user_id: str, crew_name: str, level: int):
        """Saves or updates a crew member's level."""
        self.cursor.execute("""
            INSERT INTO player_crew (user_id, crew_name, level) 
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, crew_name) DO UPDATE SET level = excluded.level
        """, (user_id, crew_name, level))
        self.conn.commit()

    def get_all_active_crew(self):
        """Fetches all rows from the crew table to process passive payouts."""
        self.cursor.execute("SELECT user_id, crew_name, level FROM player_crew WHERE level > 0")
        return self.cursor.fetchall()


