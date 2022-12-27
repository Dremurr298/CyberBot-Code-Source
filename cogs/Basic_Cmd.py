import discord
import time
import random
import json
import datetime
from discord.ext import commands
from discord import app_commands

#-------------------------------

Color = 233087
Help_Str = json.loads(open('./Help_Text.txt').read())
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

    @app_commands.command(name="help")
    async def help(self, interaction: discord.Interaction) -> None:
        """For searching an command!"""
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

        Start_Embed = discord.Embed(
            title=f'{Emoji_1} | {user_name} Help Panel',
            description=(
                '> Please select a category in the selectmenu at the bottom\n'
                '> of the embed To see the spesific command.\n'
                '⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n'
                '> `[<<]   |` Go to left\n'
                '> `[>>]   |` Go to right\n'
                '> `[HOME] |` Go to start of the page\n'
                '> `[END]  |` End the interaction'
            ),
            color=Color
        )
        Start_Embed.set_footer(text=f'Executor : {user_name} | {Time}')
        Desc_Embed_Dict = [
            (
                '> **Sync Command**\n'
                '```This is place to see a sync command,\n'
                'although the bot is automatically sync when joined the guild\n'
                'there is some situation that need to be sync again```\n'
                '⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n'
                '> Total Command : {TCOMMAND}\n'
                '> List Command :\n'
                '```{LCMD}```\n'
                '⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n'
            ),
            (
                '> **Bot Owner Command**\n'
                '```Sometimes i forgot what is command to do something\n'
                "and I'm lazy to look through the code. its need lot of scroll..```\n"
                '⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n'
                '> Total Command : {TCOMMAND}\n'
                '> List Command :\n'
                '```{LCMD}```\n'
                '⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n'
            ),
            (
                '> **Basic and Fun command**\n'
                '```This is place to see basic / fun command\n'
                'like /help, /howgay, /hownerd or /ping...```'
                '⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n'
                '> Total Command : {TCOMMAND}\n'
                '> List Command :\n'
                '```{LCMD}```\n'
                '⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n'
            ),
            (
                '> **Economy command**\n'
                '```This is place to see economy command,\n'
                'like /start, /work, /account, etc```\n'
                '⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n'
                '> Total Command : {TCOMMAND}\n'
                '> List Command :\n'
                '```{LCMD}```\n'
                '⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n'
            )
                
        ]
        
        Command_Cat_T = len([s for s in Help_Str['command']])
        Sellect_Category = []
        
        for count in range(Command_Cat_T):
            Category_name = f"{Help_Str['command'][count]['name']}"
            Sellect_Category.append(
                discord.SelectOption(
                    label=Category_name,
                    value=count,
                    description=f'Page Contains About {Category_name}'
                )
            )

        class Help_Panel(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.Category_Track = 0
                self.Help_Track = 0
                self.max_track = 0

                self.right_button.disabled = True
                self.left_button.disabled = True
                self.home_button.disabled = True
                self.end_button.disabled = False
            
            @discord.ui.select(placeholder='Select The Category',max_values=1,min_values=1,options=Sellect_Category)
            async def Help_Panel(self, interaction, select:discord.ui.Select):
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

                self.Help_Track = 0
                self.Category_Track = int(self.Help_Panel.values[0])
                base_dict = Help_Str['command'][self.Category_Track]
                ins_base_dict = base_dict['commands'][self.Help_Track]

                cmd_name = ins_base_dict['name']
                cmd_desc = ins_base_dict['Desc']
                cmd_usage = ins_base_dict['Usage']
                cmd_list = []

                for count_hold in range(len(base_dict['commands'])):
                    cmd_list.append(base_dict['commands'][count_hold]['name'])

                self.max_track = int(len(cmd_list))
                cmd_list = ', '.join(cmd_list)
                
                replace_dict = f'{Desc_Embed_Dict[int(self.Category_Track)]}'.replace("{TCOMMAND}",f"{base_dict['amount']}")
                replace_dict = f'{replace_dict.replace("{LCMD}",f"{cmd_list}")}'

                show_desc = (
                    f'{replace_dict}\n'
                    f'> **{cmd_name}**\n'
                    f'```{cmd_desc}```\n'
                    f'⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n'
                    f'Usage : {cmd_usage}'
                )

                await interaction.response.defer()
                Embed = discord.Embed(
                    title=f'{Emoji_1} | {user_name} Help Panel',
                    description=f'{show_desc}',
                    color=Color
                )
                Start_Embed.set_footer(text=f'Executor : {user_name} | {Time}')

                if self.max_track == 1:
                    self.left_button.disabled = True
                    self.right_button.disabled = True

                else:
                    self.right_button.disabled = False
                
                self.home_button.disabled = False
                self.end_button.disabled = False

                await interaction.message.edit(
                    embed=Embed,
                    view=self
                )
                
            @discord.ui.button(label='[<<]',style=discord.ButtonStyle.green)
            async def left_button(self, interaction, button:discord.ui.Button):
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

                await interaction.response.defer()
                
                self.Help_Track -= 1
                if self.Help_Track <= 0:
                    if self.max_track == 1:
                        self.left_button.disabled = True
                        self.right_button.disabled = True
                    
                    else:
                        self.left_button.disabled = True

                    self.home_button.disabled = False
                    self.end_button.disabled = False
                    self.Help_Track = 0
                
                else:
                    self.right_button.disabled = False

                base_dict = Help_Str['command'][self.Category_Track]
                ins_base_dict = base_dict['commands'][self.Help_Track]

                cmd_name = ins_base_dict['name']
                cmd_desc = ins_base_dict['Desc']
                cmd_usage = ins_base_dict['Usage']
                cmd_list = []

                for count_hold in range(len(base_dict['commands'])):
                    cmd_list.append(base_dict['commands'][count_hold]['name'])

                cmd_list = ', '.join(cmd_list)
                
                replace_dict = f'{Desc_Embed_Dict[int(self.Category_Track)]}'.replace("{TCOMMAND}",f"{base_dict['amount']}")
                replace_dict = f'{replace_dict.replace("{LCMD}",f"{cmd_list}")}'

                show_desc = (
                    f'{replace_dict}\n'
                    f'> **{cmd_name}**\n'
                    f'```{cmd_desc}```\n'
                    f'⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n'
                    f'Usage : {cmd_usage}'
                )
                Embed = discord.Embed(
                    title=f'{Emoji_1} | {user_name} Help Panel',
                    description=f'{show_desc}',
                    color=Color
                )
                Start_Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                await interaction.message.edit(
                    embed=Embed,
                    view=self
                )

            @discord.ui.button(label='[>>]',style=discord.ButtonStyle.green)
            async def right_button(self, interaction, button:discord.ui.Button):
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

                await interaction.response.defer()
                self.Help_Track += 1
                if self.Help_Track == (self.max_track-1):
                    if self.max_track == 1:
                        self.left_button.disabled = True
                        self.right_button.disabled = True
                    
                    else:
                        self.right_button.disabled = True

                    self.home_button.disabled = False
                    self.end_button.disabled = False
                
                else:
                    self.left_button.disabled = False
                
                base_dict = Help_Str['command'][self.Category_Track]
                ins_base_dict = base_dict['commands'][self.Help_Track]

                cmd_name = ins_base_dict['name']
                cmd_desc = ins_base_dict['Desc']
                cmd_usage = ins_base_dict['Usage']
                cmd_list = []

                for count_hold in range(len(base_dict['commands'])):
                    cmd_list.append(base_dict['commands'][count_hold]['name'])

                cmd_list = ', '.join(cmd_list)
                
                replace_dict = f'{Desc_Embed_Dict[int(self.Category_Track)]}'.replace("{TCOMMAND}",f"{base_dict['amount']}")
                replace_dict = f'{replace_dict.replace("{LCMD}",f"{cmd_list}")}'

                show_desc = (
                    f'{replace_dict}\n'
                    f'> **{cmd_name}**\n'
                    f'```{cmd_desc}```\n'
                    f'⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n'
                    f'Usage : {cmd_usage}'
                )
                Embed = discord.Embed(
                    title=f'{Emoji_1} | {user_name} Help Panel',
                    description=f'{show_desc}',
                    color=Color
                )
                Start_Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                await interaction.message.edit(
                    embed=Embed,
                    view=self
                )
        
            @discord.ui.button(label='[HOME]',style=discord.ButtonStyle.red)
            async def home_button(self, interaction, button:discord.ui.Button):
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
                
                await interaction.response.defer()

                self.right_button.disabled = True
                self.left_button.disabled = True
                self.home_button.disabled = True

                await interaction.message.edit(
                    embed=Start_Embed,
                    view=self
                )
        
            @discord.ui.button(label='[END]')
            async def end_button(self, interaction, button:discord.ui.Button):
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
                
                await interaction.response.defer()
                for child in self.children:
                    child.disabled = True
                
                await interaction.message.edit(
                    view=self
                )

            async def on_timeout(self):
                self.home_button.disabled = True
                self.end_button.disabled = True
                self.right_button.disabled = True
                self.left_button.disabled = True
                await interaction.edit_original_message(view=self)
        
        await interaction.followup.send(
            embed=Start_Embed,
            view=Help_Panel()
        )
                

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