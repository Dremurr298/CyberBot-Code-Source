import discord
from discord import app_commands
from discord.ext import commands

#------------------

class testing_cmd(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @app_commands.command(name="command-1")
    async def my_command(self, interaction: discord.Interaction) -> None:
        """ /command-1 """
        msg = await interaction.response.defer()
        await interaction.followup.send(
            "Hello from command 1!",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(testing_cmd(bot))