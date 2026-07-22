import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Modal, TextInput
from constants import ITEM_CATALOG
from engines import item_engine

class BulkPurchaseModal(Modal):
    def __init__(self, db, item_name, price):
        super().__init__(title=f"Bulk Buy: {item_name}")
        self.db = db
        self.item_name = item_name
        self.price = price

        # Text input for quantity selection
        self.quantity_input = TextInput(
            label=f"Quantity (Price per unit: ${price:,})",
            placeholder="Enter the number of items you want to buy...",
            min_length=1,
            max_length=4,
            required=True
        )
        self.add_item(self.quantity_input)

    async def on_submit(self, interaction: discord.Interaction):
        raw_val = self.quantity_input.value.strip()
        
        # 1. Validation Checks
        if not raw_val.isdigit():
            await interaction.response.send_message("❌ Purchase cancelled. Please enter a valid positive whole number.", ephemeral=True)
            return
            
        quantity = int(raw_val)
        if quantity <= 0:
            await interaction.response.send_message("❌ Purchase cancelled. You must buy at least 1 item.", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        total_cost = self.price * quantity
        current_cash = self.db.get_player_balance(user_id)

        # 2. Balance Verification
        if current_cash < total_cost:
            await interaction.response.send_message(
                f"❌ You don't have enough cash! **{quantity}x {self.item_name}** costs `${total_cost:,}`, but you only have `${current_cash:,}`.", 
                ephemeral=True
            )
            return

        # 3. Process Bulk Database Transactions
        self.db.update_player_cash(user_id, -total_cost, interaction.user.name)
        
        # Safely loops the inventory insertion to support your existing database layout
        for _ in range(quantity):
            self.db.add_item(user_id, self.item_name)

        await interaction.response.send_message(
            f"✅ **Bulk Purchase Successful!**\nBought **{quantity}x {self.item_name}** for a total of `${total_cost:,}`!"
        )


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
            
        selected_item = self.values[0]
        user_id = str(interaction.user.id)
        
        # Locate item configuration inside ITEM_CATALOG
        item_details = None
        for category, items in ITEM_CATALOG.items():
            if selected_item in items:
                item_details = items[selected_item]
                break
                
        if not item_details:
            await interaction.response.send_message("❌ Item data not found in catalog.", ephemeral=True)
            return
            
        item_type = item_details.get("type", "Consumable")
        price = item_details.get("price", 999999999)

        # ------------------------------------------------------------------
        # FLOW A: CONSUMABLE ITEM -> Prompt Modal for Bulk Quantity
        # ------------------------------------------------------------------
        if item_type == "Consumable":
            modal = BulkPurchaseModal(self.db, selected_item, price)
            await interaction.response.send_modal(modal)
            return

        # ------------------------------------------------------------------
        # FLOW B: PASSIVE ITEM -> Normal Single Instant Buy
        # ------------------------------------------------------------------
        await interaction.response.defer()
        
        # Fetch fresh data for verification
        current_cash = self.db.get_player_balance(user_id)
        owned_count = self.db.get_item_count(user_id, selected_item)
        
        # Run logic via engine
        result = item_engine.calculate_item_purchase(selected_item, current_cash, owned_count)
        
        if not result["success"]:
            await interaction.followup.send(result["msg"], ephemeral=True)
            return
            
        # Database Transactions
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
            description="Spend your liquid cash on illegal gear and passives.\nSelect an item from the dropdown below to purchase.",
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
                
        embed.set_footer(text="Passives can only be bought once! Consumables can be bought in bulk.")
        
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