import discord
from discord.ext import commands
import datetime
import json
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
        All_Members = len(list(bot.get_all_members()))
        All_Guilds = bot.guilds
        
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{All_Members} Members & {len(All_Guilds)} Server!"
            )
        )
        print(f'[Logs] Message : Bot is running...\n[Logs] Connection : {int(bot.latency*1000)}ms\n[Logs] Member_Count : {All_Members}\n[Logs] Guild_count : {drawbar(len(All_Guilds), 15, 100)} | {len(All_Guilds)}')
    
    async def on_guild_join(self, guild):
        try:
            await Tree.sync(guild=guild)
        except Exception as e:
            print('Error :', e)

#-----------------------------------

bot = MyBot()
Tree = bot.tree
Color = 233087
Help_Str = json.loads(open('Help_Text.txt').read())
privguild = 979708145905594439

#-----------------------------------

@bot.command()
@commands.is_owner()
async def owner_sync(ctx):
    await Tree.sync()
    for guild in bot.guilds:
        try:
            await Tree.sync(guild=guild)
            print('[LOGS] SYNC DONE IN', guild.name)
        except Exception as e:
            print('[LOGS]', e, guild.name)

@bot.hybrid_command()
async def sync(ctx):
    try:
        await Tree.sync(guild=ctx.guild)
        await ctx.send('Done Syncing!')
    except Exception as e:
        await ctx.send(f'Error Was Occured : {e}')

@bot.hybrid_command()
async def help(ctx):
    f_user = ctx.author
    user_name = f_user.name
    Time = datetime.datetime.now()

    #-------------------
    
    Guild = bot.get_guild(privguild)

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
            await msg.edit(view=self)
    
    msg = await ctx.send(
        embed=Start_Embed,
        view=Help_Panel()
    )
            
#------------------

bot.run(f"{os.environ['TOKEN']}")
