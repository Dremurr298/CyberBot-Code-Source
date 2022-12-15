import discord
import time
import random
import datetime
from discord.ext import commands
from discord import app_commands

#-------------------------------

Color = 233087
Bot_Time = time.time()

#-------------------------------

def inspect_time(seconds, str_date):
    if seconds < 86400:
        Time = str_date.replace(':',' ')
        Time = Time.split()
        Time = f'0D : {Time[0]}h : {Time[1]}m : {Time[2]}s'
        return Time
    else:
        Time = str_date.replace(':',' ')
        Time = Time.replace('days,','').replace('day,','')
        Time = Time.split()
        Time = f'{Time[0]}D : {Time[1]}h : {Time[2]}m : {Time[3]}s'
        return Time

#-------------------------------

class Basic_Cmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help")
    async def help(self, interaction: discord.Interaction) -> None:
        """For searching an command!"""
        List = ['```']
        Time = datetime.datetime.now()

        for _command in self.bot.commands:
            List.append(f'- {_command}')
        
        Array = "\n".join(List)
        Embed = discord.Embed(
            title='Bot Command',
            description=f'{Array}\n```',
            color=Color
        )
        Embed.set_footer(text=f'Executor : {interaction.user.name} | {Time}')
        await interaction.response.defer()
        await interaction.followup.send(embed=Embed)

    @app_commands.command(name='ping')
    async def ping(self, interaction: discord.Interaction) -> None:
        """Showing My Latency!"""

        Latency = int(self.bot.latency * 1000)
        Time = datetime.datetime.now()

        Embed = discord.Embed(
            title=f'CyberBot Ping',
            description=f'Pong! `{Latency}`',
            color=Color
        )
        Embed.set_footer(text=f'Executor : {interaction.user.name} | {Time}')
        await interaction.response.defer()
        await interaction.followup.send(embed=Embed)
    
    @app_commands.command(name='ppsize')
    async def ppsize(self, interaction: discord.Interaction, user: discord.Member=None) -> None:
        """Simple And Fun Command"""

        if user is None:
            user = interaction.user

        List = []
        Time = datetime.datetime.now()

        for x in range(random.randint(1,10)):
            List.append('=')
        
        Array = "".join(List)
        Embed = discord.Embed(
            title=f'{user.name} PP',
            description=f'8{Array}D',
            color=Color
        )
        Embed.set_footer(text=f'Executor : {interaction.user.name} | {Time}')
        await interaction.response.defer()
        await interaction.followup.send(embed=Embed)
    
    @app_commands.command(name='gaymeter')
    async def howgay(self, interaction: discord.Interaction, user: discord.Member=None) -> None:
        """Simple And Fun Command"""

        if user is None:
            user = interaction.user
        
        Time = datetime.datetime.now()

        Embed = discord.Embed(
            title=f'🏳️‍🌈 | {user.name} Gay Meter',
            description=f'{user.name} is `{random.randint(1,100)}%` gay!',
            color=Color
        )
        Embed.set_footer(text=f'Executor : {user.name} | {Time}')
        await interaction.response.defer()
        await interaction.followup.send(embed=Embed)

    @app_commands.command(name='hownerd')
    async def hownerd(self, interaction: discord.Interaction, user: discord.Member=None) -> None:
        """Simple And Fun Command"""

        if user is None:
            user = interaction.user
        
        Time = datetime.datetime.now()

        Embed = discord.Embed(
            title=f'🤓 | {user.name} Nerd Meter',
            description=f'{user.name} is `{random.randint(1,100)}%` Nerd!',
            color=Color
        )
        Embed.set_footer(text=f'Executor : {user.name} | {Time}')
        await interaction.response.defer()
        await interaction.followup.send(embed=Embed)

    @app_commands.command(name='coinflip')
    async def cf(self, interaction: discord.Interaction, cf_val: str=None) -> None:
        """Simple And Fun Command"""

        Time = datetime.datetime.now()
        val = cf_val
        await interaction.response.defer()

        if val is None:
            Embed = discord.Embed(
                title=f'🪙 | {interaction.user.name} Cf fail',
                description=f'> You must add selection (heads or tails)!',
                color=Color
            )
            Embed.set_footer(text=f'Executor : {interaction.user.name} | {Time}')
            await interaction.followup.send(embed=Embed)
            return
        
        elif val.lower() not in ['heads','tails']:
            Embed = discord.Embed(
                title=f'🪙 | {interaction.user.name} Cf fail',
                description=f'> Must heads or tails!',
                color=Color
            )
            Embed.set_footer(text=f'Executor : {interaction.user.name} | {Time}')
            await interaction.followup.send(embed=Embed)
            return
        
        else:
            CoinList = ['heads','tails']
            CoinGet = str(random.choice(CoinList))

            if CoinGet == val.lower():
                Embed = discord.Embed(
                    title=f'🪙 | {interaction.user.name} Win!',
                    description=f'```\n{interaction.user.name} Select : {val.lower()}\nBot Select : {CoinGet}\n```',
                    color=Color
                )
                Embed.set_footer(text=f'Executor : {interaction.user.name} | {Time}')
                await interaction.followup.send(embed=Embed)
                return
            
            else:
                Embed = discord.Embed(
                    title=f'🪙 | {interaction.user.name} Lose!',
                    description=f'```\n{interaction.user.name} Select : {val.lower()}\nBot Select : {CoinGet}\n```',
                    color=Color
                )
                Embed.set_footer(text=f'Executor : {interaction.user.name} | {Time}')
                await interaction.followup.send(embed=Embed)
                return
        
    @cf.autocomplete('cf_val')
    async def coinflip_autocomplete(self, interaction: discord.Interaction, cf_val: str):
        return [
            app_commands.Choice(name = 'heads', value = 'heads'),
            app_commands.Choice(name= 'tails', value= 'tails')
        ]

    @app_commands.command(name='uptime')
    async def uptime(self, interaction: discord.Interaction):
        """Show how long does the bot online"""
        await interaction.response.defer()

        user = interaction.user
        user_id = user.id
        user_name = user.name
        Time = datetime.datetime.now()

        Uptime = int(time.time() - Bot_Time)
        Uptime = inspect_time(Uptime, f'{datetime.timedelta(seconds=Uptime)}')

        Embed = discord.Embed(
            title='🕛 | CyberBot Uptime',
            description=f'> CyberBot Has Been online for : \n```{Uptime}```',
            color=Color
        )
        Embed.set_footer(text=f'Executor : {user_name} | {Time}')
        await interaction.followup.send(embed=Embed)

#-------------------------------

async def setup(bot):
	await bot.add_cog(Basic_Cmd(bot))