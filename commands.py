import discord
from discord import app_commands
from discord.ext import commands
from constants import FISH_DATA, FISH_TIERS, ITEM_CHOICES, FISH_TO_TIER # <-- Added FISH_TO_TIER
from engines import fishing_engine, economy_engine, item_engine
from discord.app_commands import Choice
import time
import engines.market_chart_engine # <-- Ensure the chart engine is imported

class FishingCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @app_commands.command(name="fish", description="Cast your line into the water!")
    @app_commands.checks.cooldown(10, 30.0, key=lambda i: i.user.id)
    async def fish(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = str(interaction.user.id)
        
        # 1. Fetch State
        raw_karma = dict(self.db.get_player_karma(user_id))
        has_mod_app = (
            self.db.get_item_count(user_id, "♻️ Discord Mod Application") > 0
            and self.db.get_buff(user_id, "item_disabled:♻️ Discord Mod Application") is None
        )
        has_bf_repellent = (
            self.db.get_item_count(user_id, '🧢 The "I Have a Boyfriend" Repellent') > 0
            and self.db.get_buff(user_id, 'item_disabled:🧢 The "I Have a Boyfriend" Repellent') is None
        )
        has_copium = self.db.get_buff(user_id, "copium_active") is not None
        
        gamer_girl_charges = self.db.get_buff(user_id, "gamer_girl_charges")
        has_gamer_girl = gamer_girl_charges is not None
        
        # 2. Execute Game Logic via Engine
        if has_copium:
            self.db.clear_buff(user_id, "copium_active")
            
        if has_gamer_girl:
            charges = int(gamer_girl_charges) - 1
            if charges > 0:
                self.db.set_buff(user_id, "gamer_girl_charges", str(charges))
            else:
                self.db.clear_buff(user_id, "gamer_girl_charges")

        result = fishing_engine.roll_fish(raw_karma, has_mod_app, has_bf_repellent, has_copium, has_gamer_girl)
        tier = result["tier"]
        fish_name = result["fish_name"]
        
        if has_copium and fish_name == "Old Boot":
            self.db.add_fish(user_id, interaction.user.name, fish_name, tier)
            await interaction.followup.send(f"🍼 **LMAOOO** {interaction.user.mention} ripped the Copium Inhaler, had a 50% chance for a God tier, and STILL caught an **Old Boot**. Point and laugh! 🫵😂")
            return
            
        # 3. Save to DB
        self.db.add_fish(user_id, interaction.user.name, fish_name, tier)
        
        # 4. Fetch Market Prices for Presentation
        market_prices = dict(self.db.get_market_prices())
        base_price = FISH_DATA[tier]["value"]
        current_market_price = market_prices.get(tier, base_price)
        
        trend = "🟢 Peak (+)" if current_market_price > base_price else "🔴 Crashed (-)" if current_market_price < base_price else "⚪ Stable"
        
        # 5. Build Presentation
        embed = discord.Embed(
            title="🎣 You cast your line...",
            description=(
                f"And reeled in a **{fish_name}**!\n\n"
                f"✨ **Tier:** {tier}\n"
                f"📊 **Base Chance:** `{result['base_catch_pct']:.2f}%`\n"
                f"🎲 **Your Chance:** `{result['exact_catch_pct']:.2f}%`"
            ),
            color=discord.Color.teal()
        )
        embed.add_field(name="💵 Live Market Price", value=f"`${current_market_price:.2f}` ({trend})", inline=True)
        embed.add_field(name="🏛️ Base Value", value=f"`${base_price:.2f}`", inline=True)
        embed.set_image(url=FISH_DATA[tier]["gif"])
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="leaderboard", description="Check the wealthiest fishermen in the server!")
    async def leaderboard(self, interaction: discord.Interaction):
        top_players = self.db.get_top_players(5)
        
        if not top_players:
            await interaction.response.send_message("The waters are empty! Nobody has fished yet.")
            return
            
        embed = discord.Embed(title="🏆 Wealthiest Fishermen 🏆", color=discord.Color.gold())
        for index, (name, wealth) in enumerate(top_players, start=1):
            embed.add_field(name=f"#{index} {name}", value=f"💰 ${wealth:.2f}", inline=False)
            
        await interaction.response.send_message(embed=embed)

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"⏳ The fish got spooked! Wait {error.retry_after:.1f} seconds before casting again.", 
                ephemeral=True
            )
        else:
            print(f"Error: {error}")

    @app_commands.command(name="balance", description="View your exact balance in $!")
    async def view_balance(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = str(interaction.user.id)
        
        wallet_cash = self.db.get_player_balance(user_id)
        user_inv = self.db.get_inventory(user_id)
        market_prices = dict(self.db.get_market_prices())

        portfolio = economy_engine.calculate_portfolio(wallet_cash, user_inv, market_prices)
        
        embed = discord.Embed(
            title="🎲 Live Financial Portfolio",
            description=f"Showing asset distribution for **{interaction.user.name}**",
            color=discord.Color.gold()
        )

        if portfolio['wallet_cash'] < 1e15:
            embed.add_field(name="💵 Liquid Cash", value=f"`${portfolio['wallet_cash']:,.2f}`", inline=True)
        else:
            embed.add_field(name="💵 Liquid Cash", value=f"`${portfolio['wallet_cash']:.2e}`", inline=True)
        if portfolio['inventory_value'] < 1e15:
            embed.add_field(name="🪣 Inventory Value", value=f"`${portfolio['inventory_value']:,.2f}`", inline=True)
        else:
            embed.add_field(name="🪣 Inventory Value", value=f"`${portfolio['inventory_value']:.2e}`", inline=True)
        if portfolio['total_net_worth'] < 1e15:
            embed.add_field(name="📊 Total Net Worth", value=f"**`${portfolio['total_net_worth']:,.2f}`**", inline=False)
        else:
            embed.add_field(name="📊 Total Net Worth", value=f"**`${portfolio['total_net_worth']:.2e}`**", inline=False)
        embed.set_footer(text=f"Financial Standing: {portfolio['status']}")
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="chances", description="View your exact personalized fishing drop rates!")
    async def view_chances(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = str(interaction.user.id)
        
        raw_karma = dict(self.db.get_player_karma(user_id))
        has_mod_app = (
            self.db.get_item_count(user_id, "♻️ Discord Mod Application") > 0
            and self.db.get_buff(user_id, "item_disabled:♻️ Discord Mod Application") is None
        )
        has_bf_repellent = (
            self.db.get_item_count(user_id, '🧢 The "I Have a Boyfriend" Repellent') > 0
            and self.db.get_buff(user_id, 'item_disabled:🧢 The "I Have a Boyfriend" Repellent') is None
        )
        has_copium = self.db.get_buff(user_id, "copium_active") is not None
        has_gamer_girl = self.db.get_buff(user_id, "gamer_girl_charges") is not None
        
        dynamic_weights = fishing_engine.calculate_dynamic_weights(raw_karma, has_mod_app, has_bf_repellent)
        
        embed = discord.Embed(
            title="🎲 Your Personal Catch Chances",
            description="Here are your exact tier drop rates based on your current Karma!",
            color=discord.Color.gold()
        )
        
        for i, tier in enumerate(FISH_TIERS):
            base_prob, my_prob = fishing_engine.calculate_catch_probabilities(tier, dynamic_weights, has_copium, has_gamer_girl)
            
            species_in_tier = len(FISH_DATA[tier]["species"])
            base_tier_prob = base_prob * species_in_tier
            my_tier_prob = my_prob * species_in_tier
            
            trend = "🟢 ↑" if my_tier_prob > base_tier_prob else "🔴 ↓" if my_tier_prob < base_tier_prob else "⚪ ="
                
            embed.add_field(
                name=tier,
                value=f"**Base:** `{base_tier_prob:.3f}%`\n**Yours:** `{my_tier_prob:.3f}%` {trend}",
                inline=True
            )
            
        embed.set_footer(text="Release more fish using /free to boost your rare chances!")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="sell_all", description="Liquidate your entire inventory to the live market!")
    async def sell_all(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = str(interaction.user.id)
        
        user_inv = self.db.get_inventory(user_id)
        market_prices = dict(self.db.get_market_prices())
        
        if not user_inv or sum(quantity for _, quantity in user_inv if quantity > 0) == 0:
            await interaction.followup.send("🪣 Your inventory is already empty!")
            return

        has_tax_evasion = (
            self.db.get_item_count(user_id, "📄 Tax Evasion Manual") > 0
            and self.db.get_buff(user_id, "item_disabled:📄 Tax Evasion Manual") is None
        )
        has_short_squeeze = self.db.get_buff(user_id, "short_squeeze") is not None
        
        from engines import market_engine
        result = market_engine.calculate_sell_all_impact(user_inv, market_prices, has_tax_evasion, has_short_squeeze)
        
        if result["total_fish_sold"] == 0:
            await interaction.followup.send("🪣 You don't have any fish to sell!")
            return
            
        if has_short_squeeze:
            self.db.clear_buff(user_id, "short_squeeze")
            
        self.db.update_player_cash(user_id, result["total_payout"], interaction.user.name)
        self.db.clear_inventory(user_id)
        
        # 🛡️ FIX NameError / Chart Tracking Logic: Identify exactly which tiers were handled
        sold_tiers = set()
        for fish_name, quantity in user_inv:
            if quantity > 0:
                tier_found = FISH_TO_TIER.get(fish_name)
                if tier_found:
                    sold_tiers.add(tier_found)

        new_prices = {}
        db_updates = {}
        for tier in sold_tiers:
            old_price = market_prices.get(tier, FISH_DATA[tier]["value"])
            drop = result["sanitized_drops"].get(tier, 0)
            final_calculated_price = max(0, old_price - drop)
            
            # If tax evasion is active, actual market price doesn't budge
            if has_tax_evasion:
                new_prices[tier] = old_price
            else:
                new_prices[tier] = final_calculated_price
                db_updates[tier] = final_calculated_price

        if db_updates:
            self.db.update_market_prices_bulk(db_updates)

        embed = discord.Embed(
            title="💰 Massive Payout!",
            description=f"You dumped **{result['total_fish_sold']:.2f}** fish onto the market!",
            color=discord.Color.green()
        )
        embed.add_field(name="Total Cash Earned", value=f"`${result['total_payout']:.2f}`", inline=False)
        
        if result["impacted_tiers_text"] and not has_tax_evasion:
            embed.add_field(name="📉 Market Damage Caused", value="\n".join(result["impacted_tiers_text"]), inline=False)
        elif has_tax_evasion:
            embed.add_field(name="💼 Offshore Accounts", value="Your Tax Evasion Manual prevented the market from crashing!", inline=False)
            
        embed.set_footer(text="Check your new balance with /balance")

        # Safely execute data metrics tracking across all liquidated items
        now = time.time()
        for tier, price in new_prices.items():
            self.db.cursor.execute(
                "INSERT INTO market_history (tier_name, price, timestamp) VALUES (?, ?, ?)",
                (tier, float(price), now)
            )
        self.db.conn.commit()
        
        print("📊 Executing chart generation routine via mass sale event...")
        try:
            engines.market_chart_engine.generate_and_save_market_chart(self.db)
            print("✅ market_trend.png successfully updated on disk!")
        except Exception as e:
            print(f"❌ Chart Engine generation error: {e}")

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="items", description="Inspect all the unhinged items coming to the game!")
    async def items(self, interaction: discord.Interaction):
        await interaction.response.defer()
        from constants import ITEM_CATALOG
        
        embed = discord.Embed(
            title="💎 THE BLACK MARKET EXCLUSIVE",
            description="Welcome to the underground. Here is the catalog of highly illegal, economy-ruining assets.\n", 
            color=discord.Color.purple()
        )
        embed.set_author(name=f"Access Granted: {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        
        for category, items in ITEM_CATALOG.items():
            field_text = ""
            for item_name, details in items.items():
                field_text += f"**{item_name}** `[{details['type']}]`\n> *{details['desc']}*\n\n"
            embed.add_field(name=f"{category.upper()}", value=field_text, inline=False)

        embed.set_footer(text="STATUS: SHOP SYSTEMS CURRENTLY OFFLINE")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="give_item", description="[ADMIN] Spawn a Black Market item for testing.")
    @app_commands.default_permissions(administrator=True)
    @app_commands.choices(item_name=ITEM_CHOICES)
    async def give_item(self, interaction: discord.Interaction, target: discord.Member, item_name: Choice[str], quantity: int = 1):
        user_id = str(target.id)
        self.db.add_item(user_id, item_name.value, quantity)
        await interaction.response.send_message(f"✅ Successfully spawned **{quantity}x {item_name.value}** into {target.mention}'s inventory.", ephemeral=True)

    @app_commands.command(name="use", description="Use a consumable Black Market item!")
    @app_commands.choices(item_name=ITEM_CHOICES)
    async def use_item(self, interaction: discord.Interaction, item_name: Choice[str]):
        user_id = str(interaction.user.id)
        actual_item_name = item_name.value 
        
        # 1. Protect Passive Items from being eaten
        valid_consumables = [
            "🍼 Copium Inhaler", 
            "📱 Bogdanoff’s Burner Phone", 
            "🧼 Gamer Girl Bathwater", 
            "🔋 Throw a Car Battery in the Ocean"
        ]
        
        if actual_item_name not in valid_consumables:
            await interaction.response.send_message(
                f"ℹ️ **{actual_item_name}** is a **Passive Item**! You don't need to activate it. "
                f"Its effects are automatically running in the background as long as it's in your inventory.", 
                ephemeral=True
            )
            return

        # 2. Check inventory and consume only if it's an active consumable
        if not self.db.consume_item(user_id, actual_item_name):
            await interaction.response.send_message(f"❌ You don't have **{actual_item_name}** in your inventory, bozo.", ephemeral=True)
            return

        # 3. Execute active item logic
        if actual_item_name == "🍼 Copium Inhaler":
            self.db.set_buff(user_id, "copium_active", "1")
            await interaction.response.send_message("🍼 *huffff* You ripped the Copium Inhaler! Your next `/fish` has a massively boosted chance for `God ✨` tier.")

        elif actual_item_name == "📱 Bogdanoff’s Burner Phone":
            self.db.set_buff(user_id, "short_squeeze", "1")
            await interaction.response.send_message("📱 *\"Dump eet.\"* Your next `/sell_all` will trigger a MASSIVE 3x market crash on everything you sell, ruining the economy!")
            
        elif actual_item_name == "🧼 Gamer Girl Bathwater":
            self.db.set_buff(user_id, "gamer_girl_charges", "3")
            await interaction.response.send_message("🧼 *glug glug* You drank the Bathwater! Your next 3 catches are guaranteed to be from `Your Mother 🟣` or `Gay 🌈`.")
            
        elif actual_item_name == "🔋 Throw a Car Battery in the Ocean":
            current_karma = self.db.get_player_karma(user_id)
            result = item_engine.execute_car_battery(current_karma)
            
            if not result["success"]:
                # Refund the item because they couldn't use it!
                self.db.add_item(user_id, actual_item_name, 1)
                await interaction.response.send_message(result["msg"], ephemeral=True)
                return

            self.db.add_fish_bulk(user_id, result["caught_fishes"])
            self.db.deduct_karma_points(user_id, result["karma_deductions"])

            await interaction.response.send_message(
                f"🔋 *BZZZZZT* You hurled the car battery into the sea! The water boiled and 15 fish floated to the surface.\n\n"
                f"🎣 **Loot:** {result['catch_text']}\n"
                f"📉 **Penalty:** You lost {result['karma_lost']} Karma. The ecosystem absolutely hates you."
            )

    @app_commands.command(name="how_to_play", description="Explaining how to play and the rules")
    async def how_to_play(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="🎣 Welcome to Bipbob's Live Fish Market! 📈", 
            color=discord.Color.blue()
        )
        
        embed.description = (
            "Welcome to a chaotic, heavily economy-driven fishing simulator! "
            "Your goal is to cast your line, manipulate a dynamic stock market, "
            "collect illegal Black Market items, and build your ultimate net worth. "
            "Here is everything you need to know to survive the market:\n\n"
            "\n"
        )

        embed.add_field(
            name="🎮 1. The Core Gameplay Loop",
            value=(
                "• `/fish` : Cast your line to catch fish across 10 rarity tiers (from Bozo ⚪ to God ✨).\n"
                "• `/inventory` : View your fish stockpile and see how their current value stacks up against base pricing.\n"
                "• `/balance` : Check your liquid cash versus your total asset net worth. \n\n"
            ),
            inline=False
        )

        embed.add_field(
            name="📈 2. Shifting Stocks & Dynamic Slippage",
            value=(
                "• `/market` : Prices shift naturally every 5 minutes with randomized breaking news events!\n"
                "• `/sell <tier>` or `/sell_all` : Liquidating a huge tier **crashes** its global value. Thanks to a dynamic curve, you are paid the *average price* across the crash to prevent exploits.\n"
                "• `/buy <tier> <qty>` : Purchasing fish directly from the market drives its global price **skyward**. \n\n"
            ),
            inline=False
        )

        embed.add_field(
            name="☯️ 3. The Karma System (Permanent Luck)",
            value=(
                "• Got trash or low-tier fish? Don't sell them for pennies. Use `/free` to release your inventory back into the sea!\n"
                "• Releasing fish grants permanent **Karma Points** for those specific tiers.\n"
                "• Every 100 Karma points gives a **+1% luck bonus** to your base catch rates. Grind Karma to make rare fish spawn effortlessly! \n\n"
            ),
            inline=False
        )

        embed.add_field(
            name="⬛ 4. Rigging the Game (The Black Market)",
            value=(
                "Check `/items` to purchase or track rule-bending items:\n"
                "• **📄 Tax Evasion Manual:** Freeze the market! Sell off inventory completely clean without triggering a global price crash.\n"
                "• **📱 Burner Phone:** Trigger a malicious Bogdanoff Short Squeeze, tripling your downward market impact to ruin the economy for everyone else.\n"
                "• **💳 Mommy's Credit Card:** Access infinite VIP liquidity! Buy mass fish volume at a perfectly flat market rate without driving the price up while buying. \n\n"
            ),
            inline=False
        )

        embed.set_footer(text="Rule #1: The ecosystem hates you. Rule #2: Maximize your margins. Happy fishing!")
        await interaction.followup.send(embed=embed)
        

async def setup(bot):
    await bot.add_cog(FishingCommands(bot))