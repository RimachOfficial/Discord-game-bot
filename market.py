import discord
from discord import app_commands
from discord.ext import commands, tasks
from constants import FISH_DATA, FISH_TO_TIER
from engines import market_engine

minutes_of_update=5.0

class MarketCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.update_prices.start() 

    def cog_unload(self):
        self.update_prices.cancel() 

    @tasks.loop(minutes=minutes_of_update)
    async def update_prices(self):
        current_prices = self.db.get_market_prices()
        
        # 1. Normal Market Fluctuations
        new_prices = market_engine.calculate_market_fluctuations(current_prices)
        self.db.update_market_prices_bulk(new_prices)

        # 2. Market Shocks (Random News Events)
        shock_event = market_engine.generate_market_shock()
        if shock_event:
            print("🎲 Market loop ticked: Triggering a breaking news event...")
            
            updated_prices = dict(self.db.get_market_prices())
            affected_tier = shock_event["tier"]
            
            if affected_tier in updated_prices:
                shock_price = float(updated_prices[affected_tier]) * float(shock_event["mult"])
                self.db.update_market_price(affected_tier, shock_price)
                
                channel_ids = self.db.get_all_news_channels()
                print(f"📡 Found {len(channel_ids)} registered news channel(s) in database.")
                
                embed = discord.Embed(
                    title="📰 Breaking Market News!", 
                    description=shock_event["msg"], 
                    color=discord.Color.red()
                )
                embed.set_footer(text=f"The value of {affected_tier} just drastically shifted!")

                for cid in channel_ids:
                    channel = self.bot.get_channel(int(cid))
                    if channel:
                        try:
                            await channel.send(embed=embed)
                            print(f"✅ Successfully sent news alert to channel ID: {cid}")
                        except discord.Forbidden:
                            print(f"❌ Failed to send: Lacking permissions in channel ID: {cid}")
                    else:
                        print(f"⚠️ Channel ID {cid} could not be found by the bot cache.")

    @update_prices.before_loop
    async def before_update_prices(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="market", description="Check current fish stock market prices!")
    async def market(self, interaction: discord.Interaction):
        await interaction.response.defer()
        prices = self.db.get_market_prices()
        
        embed = discord.Embed(title="📈 Live Fish Stock Market", color=discord.Color.gold())
        embed.description = f"Prices shift naturally every {minutes_of_update} minutes. Large player dumps will crash a tier's value!"
        
        for tier, price in prices:
            base = FISH_DATA[tier]["value"]
            trend = "🟢 ↗️" if price > base else ("🔴 ↘️" if price < base else "⚪ ➡️")
            
            # Formatter layer supporting cosmic numbers and standard whole figures smoothly
            price_display = f"{price:,.2f}" if price < 1e15 else f"{price:.4e}"
            
            embed.add_field(
                name=tier,
                value=f"Current Price: **${price_display}**\nBase: `${base:,}`\nTrend: {trend}",
                inline=True
            )
            
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="sell", description="Sell an entire tier of fish from your inventory!")
    @app_commands.choices(tier=[app_commands.Choice(name=t, value=t) for t in FISH_DATA.keys()])
    async def sell(self, interaction: discord.Interaction, tier: app_commands.Choice[str]):
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        chosen_tier = tier.value
        
        prices = dict(self.db.get_market_prices())
        current_unit_price = prices.get(chosen_tier, FISH_DATA[chosen_tier]["value"])
        
        user_inv = self.db.get_inventory(user_id)
        target_species = FISH_DATA[chosen_tier]["species"]
        
        total_fish_to_sell = 0
        fish_to_reset = []
        
        for fish_name, quantity in user_inv:
            if fish_name in target_species and quantity > 0:
                total_fish_to_sell += quantity
                fish_to_reset.append(fish_name)
                
        if total_fish_to_sell == 0:
            await interaction.followup.send(f"🪣 You don't have any fish from the **{chosen_tier}** tier to sell!")
            return
            
        # Execute Domain Logic
        total_payout, price_drop, new_price = market_engine.calculate_sell_impact(chosen_tier, total_fish_to_sell, current_unit_price)
        
        # Save to DB
        self.db.update_player_cash(user_id, total_payout, interaction.user.name)
        self.db.clear_specific_fish(user_id, fish_to_reset)
        self.db.update_market_price(chosen_tier, new_price)
        
        embed = discord.Embed(title="💰 Transaction Complete!", color=discord.Color.green())
        payout_display = f"{total_payout:,.2f}" if total_payout < 1e15 else f"{total_payout:.4e}"
        old_price_display = f"{current_unit_price:,.2f}" if current_unit_price < 1e15 else f"{current_unit_price:.4e}"
        new_price_display = f"{new_price:,.2f}" if new_price < 1e15 else f"{new_price:.4e}"

        embed.description = (
            f"You liquidated **x{total_fish_to_sell:,}** fish from the **{chosen_tier}** tier.\n"
            f"💵 **Earned:** `+${payout_display}`\n\n"
            f"📉 **Market Impact:** The massive supply drop caused the value of {chosen_tier} "
            f"to tumble from **${old_price_display}** down to **${new_price_display}**!"
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="setnews", description="Set the channel for market breaking news! (Admins only)")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setnews(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.db.set_news_channel(str(interaction.guild_id), str(channel.id))
        embed = discord.Embed(
            title="📰 News Channel Set!", 
            description=f"Market crashes and spikes will now be broadcasted in {channel.mention}.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buy", description="Buy a fish directly from the market and drive its value up!")
    @app_commands.choices(tier=[app_commands.Choice(name=t, value=t) for t in FISH_DATA.keys()])
    async def buy(self, interaction: discord.Interaction, tier: app_commands.Choice[str], quantity: int = 1):
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        chosen_tier = tier.value
        
        if quantity <= 0:
            await interaction.followup.send("❌ You must buy at least 1 fish!")
            return

        prices = dict(self.db.get_market_prices())
        current_unit_price = prices.get(chosen_tier, FISH_DATA[chosen_tier]["value"])
        player_cash = self.db.get_player_balance(user_id)
        
        has_credit_card = (
            self.db.get_item_count(user_id, "💳 Mommy's Credit Card") > 0
            and self.db.get_buff(user_id, "item_disabled:💳 Mommy's Credit Card") is None
        )
        
        # Domain Logic
        impact = market_engine.calculate_buy_impact(chosen_tier, quantity, current_unit_price, player_cash, has_credit_card)
        
        if not impact["success"]:
            await interaction.followup.send(f"💸 You don't have enough cash! You need `${impact['shortfall']:,}` more to buy **x{quantity} {chosen_tier}**.")
            return

        total_cost = impact["total_cost"]
        new_price = impact["new_price"]
        
        # Save to DB
        self.db.update_player_cash(user_id, -total_cost)
        import random
        import math
        from collections import Counter
        
        species_list = FISH_DATA[chosen_tier]["species"]
        species_counts = {}

        # 1. If quantity is huge, use instant O(1) math instead of allocating gigabytes of memory
        if quantity > 100000:
            remaining_qty = quantity
            for i in range(len(species_list) - 1):
                p = 1 / (len(species_list) - i)
                mu = remaining_qty * p
                sigma = math.sqrt(remaining_qty * p * (1 - p))
                count = max(0, min(remaining_qty, int(random.gauss(mu, sigma))))
                species_counts[species_list[i]] = count
                remaining_qty -= count
            species_counts[species_list[-1]] = remaining_qty
        else:
            # Fast normal generation for smaller regular purchases
            bought_species = random.choices(species_list, k=quantity)
            species_counts = Counter(bought_species)
        
        # 2. Update the database using the compressed counts
        for species_name, count in species_counts.items():
            if count <= 0: continue
            self.db.cursor.execute(
                """
                INSERT INTO inventory (user_id, fish_tier, quantity) VALUES (?, ?, ?)
                ON CONFLICT(user_id, fish_tier) DO UPDATE SET quantity = quantity + ?
                """,
                (user_id, species_name, count, count)
            )
        self.db.conn.commit()
        self.db.update_market_price(chosen_tier, new_price)

        embed = discord.Embed(title="🛒 Market Purchase Complete!", color=discord.Color.gold())
        cost_display = f"{total_cost:,.2f}" if total_cost < 1e15 else f"{total_cost:.4e}"
        old_price_display = f"{current_unit_price:,.2f}" if current_unit_price < 1e15 else f"{current_unit_price:.4e}"
        new_price_display = f"{new_price:,.2f}" if new_price < 1e15 else f"{new_price:.4e}"

        embed.description = (
            f"You bought **x{quantity:,}** fish from the **{chosen_tier}** tier.\n"
            f"💸 **Total Spent:** `-${cost_display}`\n\n"
            f"📈 **Market Impact:** Your massive order caused the value of {chosen_tier} "
            f"to skyrocket from **${old_price_display}** up to **${new_price_display}**!"
        )
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MarketCommands(bot))