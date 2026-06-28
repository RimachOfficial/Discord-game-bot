import discord
from discord import app_commands
from discord.ext import commands
from constants import ITEM_CATALOG
from engines import item_engine

class ShopDropdown(discord.ui.Select):
    def __init__(self, db, user_cash):
        self.db = db
        self.user_cash = user_cash
        
        # Populate options dynamically from ITEM_CATALOG
        options = []
        for category, items in ITEM_CATALOG.items():
            for item_name, details in items.items():
                price = details.get("price", 999999999)
                desc = details.get("desc", "No description.")[:50] + "..."
                
                # Visual indicator if they can afford it
                emoji = "✅" if user_cash >= price else "❌"
                
                options.append(discord.SelectOption(
                    label=item_name,
                    description=f"${price:,} | {desc}",
                    value=item_name,
                    emoji=emoji
                ))
                
        super().__init__(placeholder="Select an item to purchase...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # Only the person who invoked the command can use the dropdown
        if interaction.user.id != interaction.message.interaction_metadata.user.id:
            await interaction.response.send_message("❌ This is not your shop menu!", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        selected_item = self.values[0]
        user_id = str(interaction.user.id)
        
        # Fetch fresh data in case they bought something else
        current_cash = self.db.get_player_balance(user_id)
        owned_count = self.db.get_item_count(user_id, selected_item)
        
        # 1. Run logic via engine
        result = item_engine.calculate_item_purchase(selected_item, current_cash, owned_count)
        
        if not result["success"]:
            await interaction.followup.send(result["msg"], ephemeral=True)
            return
            
        # 2. Database Transactions
        self.db.update_player_cash(user_id, -result["price"], interaction.user.name)
        self.db.add_item(user_id, selected_item)
        
        await interaction.followup.send(result["msg"])
        

class ShopView(discord.ui.View):
    def __init__(self, db, user_cash):
        super().__init__(timeout=120)
        self.add_item(ShopDropdown(db, user_cash))


class ShopCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="shop", description="Open the Black Market to buy illegal fishing gear and passives!")
    async def shop(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        user_cash = self.db.get_player_balance(user_id)
        
        embed = discord.Embed(
            title="🛒 Welcome to the Black Market!",
            description="Spend your liquid cash on illegal gear and passives.\nSelect an item from the dropdown below to purchase it instantly.",
            color=discord.Color.dark_purple()
        )
        
        embed.add_field(name="Your Liquid Cash", value=f"`${user_cash:,}`", inline=False)
        
        for category, items in ITEM_CATALOG.items():
            items_text = ""
            for name, details in items.items():
                price = details.get("price", 999999999)
                item_type = details.get("type", "Consumable")
                desc = details.get("desc", "No description.")
                
                # Check if player owns this passive
                owned = ""
                if item_type == "Passive":
                    owned_count = self.db.get_item_count(user_id, name)
                    if owned_count > 0:
                        owned = " *(✅ Owned)*"
                        
                items_text += f"**{name}** - `${price:,}` {owned}\n*{item_type}* - {desc}\n\n"
                
            if items_text:
                embed.add_field(name=category, value=items_text, inline=False)
                
        embed.set_footer(text="Passives can only be bought once and do not stack!")
        
        view = ShopView(self.db, user_cash)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="toggle", description="Enable or disable one of your passive items.")
    @app_commands.describe(item="The passive item to toggle on or off.")
    @app_commands.choices(item=[
        app_commands.Choice(name="♻️ Discord Mod Application",         value="♻️ Discord Mod Application"),
        app_commands.Choice(name="🧢 Boyfriend Repellent",              value='🧢 The "I Have a Boyfriend" Repellent'),
        app_commands.Choice(name="📄 Tax Evasion Manual",               value="📄 Tax Evasion Manual"),
        app_commands.Choice(name="💳 Mommy's Credit Card",              value="💳 Mommy's Credit Card"),
    ])
    async def toggle(self, interaction: discord.Interaction, item: app_commands.Choice[str]):
        user_id  = str(interaction.user.id)
        item_name = item.value
        buff_key  = f"item_disabled:{item_name}"

        # 1. Fetch state from DB (Data Layer)
        owned_count        = self.db.get_item_count(user_id, item_name)
        currently_disabled = self.db.get_buff(user_id, buff_key) is not None

        # 2. Validate + flip state (Engine / Business Layer)
        result = item_engine.toggle_item_usage(item_name, owned_count, currently_disabled)

        if not result["success"]:
            await interaction.response.send_message(result["msg"], ephemeral=True)
            return

        # 3. Persist the new state (Data Layer)
        if result["new_disabled"]:
            self.db.set_buff(user_id, buff_key, "1")
        else:
            self.db.clear_buff(user_id, buff_key)

        # 4. Respond (Interface Layer)
        await interaction.response.send_message(result["msg"])


async def setup(bot):
    await bot.add_cog(ShopCog(bot))
