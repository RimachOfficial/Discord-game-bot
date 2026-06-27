import discord
from discord import app_commands
from discord.ext import commands, tasks
import random
from database import FISH_DATA

minutes_of_update=5.0

class MarketCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.update_prices.start() # Starts the background simulation loop

    def cog_unload(self):
        self.update_prices.cancel() # Cleans up if the bot restarts

    # Background task: Simulates natural market fluctuations every 5 minutes
    @tasks.loop(minutes=minutes_of_update)
    async def update_prices(self):
        # 1. Normal Market Fluctuations
        current_prices = self.db.get_market_prices()
        for tier, current_price in current_prices:
            base_price = FISH_DATA[tier]["value"]
            
            change_percent = random.uniform(-0.15, 0.20)
            new_price = int(current_price * (1 + change_percent))
            new_price = max(int(base_price * 0.4), min(new_price, int(base_price * 2.5)))
            
            self.db.update_market_price(tier, new_price)

        # 2. 🚨 Market Shocks (Random News Events)
        # TEMPORARY FOR TESTING: Commenting out the 15% random chance so it triggers 100% of the time
        # if random.random() < 0.15: 
        if True:
            print("🎲 Market loop ticked: Triggering a guaranteed breaking news event...")
            event = random.choice([
                {"msg": "⚠️ **ANCHOVY INFLATION!** Low tier fish prices skyrocketed!", "tier": "Bozo ⚪", "mult": 1.8},
                {"msg": "🐋 **WHALE CONSERVATION ACT!** 'Your Mother' prices doubled!", "tier": "Your Mother 🟣", "mult": 2.0},
                {"msg": "📉 **CRYPTO CRASH!** Rich players panic-selling God fish!", "tier": "God ✨", "mult": 0.4},
                {"msg": "🦈 **SHARK WEEK!** Apex predators are in high demand!", "tier": "Rimach 🔴", "mult": 2.2},
                {"msg": "🦠 **RED TIDE OUTBREAK!** Common fish populations decimated, prices surging!", "tier": "Common 🔘", "mult": 1.6}
            ])
            
            updated_prices = dict(self.db.get_market_prices())
            affected_tier = event["tier"]
            
            if affected_tier in updated_prices:
                shock_price = int(updated_prices[affected_tier] * event["mult"])
                self.db.update_market_price(affected_tier, shock_price)
                
                channel_ids = self.db.get_all_news_channels()
                print(f"📡 Found {len(channel_ids)} registered news channel(s) in database.")
                
                embed = discord.Embed(
                    title="📰 Breaking Market News!", 
                    description=event["msg"], 
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
                        print(f"⚠️ Channel ID {cid} could not be found by the bot cache (is it in a different server?).")

    # 🛑 THE FIX: This forces the loop to wait until the bot is fully online!
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

    @app_commands.command(name="setnews", description="Set the channel for market breaking news! (Admins only)")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setnews(self, interaction: discord.Interaction, channel: discord.TextChannel):
        # Save the chosen channel to the database
        self.db.set_news_channel(str(interaction.guild_id), str(channel.id))
        
        embed = discord.Embed(
            title="📰 News Channel Set!", 
            description=f"Market crashes and spikes will now be broadcasted in {channel.mention}.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buy", description="Buy a fish directly from the market and drive its value up!")
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
    async def buy(self, interaction: discord.Interaction, tier: app_commands.Choice[str], quantity: int = 1):
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        username = interaction.user.name
        chosen_tier = tier.value
        
        if quantity <= 0:
            await interaction.followup.send("❌ You must buy at least 1 fish!")
            return

        # 1. Get current market price for this tier
        prices = dict(self.db.get_market_prices())
        current_unit_price = prices.get(chosen_tier, FISH_DATA[chosen_tier]["value"])
        total_cost = current_unit_price * quantity
        
        # 2. Check player's wallet balance
        self.db.cursor.execute("SELECT cash FROM players WHERE user_id = ?", (user_id,))
        player_row = self.db.cursor.fetchone()
        player_cash = player_row[0] if player_row else 0
        
        if player_cash < total_cost:
            shortfall = total_cost - player_cash
            await interaction.followup.send(f"💸 You don't have enough cash! You need `${shortfall:,}` more to buy **x{quantity} {chosen_tier}**.")
            return

        # 3. Calculate market impact (Price RISES by 0.5% of BASE value per fish bought)
        base_price = FISH_DATA[chosen_tier]["value"]
        price_bump = int(quantity * (base_price * 0.005))
        
        # Cap check: Make sure we don't exceed the absolute max market ceiling (2.5x base)
        max_allowed_price = int(base_price * 2.5)
        if current_unit_price + price_bump > max_allowed_price:
            price_bump = max(0, max_allowed_price - current_unit_price)

        # 4. Pick a random fish species from that tier to award them for each unit
        # (If they buy multiple, we can just pick one representative species to loop or log)
        chosen_species = random.choice(FISH_DATA[chosen_tier]["species"])

        # 5. Execute the buy sequence in the DB
        # If they buy more than 1, we can adjust your inventory loop, 
        # but for simplicity, this adds 'quantity' to their inventory row:
        for _ in range(quantity):
            # Pick a random species for every single fish bought
            fish_name = random.choice(FISH_DATA[chosen_tier]["species"])
            # We apply the price bump on the final execution step
            is_last = (_ == quantity - 1)
            actual_bump = price_bump if is_last else 0
            actual_cost = total_cost if is_last else 0
            
            # Internal tiny steps or single call adjustments:
            # To keep database execution super efficient, let's look at doing it directly:
            pass

        # Cleaner execution method to avoid multiple loops:
        # Let's execute the single query adjustments cleanly:
        # 1. Deduct cash from player
        self.db.cursor.execute("UPDATE players SET cash = cash - ? WHERE user_id = ?", (total_cost, user_id))
        
        # 2. Add to inventory
        for _ in range(quantity):
            fish_name = random.choice(FISH_DATA[chosen_tier]["species"])
            self.db.cursor.execute(
                """
                INSERT INTO inventory (user_id, fish_tier, quantity) VALUES (?, ?, 1)
                ON CONFLICT(user_id, fish_tier) DO UPDATE SET quantity = quantity + 1
                """,
                (user_id, fish_name)
            )
            
        # 3. Apply market price surge using your EXACT column names!
        self.db.cursor.execute(
            "UPDATE market SET current_price = current_price + ? WHERE tier_name = ?", 
            (price_bump, chosen_tier)
        )
        
        # 4. Commit all the changes at once
        self.db.conn.commit()

        # 5. Fetch updated price to show them the impact
        new_prices = dict(self.db.get_market_prices())
        updated_price = new_prices.get(chosen_tier, current_unit_price)

        # 6. Build transaction receipt
        embed = discord.Embed(title="🛒 Market Purchase Complete!", color=discord.Color.gold())
        embed.description = (
            f"You bought **x{quantity}** fish from the **{chosen_tier}** tier.\n"
            f"💸 **Total Spent:** `-${total_cost:,}`\n\n"
            f"📈 **Market Impact:** Your massive order caused the value of {chosen_tier} "
            f"to skyrocket from **${current_unit_price:,}** up to **${updated_price:,}**!"
        )
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MarketCommands(bot))