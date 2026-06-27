import discord
from discord import app_commands
from discord.ext import commands
from database import FISH_DATA, FISH_VALUES

# Create a quick map to find which tier a specific fish name belongs to
FISH_TO_TIER = {species: tier for tier, info in FISH_DATA.items() for species in info["species"]}

class InventoryCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="inventory", description="Check your fish stash with live market valuation!")
    async def inventory(self, interaction: discord.Interaction):
        # 🛡️ Defer the response instantly so the command doesn't timeout
        await interaction.response.defer()
        
        # 1. Get data from database
        user_id = str(interaction.user.id)
        user_inv = self.db.get_inventory(user_id)
        
        if not user_inv:
            await interaction.followup.send("🪣 Your bucket is empty! Go use `/fish`.")
            return
            
        embed = discord.Embed(title=f"🎒 {interaction.user.name}'s Inventory", color=discord.Color.blue())
        
        # Fetch the live market prices to map current worth
        market_prices = dict(self.db.get_market_prices())
        
        # Set up dictionary buckets for each tier to group fish together
        tier_groups = {tier: [] for tier in FISH_DATA.keys()}
        total_market_value = 0 
        total_base_value = 0
        
        # 2. Sort the database results into their respective tiers
        for fish_name, quantity in user_inv:
            tier = FISH_TO_TIER.get(fish_name)
            if not tier:
                continue # Safety bypass for old test data strings
                
            # Get values (individual static base price vs fluctuating unit market price)
            fish_base_unit = FISH_VALUES.get(fish_name, 0)
            fish_market_unit = market_prices.get(tier, fish_base_unit)
            
            # Multiply by quantity owned
            item_total_base = quantity * fish_base_unit
            item_total_market = quantity * fish_market_unit
            
            total_base_value += item_total_base
            total_market_value += item_total_market
            
            # Pack data into its corresponding tier group
            tier_groups[tier].append((fish_name, quantity, item_total_market, item_total_base))
            
        # 3. Add fields horizontally for each tier that has items in it
        for tier, fish_list in tier_groups.items():
            if not fish_list:
                continue # Skip empty tiers to keep the layout clean
                
            field_content = ""
            for name, qty, market_w, base_w in fish_list:
                field_content += (
                    f"**{name}**\n"
                    f"└ x{qty}\n"
                    f"   • Mkt: `💰${market_w:,}`\n"
                    f"   • Base: `🏛️${base_w:,}`\n\n"
                )
            
            embed.add_field(
                name=tier, 
                value=field_content.strip(), 
                inline=True # Forces tiers to align side-by-side horizontally
            )
            
        # 4. Global valuation summary at the top of the embed description
        profit_loss_color = "🟢" if total_market_value >= total_base_value else "🔴"
        embed.description = (
            f"📈 **Live Market Worth:** **${total_market_value:,}**\n"
            f"🏛️ **Static Base Worth:** `${total_base_value:,}`\n"
            f"{profit_loss_color} **Market Performance:** `{(total_market_value - total_base_value):+,}` compared to base values.\n"
        )
            
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(InventoryCommands(bot))