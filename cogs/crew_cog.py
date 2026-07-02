import discord
from discord import app_commands
from discord.ext import commands, tasks
from constants import CREW_CATALOG
from engines import crew_engine

# ⏱️ CONFIGURATION: Set how many minutes pass between each passive income tick
MINUTES_OF_UPDATE = 5.0

# ------------------------------------------------------------------
# 🛒 THE RECRUITMENT DROPDOWN COMPONENTS
# ------------------------------------------------------------------
class CrewRecruitDropdown(discord.ui.Select):
    def __init__(self, db, user_cash, user_id):
        self.db = db
        self.user_cash = user_cash
        self.user_id = user_id
        
        options = []
        for crew_name, details in CREW_CATALOG.items():
            current_level = self.db.get_crew_level(user_id, crew_name)
            
            # Use engine logic to find the initial level 0 -> 1 hiring cost
            upgrade_info = crew_engine.get_upgrade_details(crew_name, current_level)
            price = upgrade_info["next_cost"]
            
            # Visual status indicators
            if current_level > 0:
                emoji = "💼"
                desc_prefix = f"Lv. {current_level} (Already Hired)"
            elif user_cash >= price:
                emoji = "✅"
                desc_prefix = f"${price:.2f} | Hire Now!"
            else:
                emoji = "❌"
                desc_prefix = f"${price:.2f} | Low Funds"

            options.append(discord.SelectOption(
                label=crew_name,
                description=f"{desc_prefix} - {details['description'][:50]}...",
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
                f"❌ You don't have enough cash! Recruiting **{selected_crew}** costs `${details['next_cost']:.2f}`, but you only have `${current_cash:.2f}`.", 
                ephemeral=True
            )
            return

        self.db.update_player_cash(user_id, -details["next_cost"], interaction.user.name)
        self.db.set_crew_level(user_id, selected_crew, 1)
        
        await interaction.followup.send(f"🤝 **Contract Signed!** You successfully hired **{selected_crew}** for `${details['next_cost']:.2f}`! They are now yielding passive income.")


class CrewRecruitView(discord.ui.View):
    def __init__(self, db, user_cash, user_id):
        super().__init__(timeout=120)
        self.add_item(CrewRecruitDropdown(db, user_cash, user_id))


# ------------------------------------------------------------------
# 🧑‍🌾 THE MAIN COG SYSTEM WITH MINUTELY BACKGROUND LOOP
# ------------------------------------------------------------------
class CrewCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.passive_income_loop.start()

    def cog_unload(self):
        self.passive_income_loop.cancel()

    # ⏱️ Switched from hours=1.0 to minutes=MINUTES_OF_UPDATE
    @tasks.loop(minutes=MINUTES_OF_UPDATE)
    async def passive_income_loop(self):
        print(f"💼 Processing crew passive paychecks (Every {MINUTES_OF_UPDATE} minutes)...")
        try:
            all_crew_data = self.db.get_all_active_crew()
            payouts = {}
            
            # Scale factor: e.g. 5 minutes / 60 minutes = 0.0833 of their hourly wage
            time_fraction = MINUTES_OF_UPDATE / 60.0
            
            for user_id, crew_name, level in all_crew_data:
                if level <= 0:
                    continue
                config = CREW_CATALOG.get(crew_name)
                if config:
                    hourly_yield = config["base_production"] * level
                    # Calculate fractional payout for this specific tick window
                    tick_yield = hourly_yield * time_fraction
                    payouts[user_id] = payouts.get(user_id, 0.0) + tick_yield

            for user_id, total_cash_earned in payouts.items():
                if total_cash_earned > 0:
                    # Added a decimal rounding safety step since division introduces long floats
                    self.db.update_player_cash(user_id, round(total_cash_earned, 2), "Crew Passive Income")
            print(f"✅ Distributed passive minute-scaled income to {len(payouts)} users!")
        except Exception as e:
            print(f"❌ Error in passive income worker thread loop: {e}")

    @passive_income_loop.before_loop
    async def before_passive_income_loop(self):
        await self.bot.wait_until_ready()

    # ------------------------------------------------------------------
    # COMMAND A: /crew
    # ------------------------------------------------------------------
    @app_commands.command(name="crew", description="Open your crew management board to hire staff or check statistics.")
    async def view_crew(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        user_cash = self.db.get_player_balance(user_id)
        
        embed = discord.Embed(
            title="🧑‍🌾 Bipbob's Offshore Idle Crew HQ",
            description="Recruit your friends to work the high seas for passive capital. Select an unhired crew member from the dropdown below to sign their contract!",
            color=discord.Color.dark_gold()
        )
        embed.add_field(name="Your Balance", value=f"`${user_cash:,}`", inline=False)

        for crew_name, config in CREW_CATALOG.items():
            current_level = self.db.get_crew_level(user_id, crew_name) 
            details = crew_engine.get_upgrade_details(crew_name, current_level)
            
            if current_level > 0:
                status_label = f"**🔄 Level {current_level}**"
                action_label = "Level Up Cost"
            else:
                status_label = "❌ *Not Yet Acquired*"
                action_label = "Initial Recruitment Cost"
                
            value_text = (
                f"{status_label}\n"
                f"💬 *\"{details['desc']}\"*\n"
                f"⚙️ Income Rate: `${details['current_prod']:,}/hr` ➡️ `${details['next_prod']:,}/hr`\n"
                f"💰 {action_label}: `${details['next_cost']:,}`\n"
            )
                
            embed.add_field(name=f"👤 {crew_name}", value=value_text, inline=False)
            
        embed.set_footer(text="To upgrade existing staff levels, use the /upgrade_crew command.")
        
        view = CrewRecruitView(self.db, user_cash, user_id)
        await interaction.response.send_message(embed=embed, view=view)

    # ------------------------------------------------------------------
    # COMMAND B: /upgrade_crew
    # ------------------------------------------------------------------
    @app_commands.command(name="upgrade_crew", description="Level up an existing crew member that you already own.")
    @app_commands.describe(crew_member="Select which employee you are upgrading.")
    @app_commands.choices(crew_member=[
        app_commands.Choice(name="Rimach The Fisherman",    value="Rimach The Fisherman"),
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
                f"❌ Low funds! You need `${details['next_cost']:.2f}` to upgrade **{crew_name}**, but you only have `${user_cash:.2f}`.",
                ephemeral=True
            )
            return
            
        self.db.update_player_cash(user_id, -details["next_cost"], interaction.user.name)
        self.db.set_crew_level(user_id, crew_name, current_level + 1)
        
        await interaction.followup.send(
            f"📈 **Promotion Complete!**\n"
            f"Successfully elevated **{crew_name}** to **Level {current_level + 1}**!\n"
            f"Their production rate increased to `${details['next_prod']:.2f}/hr`."
        )

async def setup(bot):
    await bot.add_cog(CrewCog(bot))