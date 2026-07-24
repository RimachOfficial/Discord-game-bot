import discord
from discord import app_commands
from discord.ext import commands, tasks
from constants import CREW_CATALOG, FISH_DATA
from engines import crew_engine

# Configuration: Minutes between each market paycheck evaluation
MINUTES_OF_UPDATE = 5.0

class CrewRecruitDropdown(discord.ui.Select):
    def __init__(self, db, user_cash, user_id):
        self.db = db
        self.user_cash = user_cash
        self.user_id =str(user_id)
        
        
        options = []

        for crew_name, details in CREW_CATALOG.items():
            current_level = self.db.get_crew_level(user_id, crew_name)
            upgrade_info = crew_engine.get_upgrade_details(crew_name, current_level)
            price = upgrade_info["next_cost"]
            
            if current_level > 0:
                emoji = "💼"
                desc_prefix = f"Lv. {current_level} (Employed)"
            elif user_cash >= price:
                emoji = "✅"
                desc_prefix = f"${price:,.2f} | Hire Now!"
            else:
                emoji = "❌"
                desc_prefix = f"${price:,.2f} | Low Funds"

            options.append(discord.SelectOption(
                label=crew_name,
                description=f"{desc_prefix} - Tiers: {', '.join(details['assigned_tiers'])}",
                value=crew_name,
                emoji=emoji
            ))
            
        super().__init__(placeholder="Select a lad to recruit into your company...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != interaction.message.interaction_metadata.user.id:
            await interaction.response.send_message("❌ This is not your management portal!", ephemeral=True)
            return
            
        selected_crew = self.values[0]
        user_id = str(interaction.user.id)
        
        await interaction.response.defer()
        current_level = self.db.get_crew_level(user_id, selected_crew)
        
        if current_level > 0:
            await interaction.followup.send(f"❌ You already hired **{selected_crew}**! Use `/upgrade_crew` to level them up.", ephemeral=True)
            return
            
        details = crew_engine.get_upgrade_details(selected_crew, current_level)
        current_cash = self.db.get_player_balance(user_id)
        
        if current_cash < details["next_cost"]:
            await interaction.followup.send(
                f"❌ You don't have enough cash! Recruiting **{selected_crew}** costs `${details['next_cost']:,.2f}`, but you only have `${current_cash:,.2f}`.", 
                ephemeral=True
            )
            return

        self.db.update_player_cash(user_id, -details["next_cost"], interaction.user.name)
        self.db.set_crew_level(user_id, selected_crew, 1)
        
        await interaction.followup.send(f"🤝 **Contract Signed!** You successfully hired **{selected_crew}**! They are out tracking live stock yields.")


class CrewRecruitView(discord.ui.View):
    def __init__(self, db, user_cash, user_id):
        super().__init__(timeout=120)
        self.add_item(CrewRecruitDropdown(db, user_cash, user_id))


class CrewCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.passive_income_loop.start()

    def cog_unload(self):
        self.passive_income_loop.cancel()

    # ------------------------------------------------------------------
    # The Stock-Tied Background Revenue Engine
    # ------------------------------------------------------------------
    @tasks.loop(minutes=MINUTES_OF_UPDATE)
    async def passive_income_loop(self):
        print("💼 Recalculating crew paychecks against live stock valuations...")
        try:
            all_crew_data = self.db.get_all_active_crew()
            market_prices = dict(self.db.get_market_prices())
            payouts = {}
            
            time_fraction = MINUTES_OF_UPDATE / 60.0
            
            for user_id, crew_name, level in all_crew_data:
                if level <= 0:
                    continue
                config = CREW_CATALOG.get(crew_name)
                if not config:
                    continue
                
                # Calculate what their assigned tiers are valued at RIGHT NOW
                hourly_crew_yield = 0.0
                for tier in config["assigned_tiers"]:
                    # Fallback to base configuration value if market lookup doesn't resolve entry
                    base_price = FISH_DATA.get(tier, {}).get("value", 10.0)
                    live_price = market_prices.get(tier, base_price)
                    
                    # Hourly valuation: Catch volume multiplier * value
                    hourly_crew_yield += config["base_production"] * live_price
                
                # Multiply by employee level and scale to our execution time slice
                tick_yield = (hourly_crew_yield * level) * time_fraction
                payouts[user_id] = payouts.get(user_id, 0.0) + tick_yield

            for user_id, total_cash_earned in payouts.items():
                if total_cash_earned > 0:
                    self.db.update_player_cash(user_id, round(total_cash_earned, 2))
            print("✅ Live market-indexed payroll processing complete.")
        except Exception as e:
            print(f"❌ Error in stock evaluation loop: {e}")

    @passive_income_loop.before_loop
    async def before_passive_income_loop(self):
        await self.bot.wait_until_ready()

    # ------------------------------------------------------------------
    # COMMAND A: /crew (Live Dashboard Matrix)
    # ------------------------------------------------------------------
    @app_commands.command(name="crew", description="Check how hard your friends are getting wrecked by the fish market trends.")
    async def view_crew(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        user_cash = self.db.get_player_balance(user_id)
        market_prices = dict(self.db.get_market_prices())
        
        embed = discord.Embed(
            title="🧑‍🌾 Bipbob's Joint-Stock Crew Operations",
            description="Your workers generate value tied directly to live market pricing. If a tier crashes, their efficiency drops with it!",
            color=discord.Color.dark_gold()
        )
        embed.add_field(name="Your Funding", value=f"`${user_cash:,}`", inline=False)

        for crew_name, config in CREW_CATALOG.items():
            current_level = self.db.get_crew_level(user_id, crew_name) 
            upgrade_info = crew_engine.get_upgrade_details(crew_name, current_level)
            
            # Compute current real hourly yield matching live prices
            current_hourly_rate = 0.0
            next_hourly_rate = 0.0
            tier_status_lines = []
            
            for tier in config["assigned_tiers"]:
                base_val = FISH_DATA.get(tier, {}).get("value", 10.0)
                live_val = market_prices.get(tier, base_val)
                
                current_hourly_rate += (config["base_production"] * live_val) * max(1, current_level)
                next_hourly_rate += (config["base_production"] * live_val) * (current_level + 1)
                
                trend_marker = "🟢" if live_val > base_val else "🔴" if live_val < base_val else "⚪"
                tier_status_lines.append(f"{trend_marker} `{tier}` Price: `${live_val:,.2f}`")

            status_header = f"**🔄 Level {current_level}**" if current_level > 0 else "❌ *Not Yet Employed*"
            action_label = "Level Up Cost" if current_level > 0 else "Initial Recruitment Cost"
            
            # Clear display of current vs upcoming profitability states
            rate_display = f"`${current_hourly_rate:,.2f}/hr` ➡️ `${next_hourly_rate:,.2f}/hr`" if current_level > 0 else f"`$0.00/hr` ➡️ `${next_hourly_rate:,.2f}/hr`"

            value_text = (
                f"{status_header}\n"
                f"💬 *\"{config['description']}\"*\n"
                f"📊 **Target Assets:**\n" + "\n".join(tier_status_lines) + "\n"
                f"⚙️ Live Yield Efficiency: {rate_display}\n"
                f"💰 {action_label}: `${upgrade_info['next_cost']:,}`\n"
            )
                
            embed.add_field(name=f"👤 {crew_name}", value=value_text, inline=False)
            
        embed.set_footer(text="If your worker's market crashes, manipulate the stock using trades or wait out the rotation!")
        
        view = CrewRecruitView(self.db, user_cash, user_id)
        await interaction.response.send_message(embed=embed, view=view)

    # ------------------------------------------------------------------
    # COMMAND B: /upgrade_crew
    # ------------------------------------------------------------------
    @app_commands.command(name="upgrade_crew", description="Promote a worker to increase their total fish extraction capacities.")
    @app_commands.describe(crew_member="Select who you are upgrading.")
    @app_commands.choices(crew_member=[
        app_commands.Choice(name="Rimach The Fisherman",    value="Rimach The Fisherman"),
        app_commands.Choice(name="Ka2lina",                 value="Ka2lina"),
        app_commands.Choice(name="Jim The Wolf",            value="Jim The Wolf"),
        app_commands.Choice(name="Magician Oceans Red",     value="Magician Oceans Red"),
        app_commands.Choice(name="Secret the airplane",     value="Secret the airplane"),
        app_commands.Choice(name="Katratzoglou",            value="Katratzoglou"),
    ])
    async def upgrade_crew(self, interaction: discord.Interaction, crew_member: app_commands.Choice[str]):
        await interaction.response.defer()
        user_id = str(interaction.user.id)
        crew_name = crew_member.value
        
        current_level = self.db.get_crew_level(user_id, crew_name)
        
        if current_level == 0:
            await interaction.followup.send(
                f"❌ **You don't hire people via the upgrade system!**\nYou must purchase and recruit **{crew_name}** first from the `/crew` shop dropdown menu before you can level them up.",
                ephemeral=True
            )
            return
            
        details = crew_engine.get_upgrade_details(crew_name, current_level)
        user_cash = self.db.get_player_balance(user_id)
        
        if user_cash < details["next_cost"]:
            await interaction.followup.send(
                f"❌ Low funds! You need `${details['next_cost']:,.2f}` to upgrade **{crew_name}**, but you only have `${user_cash:,.2f}`.",
                ephemeral=True
            )
            return
            
        self.db.update_player_cash(user_id, -details["next_cost"], interaction.user.name)
        self.db.set_crew_level(user_id, crew_name, current_level + 1)
        
        await interaction.followup.send(
            f"📈 **Promotion Complete!**\n"
            f"Successfully elevated **{crew_name}** to **Level {current_level + 1}**!\n"
            f"Their catch capacity has been multiplied."
        )

async def setup(bot):
    await bot.add_cog(CrewCog(bot))