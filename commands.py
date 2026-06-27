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
        # 1. Roll for the fish
        tier = random.choices(FISH_TIERS, weights=FISH_WEIGHTS, k=1)[0]
        fish_name = random.choice(FISH_DATA[tier]["species"])
        value = FISH_DATA[tier]["value"]
        gif_url = FISH_DATA[tier]["gif"]
        
        # 2. Save to database
        self.db.add_fish(str(interaction.user.id), interaction.user.name, fish_name, value)
        
        # 3. Create a beautiful Embed
        embed = discord.Embed(
            title="🎣 You cast your line...",
            description=f"And reeled in a **{fish_name}**!\n\n✨ **Tier:** {tier}\n💰 **Value:** `${value:,}`",
            color=discord.Color.teal()
        )
        
        # This injects the meme GIF directly into the embed layout
        embed.set_image(url=gif_url)
        
        # 4. Send the embed response
        await interaction.response.send_message(embed=embed)

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

async def setup(bot):
    await bot.add_cog(FishingCommands(bot))