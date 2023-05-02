import discord
import time
import random
import json
import datetime
import prettytable
from discord.ext import commands
from discord import app_commands

#-------------------------------

Color = 233087
Help_Str = json.loads(open('./Help_Text.txt').read())
News_Str = json.loads(open('./news.txt','rb').read())
privguild = 979708145905594439
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

    @app_commands.command(name='ping')
    async def ping(self, interaction: discord.Interaction) -> None:
        """Showing My Latency!"""

        Latency = int(self.bot.latency * 1000)
        Time = datetime.datetime.now()

        Embed = discord.Embed(
            title=f'CyberBot Ping',
            description=f'Pong! `{Latency}ms`',
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

    @app_commands.command(name='news')
    async def news(self, interaction: discord.Interaction):
        """A Place to see an cyberbot top news!"""
        await interaction.response.defer()

        f_user = interaction.user
        user_name = f_user.name
        Time = datetime.datetime.now()

        #-------------------
        
        Guild = self.bot.get_guild(privguild)

        Emoji_1 = discord.utils.get(Guild.emojis, name='CYBUSER')
        Emoji_2 = discord.utils.get(Guild.emojis, name='CYBTUBE')
        Emoji_3 = discord.utils.get(Guild.emojis, name='PROGRAMMING')
        Emoji_4 = discord.utils.get(Guild.emojis, name='CYBERPROFESSION')

        #-------------------

        check = News_Str['news']
        Detail_SelOP_List = []

        table = prettytable.PrettyTable()
        table.field_names = ["CATEGORY", "DATE", "NEW FEATURE"]
        table._max_widths = {"CATEGORY": 233, "DATE": 116, "NEW": 351}

        HFile = discord.File("./img_folder/NewsHeader.png", filename="image.png")
        HeaderEmbed = discord.Embed(
            title=f'{user_name} News panel',
            color=Color
        )
        HeaderEmbed.set_image(url='attachment://image.png')

        for count in range(10):
            try:
                Detail_SelOP_List.append(
                    discord.SelectOption(
                        label=f'{count+1}. {check[count]["NEW"]}',
                        value=count,
                        description=f'Detail news of {check[count]["NEW"]}'
                    )
                )

                char = check[count]['NEW']
                if len(list(char)) > 15:
                    holder = list(char)
                    char = char[:11] + '...'
                table.add_row([f'{check[count]["CATEGORY"]}', f'{check[count]["DATE"]}', f'{char}'])
            except:
                table.add_row([f'-', '-','-'])

        class Detail_Panel(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.Index = 0

            @discord.ui.select(placeholder='Detail',max_values=1,min_values=1,options=Detail_SelOP_List)
            async def Details(self, interaction, select:discord.ui.Select):
                await interaction.response.defer()
                user = f_user
                user_id = user.id
                user_name = user.name
                inter_id = interaction.user.id

                if inter_id != user_id:
                    await interaction.response.defer()
                    await interaction.followup.send(
                        content=f'Sorry This Menu is controlled by {user_name}',
                        ephemeral=True
                    )
                    return inter_id == user_id

                self.Index = int(self.Details.values[0])
                HeaderImg = check[self.Index]["IMAGE"]

                if HeaderImg == 'NONE':
                    HFile = discord.File(f"./img_folder/NewsHeader.png", filename=f"Header.png")
                    HeaderImg = 'attachment://Header.png'
                else:
                    HFile = discord.File(f"./img_folder/{HeaderImg}.png", filename=f"{HeaderImg}.png")
                    HeaderImg = f'attachment://{HeaderImg}.png'

                HeaderEmbed = discord.Embed(
                    title=f'{user_name} News panel',
                    color=Color
                )
                HeaderEmbed.set_image(url=HeaderImg)
                Embed = discord.Embed(
                    title=f'{check[self.Index]["NEW"]}',
                    description=f'{check[self.Index]["DETAIL"]}',
                    color=Color
                )
                Embed.set_image(url='https://cdn.discordapp.com/attachments/987680634694684712/1090189524241485825/Line.png')
                Embed.set_footer(text=f'Executor : {user_name} | {Time}')

                await interaction.followup.send(
                    embeds=[HeaderEmbed, Embed],
                    file=HFile,
                    ephemeral=True
                )


        Embed = discord.Embed(
            description=f'```{table.get_string()}```',
            color=Color
        )
        Embed.set_image(url='https://cdn.discordapp.com/attachments/987680634694684712/1090189524241485825/Line.png')
        Embed.set_footer(text=f'Executor : {user_name} | {Time}')

        await interaction.followup.send(
            embeds=[HeaderEmbed, Embed],
            file=HFile,
            view=Detail_Panel()
        )
#-------------------------------

async def setup(bot):
	await bot.add_cog(Basic_Cmd(bot))