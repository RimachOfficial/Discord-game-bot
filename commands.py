import discord
from discord import app_commands
from discord.ext import commands
import random
from database import FISH_TIERS
from database import FISH_VALUES
from database import FISH_WEIGHTS
from database import FISH_DATA

class FishingCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @app_commands.command(name="fish", description="Cast your line into the water!")
    @app_commands.checks.cooldown(30, 30.0, key=lambda i: i.user.id)
    async def fish(self, interaction: discord.Interaction):
        # 🛡️ Defer the response instantly so the command doesn't lag out or timeout
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        
        # --- ✨ KARMA LUCK MATH ✨ ---
        # 1. Fetch the user's accumulated Karma from the database
        raw_karma = dict(self.db.get_player_karma(user_id))
        
        # 2. Build personalized, dynamic drop weights based on their Karma!
        dynamic_weights = []
        for i, tier in enumerate(FISH_TIERS):
            base_weight = FISH_WEIGHTS[i]
            points = raw_karma.get(tier, 0)
            
            # Math: Every 100 points = +1% to the base weight
            luck_bonus_pct = points / 100.0 
            adjusted_weight = base_weight * (1 + (luck_bonus_pct / 100.0))
            
            dynamic_weights.append(adjusted_weight)
        
        # 3. Roll for the fish using their NEW SUPERCHARGED weights
        tier = random.choices(FISH_TIERS, weights=dynamic_weights, k=1)[0]
        fish_name = random.choice(FISH_DATA[tier]["species"])
        gif_url = FISH_DATA[tier]["gif"]
        
        # --- 🎲 EXACT DROP CHANCE MATH ---
        total_weight_sum = sum(dynamic_weights)
        total_base_weight_sum = sum(FISH_WEIGHTS) # Get the global base total
        
        tier_index = FISH_TIERS.index(tier)
        my_tier_weight = dynamic_weights[tier_index]
        base_tier_weight = FISH_WEIGHTS[tier_index]
        
        species_in_tier = len(FISH_DATA[tier]["species"])
        
        # 1. Calculate Player's Karma Probability
        tier_probability = my_tier_weight / total_weight_sum
        exact_catch_pct = (tier_probability / species_in_tier) * 100
        
        # 2. Calculate Global Base Probability
        base_tier_probability = base_tier_weight / total_base_weight_sum
        base_catch_pct = (base_tier_probability / species_in_tier) * 100
        # ---------------------------------
        
        # 4. Get Live Market Prices vs Base Values
        market_prices = dict(self.db.get_market_prices())
        base_price = FISH_DATA[tier]["value"]
        current_market_price = market_prices.get(tier, base_price)
        
        # 5. Calculate trend arrow visual
        if current_market_price > base_price:
            trend = "🟢 Peak (+)"
        elif current_market_price < base_price:
            trend = "🔴 Crashed (-)"
        else:
            trend = "⚪ Stable"
        
        # 6. Save to database 
        self.db.add_fish(user_id, interaction.user.name, fish_name, tier)
        
        # 7. Create the updated Embed displaying both drop chances!
        embed = discord.Embed(
            title="🎣 You cast your line...",
            description=(
                f"And reeled in a **{fish_name}**!\n\n"
                f"✨ **Tier:** {tier}\n"
                f"📊 **Base Chance:** `{base_catch_pct:.3f}%`\n"
                f"🎲 **Your Chance:** `{exact_catch_pct:.3f}%`"
            ),
            color=discord.Color.teal()
        )
        
        embed.add_field(name="💵 Live Market Price", value=f"`${current_market_price:,}` ({trend})", inline=True)
        embed.add_field(name="🏛️ Base Value", value=f"`${base_price:,}`", inline=True)
        
        # Injects the meme GIF directly into the embed layout
        embed.set_image(url=gif_url)
        
        # 8. Send the embed response
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="leaderboard", description="Check the wealthiest fishermen in the server!")
    async def leaderboard(self, interaction: discord.Interaction):
        # 1. Fetch real data from the DB
        top_players = self.db.get_top_players(5)
        
        if not top_players:
            await interaction.response.send_message("The waters are empty! Nobody has fished yet.")
            return
            
        embed = discord.Embed(title="🏆 Wealthiest Fishermen 🏆", color=discord.Color.gold())
        
        # 2. Loop through DB rows instead of fake data
        for index, (name, wealth) in enumerate(top_players, start=1):
            embed.add_field(name=f"#{index} {name}", value=f"💰 ${wealth:,}", inline=False)
            
        await interaction.response.send_message(embed=embed)

    # This automatically catches errors in this specific Cog
    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            # ephemeral=True means only the user who spammed the command can see this warning
            await interaction.response.send_message(
                f"⏳ The fish got spooked! Wait {error.retry_after:.1f} seconds before casting again.", 
                ephemeral=True
            )
        else:
            # If it's a different error, just print it to the terminal
            print(f"Error: {error}")

    @app_commands.command(name="chances", description="View your exact personalized fishing drop rates!")
    async def view_chances(self, interaction: discord.Interaction):
        # 🛡️ Defer the response instantly
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        
        # 1. Fetch Karma from the database
        raw_karma = dict(self.db.get_player_karma(user_id))
        
        # 2. Build the personalized dynamic weights
        dynamic_weights = []
        for i, tier in enumerate(FISH_TIERS):
            base_weight = FISH_WEIGHTS[i]
            points = raw_karma.get(tier, 0)
            
            # Math: Every 100 points = +1% to the base weight
            luck_bonus_pct = points / 100.0 
            adjusted_weight = base_weight * (1 + (luck_bonus_pct / 100.0))
            
            dynamic_weights.append(adjusted_weight)
            
        # 3. Calculate the total sums to figure out the true pie chart percentages
        total_weight_sum = sum(dynamic_weights)
        total_base_weight_sum = sum(FISH_WEIGHTS)
        
        # 4. Build a beautiful presentation embed
        embed = discord.Embed(
            title="🎲 Your Personal Catch Chances",
            description="Here are your exact tier drop rates based on your current Karma!",
            color=discord.Color.gold()
        )
        
        # 5. Loop through every tier to compare Base vs Personal chances
        for i, tier in enumerate(FISH_TIERS):
            # Calculate the Tier probabilities (not specific fish, just the whole tier)
            base_tier_probability = (FISH_WEIGHTS[i] / total_base_weight_sum) * 100
            my_tier_probability = (dynamic_weights[i] / total_weight_sum) * 100
            
            # Create a visual trend indicator to show the "Pie Effect"
            if my_tier_probability > base_tier_probability:
                trend = "🟢 ↑" # Karma boosted this tier
            elif my_tier_probability < base_tier_probability:
                trend = "🔴 ↓" # Pie effect squeezed this tier
            else:
                trend = "⚪ =" # Untouched
                
            embed.add_field(
                name=tier,
                value=(
                    f"**Base:** `{base_tier_probability:.3f}%`\n"
                    f"**Yours:** `{my_tier_probability:.3f}%` {trend}"
                ),
                inline=True
            )
            
        embed.set_footer(text="Release more fish using /free to boost your rare chances!")
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="sell_all", description="Liquidate your entire inventory to the live market!")
    async def sell_all(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = str(interaction.user.id)
        username = interaction.user.name
        
        # 1. Fetch inventory and market prices
        user_inv = self.db.get_inventory(user_id)
        market_prices = dict(self.db.get_market_prices())
        
        if not user_inv:
            await interaction.followup.send("🪣 Your inventory is already empty!")
            return

        # --- THE FIX: Create a mapping to find a fish's tier! ---
        species_to_tier = {}
        for tier_key, data in FISH_DATA.items():
            for species in data["species"]:
                species_to_tier[species] = tier_key
        # --------------------------------------------------------

        total_payout = 0
        total_fish_sold = 0
        
        # 2. Calculate the exact payout based on LIVE prices
        for fish_name, quantity in user_inv:
            if quantity > 0:
                # Find which tier this specific fish belongs to
                tier = species_to_tier.get(fish_name)
                
                # Safety check just in case an old deleted fish is in the DB
                if not tier:
                    continue 

                base_price = FISH_DATA[tier]["value"]
                current_price = market_prices.get(tier, base_price)
                
                total_payout += (current_price * quantity)
                total_fish_sold += quantity
                
        if total_fish_sold == 0:
            await interaction.followup.send("🪣 You don't have any fish to sell!")
            return

        # 3. Execute the database transaction
        self.db.sell_all_fish_db(user_id, username, total_payout)
        
        # 4. Build a satisfying receipt
        embed = discord.Embed(
            title="💰 Massive Payout!",
            description=f"You dumped **{total_fish_sold:,}** fish onto the market!",
            color=discord.Color.green()
        )
        embed.add_field(name="Total Cash Earned", value=f"`${total_payout:,}`", inline=False)
        embed.set_footer(text="Check your new balance with /balance")
        
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(FishingCommands(bot))