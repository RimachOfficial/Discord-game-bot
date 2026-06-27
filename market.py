import discord
from discord import app_commands
from discord.ext import commands, tasks
import random
from database import FISH_DATA

class MarketCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.update_prices.start() # Starts the background simulation loop

    def cog_unload(self):
        self.update_prices.cancel() # Cleans up if the bot restarts

    # Background task: Simulates natural market fluctuations every 30 minutes
    @tasks.loop(minutes=30.0)
    async def update_prices(self):
        current_prices = self.db.get_market_prices()
        for tier, current_price in current_prices:
            base_price = FISH_DATA[tier]["value"]
            
            # Solo-friendly fluctuation: shift price randomly by -15% to +20%
            change_percent = random.uniform(-0.15, 0.20)
            new_price = int(current_price * (1 + change_percent))
            
            # Safety caps: don't let prices drop below 50% of base value, or exceed 250%
            new_price = max(int(base_price * 0.5), min(new_price, int(base_price * 2.5)))
            
            self.db.update_market_price(tier, new_price)

    # 🛑 THE FIX: This forces the loop to wait until the bot is fully online!
    @update_prices.before_loop
    async def before_update_prices(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="market", description="Check current fish stock market prices!")
    async def market(self, interaction: discord.Interaction):
        await interaction.response.defer()
        prices = self.db.get_market_prices()
        
        embed = discord.Embed(title="📈 Live Fish Stock Market", color=discord.Color.gold())
        embed.description = "Prices shift naturally every 30 minutes. Large player dumps will crash a tier's value!"
        
        for tier, price in prices:
            base = FISH_DATA[tier]["value"]
            # Visual trend indicator
            trend = "🟢 ↗️" if price > base else ("🔴 ↘️" if price < base else "⚪ ➡️")
            embed.add_field(
                name=tier,
                value=f"Current Price: **${price:,}**\nBase: `${base:,}`\nTrend: {trend}",
                inline=True
            )
            
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="sell", description="Sell an entire tier of fish from your inventory!")
    @app_commands.choices(tier=[
        app_commands.Choice(name="Bozo ⚪", value="Bozo ⚪"),
        app_commands.Choice(name="Common 🔘", value="Common 🔘"),
        app_commands.Choice(name="Uncommon 🔵", value="Uncommon 🔵"),
        app_commands.Choice(name="El Bozo 🟢", value="El Bozo 🟢"),
        app_commands.Choice(name="Your Mother 🟣", value="Your Mother 🟣"),
        app_commands.Choice(name="Legendary 🟡", value="Legendary 🟡"),
        app_commands.Choice(name="Rimach 🔴", value="Rimach 🔴"),
        app_commands.Choice(name="Gay 🌈", value="Gay 🌈"),
        app_commands.Choice(name="Divine ⚪🟣", value="Divine ⚪🟣"),
        app_commands.Choice(name="God ✨", value="God ✨")
    ])
    async def sell(self, interaction: discord.Interaction, tier: app_commands.Choice[str]):
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        chosen_tier = tier.value
        
        # 1. Get current market price for this tier
        prices = dict(self.db.get_market_prices())
        current_unit_price = prices.get(chosen_tier, FISH_DATA[chosen_tier]["value"])
        
        # 2. Check what matching fish the user actually owns
        user_inv = self.db.get_inventory(user_id)
        target_species = FISH_DATA[chosen_tier]["species"]
        
        total_fish_to_sell = 0
        fish_to_reset = []
        
        for fish_name, quantity in user_inv:
            if fish_name in target_species and quantity > 0:
                total_fish_to_sell += quantity
                fish_to_reset.append(fish_name)
                
        # Guard clause if they try to sell nothing
        if total_fish_to_sell == 0:
            await interaction.followup.send(f"🪣 You don't have any fish from the **{chosen_tier}** tier to sell!")
            return
            
        # 3. Calculate payout and market impact
        total_payout = total_fish_to_sell * current_unit_price
        base_price = FISH_DATA[chosen_tier]["value"]
        
        # Price drops by 0.5% of its BASE value for every single fish dumped
        price_drop = int(total_fish_to_sell * (base_price * 0.005))
        
        # 4. Commit transaction to database
        self.db.execute_sell(user_id, fish_to_reset, chosen_tier, total_payout, price_drop)
        
        # 5. Build dynamic breakdown message
        new_prices = dict(self.db.get_market_prices())
        updated_price = new_prices.get(chosen_tier, current_unit_price)
        
        embed = discord.Embed(title="💰 Transaction Complete!", color=discord.Color.green())
        embed.description = (
            f"You liquidated **x{total_fish_to_sell}** fish from the **{chosen_tier}** tier.\n"
            f"💵 **Earned:** `+${total_payout:,}`\n\n"
            f"📉 **Market Impact:** The massive supply drop caused the value of {chosen_tier} "
            f"to tumble from **${current_unit_price:,}** down to **${updated_price:,}**!"
        )
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MarketCommands(bot))