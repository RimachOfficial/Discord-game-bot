import sys
import os
from pathlib import Path

# Ensure the 'code' directory is on the Python path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

import discord
from dotenv import load_dotenv
from discord.ext import commands
from database import DatabaseManager
import io


# 1. Load the secret token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 2. Subclass the Bot to manage startup tasks cleanly
class BipbobBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.db = DatabaseManager()

    # setup_hook runs automatically before the bot logs in
    async def setup_hook(self):
        # Load the commands.py file (do not include the .py extension here)
        await self.load_extension("commands")
        print("✅ Loaded extension: commands")
        await self.load_extension("inventory")
        print("✅ Loaded extension: inventory")
        await self.load_extension("market")
        print("✅ Loaded extension: market")
        await self.load_extension("karma_system") # Add this line!
        print("✅ Loaded extension: karma_system")
        await self.load_extension("shop")
        print("✅ Loaded extension: shop")
        await self.load_extension("crew")
        print("✅ Loaded extension: Crews")
        # Sync the slash commands globally
        try:
            synced = await self.tree.sync()
            print(f"🔄 Synced {len(synced)} extensions")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

    async def on_ready(self):
        print("----------------------------------------")
        print(f"🎉 Success! {self.user.name} is now online!")
        print("----------------------------------------")



# 3. Initialize and run the bot
bot = BipbobBot()

if __name__ == "__main__":
    bot.run(TOKEN)