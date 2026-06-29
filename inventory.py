import discord
from discord import app_commands
from discord.ext import commands
from constants import FISH_DATA, FISH_VALUES, FISH_TO_TIER

class InventoryCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="inventory", description="Check your fish stash with live market valuation!")
    async def inventory(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        user_inv = self.db.get_inventory(user_id)
        
        if not user_inv:
            await interaction.followup.send("🪣 Your bucket is empty! Go use `/fish`.")
            return
            
        embed = discord.Embed(title=f"🎒 {interaction.user.name}'s Inventory", color=discord.Color.blue())
        
        market_prices = dict(self.db.get_market_prices())
        
        tier_groups = {tier: [] for tier in FISH_DATA.keys()}
        total_market_value = 0 
        total_base_value = 0
        
        for fish_name, quantity in user_inv:
            tier = FISH_TO_TIER.get(fish_name)
            if not tier:
                continue
                
            fish_base_unit = FISH_VALUES.get(fish_name, 0)
            fish_market_unit = market_prices.get(tier, fish_base_unit)
            
            item_total_base = quantity * fish_base_unit
            item_total_market = quantity * fish_market_unit
            
            total_base_value += item_total_base
            total_market_value += item_total_market
            
            tier_groups[tier].append((fish_name, quantity, item_total_market, item_total_base))
            
        for tier, fish_list in tier_groups.items():
            if not fish_list:
                continue
                
            field_content = ""
            for name, qty, market_w, base_w in fish_list:
                field_content += (
                    f"**{name}**\n"
                    f"└ x{qty}\n"
                    f"   • Mkt: `💰${market_w:.2f}`\n"
                    f"   • Base: `🏛️${base_w:.2f}`\n\n"
                )
            
            embed.add_field(
                name=tier, 
                value=field_content.strip(), 
                inline=True
            )
            
        profit_loss_color = "🟢" if total_market_value >= total_base_value else "🔴"
        embed.description = (
            f"📈 **Live Market Worth:** **${total_market_value:.2f}**\n"
            f"🏛️ **Static Base Worth:** `${total_base_value:.2f}`\n"
            f"{profit_loss_color} **Market Performance:** `{(total_market_value - total_base_value):+.2f}` compared to base values.\n"
        )
            
        from constants import ITEM_CATALOG
        owned_items_text = ""
        
        for category, items in ITEM_CATALOG.items():
            for item_name in items.keys():
                quantity = self.db.get_item_count(user_id, item_name)
                if quantity > 0:
                    owned_items_text += f"**{quantity}x** {item_name}\n"
                    
        if owned_items_text:
            embed.add_field(name="🎒 Black Market Stash", value=owned_items_text.strip(), inline=False)

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(InventoryCommands(bot))