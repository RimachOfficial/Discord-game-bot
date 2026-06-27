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

    @app_commands.command(name="inventory", description="Check your fish stash!")
    async def inventory(self, interaction: discord.Interaction):
        # 1. Get data from database
        user_inv = self.db.get_inventory(str(interaction.user.id))
        
        if not user_inv:
            await interaction.response.send_message("🪣 Your bucket is empty! Go use `/fish`.")
            return
            
        embed = discord.Embed(title=f"🎒 {interaction.user.name}'s Inventory", color=discord.Color.blue())
        
        # Set up dictionary buckets for each tier to group fish together
        tier_groups = {tier: [] for tier in FISH_DATA.keys()}
        total_value = 0 
        
        # 2. Sort the database results into their respective tiers
        for fish_name, quantity in user_inv:
            tier = FISH_TO_TIER.get(fish_name)
            if not tier:
                continue # Safety bypass for old test data strings
                
            fish_base_value = FISH_VALUES.get(fish_name, 0)
            tier_wealth = quantity * fish_base_value
            total_value += tier_wealth
            
            # Pack data into its corresponding tier group
            tier_groups[tier].append((fish_name, quantity, tier_wealth))
            
        # 3. Add fields horizontally for each tier that has items in it
        for tier, fish_list in tier_groups.items():
            if not fish_list:
                continue # Skip empty tiers to keep the layout clean
                
            field_content = ""
            for name, qty, wealth in fish_list:
                field_content += f"**{name}**\n└ x{qty} (💰${wealth:,})\n\n"
            
            embed.add_field(
                name=tier, 
                value=field_content.strip(), 
                inline=True # Forces tiers to align side-by-side horizontally
            )
            
        # 4. Global total value sitting perfectly under all horizontal blocks
        embed.description = f"**Total Stash Value:** 💰 **${total_value:,}**\n"
            
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(InventoryCommands(bot))