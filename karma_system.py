import discord
from discord import app_commands
from discord.ext import commands
from constants import FISH_DATA, FISH_TO_TIER

class KarmaSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="free", description="Release all your fish back into the ocean to gain permanent Karma luck!")
    async def free_fish(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = str(interaction.user.id)
        
        user_inv = self.db.get_inventory(user_id)
        
        if not user_inv or sum(q for _, q in user_inv) == 0:
            await interaction.followup.send("🪣 Your inventory is already empty! Go catch some fish first.")
            return

        total_fish_freed = 0
        karma_to_add = {}

        for fish_name, quantity in user_inv:
            if quantity > 0 and fish_name in FISH_TO_TIER:
                tier = FISH_TO_TIER[fish_name]
                base_val = FISH_DATA[tier]["value"]
                
                # Math: Calculate karma per fish. Minimum 1 point.
                karma_per_fish = max(1, int(base_val / 10))
                total_karma_for_species = karma_per_fish * quantity
                
                karma_to_add[tier] = karma_to_add.get(tier, 0) + total_karma_for_species
                total_fish_freed += quantity

        db_karma_payload = [(tier, points) for tier, points in karma_to_add.items()]
        
        self.db.clear_inventory(user_id)
        self.db.add_karma_points(user_id, db_karma_payload)

        embed = discord.Embed(
            title="🌊 The Ocean Thanks You!", 
            description=f"You opened your buckets and released **{total_fish_freed}** fish back into the wild!", 
            color=discord.Color.blue()
        )
        
        breakdown = ""
        for tier, points in karma_to_add.items():
            breakdown += f"• **{tier}**: `+{points:,} Karma` \n"
            
        embed.add_field(name="✨ Karma Earned Breakdown", value=breakdown, inline=False)
        embed.set_footer(text="Check your upgraded bonus luck status anytime using /karma")
        
        await interaction.followup.send(embed=embed)


    @app_commands.command(name="karma", description="View your accumulated Karma and fish tier luck modifiers.")
    async def view_karma(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = str(interaction.user.id)
        
        raw_karma = dict(self.db.get_player_karma(user_id))
        
        embed = discord.Embed(
            title="✨ Your Spiritual Karma & Luck Modifiers", 
            description="Releasing fish via `/free` gives you Karma. Every **100 points** in a tier grants a permanent **+1% drop-rate bonus** for that tier!",
            color=discord.Color.purple()
        )
        
        for tier in FISH_DATA.keys():
            points = raw_karma.get(tier, 0)
            luck_bonus = points / 100.0
            
            embed.add_field(
                name=tier,
                value=f"Points: **{points:,}**\nLuck Bonus: `+{luck_bonus:.2f}%`",
                inline=True
            )
            
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(KarmaSystem(bot))