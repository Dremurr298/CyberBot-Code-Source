import discord
from discord.ext import commands
import os

#-----------------------------------

def drawbar(amount, length, m_length):
    return f"{'█'*round(int(amount)/(m_length/length)):◦<{length}}"

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='cb.',
            intents=discord.Intents().all(),
            help_command=None
        )

    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                print(f'[Logs] {filename} has been loaded!')
                await bot.load_extension(f'cogs.{filename[:-3]}')

    async def on_ready(self):
        All_Members = bot.get_all_members()
        All_Guilds = bot.guilds
        Count = 0

        for x in All_Members:
            Count += 1
        
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{Count} Members & {len(All_Guilds)} Server!"
            )
        )

        print(f'[Logs] Message : Bot is running...\n[Logs] Connection : {int(bot.latency*1000)}ms\n[Logs] Member_Count : {Count}\n[Logs] Guild_count : {drawbar(len(All_Guilds), 15, 100)} | {len(All_Guilds)}')

#-----------------------------------

bot = MyBot()
Tree = bot.tree

#-----------------------------------

@bot.command()
@commands.is_owner()
async def sync(ctx):
    try:
        await Tree.sync()
        print('[LOGS] SYNC DONE')
    except Exception as e:
        print('[LOGS]', e)

@bot.command()
async def start_guild_sync(ctx):
    try:
        await Tree.sync(guild=ctx.guild)
        await ctx.send('Done Syncing!')
    except Exception as e:
        await ctx.send(f'Error Was Occured : {e}')

#------------------

bot.run(f"{os.environ['TOKEN']}")