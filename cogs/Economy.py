import os
import discord
import random
import pymongo
import json
import time
import datetime
from discord.ext import commands
from discord import app_commands
from discord import ui

#--------------------------------

client = pymongo.MongoClient(os.environ['DBLINK'])
db = client.Data
cursor = db['Economy_Data']
q_cursor = db['Question_Data']
s_cursor = db['Shop_Data']
privguild = 979708145905594439
color = 233087

#--------------------------------

def drawbar(amount, length, m_length):
    # just a drawbar function that i use...
    return f"{'█'*round(int(amount)/(m_length/length)):◦<{length}}"

def custom_drawbar(amount, length, m_length, reached_emoji, not_reached_emoji):
    # same as before just a drawbar but the indicator (Bars) can be customize
    return f"{f'{reached_emoji}'*round(int(amount)/(m_length/length)):{not_reached_emoji}<{length}}"

def get_cooldown(Id, cooldown):
    # getting the time.time() seconds that saved in db
    # the time now will reduce by time that saved in db
    # if the result is actually below 0 that mean
    # the cd is done or the cmd can be use again
    # for checking again 
    # im doing that calculation outside the func
    # yea thats little pain lmao
    # if u dont understand ... i dont care :D

    user = cursor.find_one({'id':Id})                             # Getting The User

    if user['Cooldown_Data'][cooldown] == 0:
        return [0, 'None']

    var_time = int(time.time() - user['Cooldown_Data'][cooldown]) # seconds / raw
    flex_time = f'{datetime.timedelta(seconds = var_time)}'       # Good Lookings Time

    return [var_time, flex_time]

def change_cooldown(Id, cooldown):
    # reward / work cooldown changer for cyberbot
    # yea im using a fkin time.time() :)

    user = cursor.find_one({'id':Id})
    user_data = dict(user)

    user_data['Cooldown_Data'][cooldown] = time.time()
    cursor.update_many({'id':Id},{'$set':{
        'Cooldown_Data':user_data['Cooldown_Data']
    }})

    return 'Done'

def inspect_time(seconds, str_date):
    # this func just making a raw timedelta like '1 day, 02:04:02' become
    # like this '1D : 02h : 04m : 02s'

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

def reward_list(reward):
    # an cyberbot hourly / daily / weekly / moonthly reward function
    # its just giv an dict that im using for give user reward
    # with this i dont need to spesifically writin the reward

    if reward.lower() == 'hourly':
        return {
            'Money':1000,
            'Exp':250,
            'ID':'HR_CD'
        }
    
    elif reward.lower() == 'daily':
        return {
            'Money':5000,
            'Exp':500,
            'ID':'DR_CD'
        }
    
    elif reward.lower() == 'weekly':
        return {
            'Money':15000,
            'Exp':650,
            'ID':'WR_CD'
        }
    
    elif reward.lower() == 'moonthly':
        return {
            'Money':20000,
            'Exp':1000,
            'ID':'MR_CD'
        }
    
    else:
        return None

def reward_cdls(reward):
    # contain an reward cooldown list
    # im using it for reward command

    if reward.lower() == 'hourly':
        return 3600
    
    elif reward.lower() == 'daily':
        return 86400
    
    elif reward.lower() == 'weekly':
        return 604800
    
    elif reward.lower() == 'moonthly':
        return 2592000
    
    else:
        return None

def Item_Time(IDS):
    # contain a list of item time
    # just ignore it lmfao

    if IDS == 'Xp_Boost':
        return 900

    elif IDS == 'C_Boost':
        return 14400

    elif IDS == 'Sal_Boost':
        return 1200

    elif IDS == 'S_Booster':
        return 18000

    elif IDS == 'V_Boost':
        return 18000

def effect_time(user, Item):
    # same as get_cooldown but more complex with inspect_time func inside of it
    # its really2 hard to write for me. 'this is not that hard ' stfu, i made it myself >:(

    res = cursor.find_one({'id':user})
    time_now = int(time.time())
    time_dbs = res['Item_Time']['Item_DT'][Item]
    max_time = res['Item_Time'][Item]

    if time_dbs is None or time_dbs == 'None' or time_dbs == 0:
        return '00D : 00h : 00m : 00s','None'

    try:
        minus = time_now - time_dbs
    except Exception as E:
        return E
    
    if minus >= max_time:
        return '00D : 00h : 00m : 00s','None'

    else:
        max_time -= minus
        deltas = datetime.timedelta(seconds=max_time)
        show = deltas

        if max_time >= 86400:
            time_left = int(max_time)
            shows = str(show).split()
            shows = f"{shows[2].split('.', 2)[0]}"
            shows = shows.replace(":", " ")
            shows = shows.split()
            shows = f"{shows[0]}D : {shows[1]}h : {shows[2]}m : {shows[3]}"
            return shows,time_left

        else:
            time_left = int(max_time)
            shows = str(show).split()
            shows = f"{shows[0].split('.', 2)[0]}"
            shows = shows.replace(':',' ')
            shows = shows.split()
            shows = f"00D : {shows[0]}h : {shows[1]}m : {shows[2]}s"
            return shows,time_left

def effect_time_add(user, Item, multi:int=1):
    res = cursor.find_one({'id':user})

    time_now = int(time.time())
    seconds_left = effect_time(user, Item)

    if seconds_left[1] == 'None':
        seconds_left = ['holder',0]

    res['Item_Time'][Item] = seconds_left[1] + (Item_Time(Item) * multi)
    res['Item_Time']['Item_DT'][Item] = time.time()
    cursor.update_many({'id':res['id']},{'$set':{
        'Item_Time':res['Item_Time']
    }})

    return 'Done'

class Economy_Cmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name='start')
    async def start(self, interaction: discord.Interaction):
        """Create A CyberBot Account!"""
        await interaction.response.defer()

        f_user = interaction.user
        user_id = f_user.id
        user_name = f_user.name
        user_pfp = f_user.display_avatar
        check = cursor.find_one({'id':user_id})
        Time = datetime.datetime.now()

        #-------------------
        
        Guild = self.bot.get_guild(privguild)

        Emoji_1 = discord.utils.get(Guild.emojis, name='CYBUSER')
        Emoji_2 = discord.utils.get(Guild.emojis, name='CYBTUBE')
        Emoji_3 = discord.utils.get(Guild.emojis, name='PROGRAMMING')
        Emoji_4 = discord.utils.get(Guild.emojis, name='CYBERPROFESSION')

        #-------------------

        if check is None:
            Embed = discord.Embed(
                title=f'{Emoji_4} | Select The Jobs!',
                description=(
                    f'> {Emoji_2} | **CyberTuber**\n'
                    '> *Make videos and earn money from them!*\n\n'

                    '> This Jobs is really easy, you just need to\n'
                    '> make a video then post it. you can get a money\n'
                    '> from it after you get **Monetize Sertificate**\n\n'

                    '━━━━━━━━━━━━━━━━━━━━━━━━━\n\n'

                    f'> {Emoji_3} | **CyberProgramming**\n'
                    '> *Answer an question about code an earn money!*\n\n'

                    '> This jobs quitely not easy, not everyone is\n'
                    '> a programmer. but even the answer is wrong\n'
                    '> you still get a money!'
                ),
                color=color
            )
            Embed.set_footer(text=f'Executor : {user_name} | {Time}')
            Embed.set_thumbnail(url=user_pfp.url)
            
            class Bio_edit(ui.Modal,title='User Bio'):
                Bio = ui.TextInput(
                    label='Bio...',
                    style=discord.TextStyle.paragraph,
                    placeholder='Write your own bio here...',
                    required=True,
                    max_length=600
                )

                async def on_submit(self, interaction):
                    await interaction.response.defer()
                    self.value = self.Bio.value
                    self.stop()

            class Start_Menu(discord.ui.View):
                def __init__(self):
                    super().__init__()
                    self.user_data = 'None'
                    self.Done_button.disabled = True
                    self.Edit_bio_button.disabled = True

                @ui.select(placeholder='Select The Jobs',max_values=1,min_values=1,options=[
                    discord.SelectOption(
                        label=f'CyberTuber',
                        value='Select1',
                        description='Select a CyberTuber Jobs',
                        emoji=Emoji_2
                    ),
                    discord.SelectOption(
                        label=f'CyberProgrammer',
                        value='Select2',
                        description='Select a CyberProgrammer Jobs',
                        emoji=Emoji_3
                    )
                ])
                async def Jobs_DropDown(self, interaction, select:discord.ui.Select):
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
                    if select.values[0] == 'Select1':
                        Data = {
                            'id':user_id,
                            'WEBID':f'{user_id}', # For Website account searching
                            'name':user_name,
                            'bio':'> `None`',
                            'N_economy_Data':{
                                'Money':1000,
                                'NetWorth':0,
                                'Shard':0,
                                'Level':1,
                                'MaxExp':100,
                                'Exp':0
                            },
                            'Jobs_Data':{
                                'CJobs':'CyberTuber',
                                'CName':f'{user_name} Channel', # Channel Name
                                'CSubs':10,             # Total Subs
                                'CView':0,             # Total View
                                'CLike':0,             # Total Like
                                'CDislike':0,          # Total dislike
                                'CSertificate':'None', # Monetize sertificate
                                'CVideo':[],           # Video List (user made it)
                                'CLive':{              # Live Data
                                    'Last_for':'None', # Datetime object
                                    'N_Live':'None'    # Livename
                                }
                            },
                            'Cooldown_Data':{
                                'W_CD':0,  # Work cd
                                'HR_CD':0, # hourly reward cd
                                'DR_CD':0, # daily reward cd
                                'WR_CD':0, # weekly reward cd
                                'MR_CD':0  # monthly reward cd
                            },
                            'Item_Data':{
                                'S_Boost':0,  # Subs Booster
                                'C_Boost':0,  # Cooldown Reducer
                                'V_Boost':0,  # View Booster
                                'Xp_Boost':0, # XP booster
                                'AD_sd':0     # Ancient Data
                            },
                            'Item_Time': {
                                "Item_DT": {
                                  "S_Boost": 0, # Subs Booster Datetime object
                                  "V_Boost": 0, # View Booster Datetime Object
                                  "C_Boost": 0, # Cooldown Reducer Datetime Object
                                  "Xp_Boost": 0 # XP Booster Datetime Object
                                },
                                "S_Boost": 0, # Subs Booster Time
                                "V_Boost": 0, # View Booster Time
                                "C_Boost": 0, # Coldown Reducer Time
                                "Xp_Boost": 0 # XP booster Time
                            } 
                        }
                        self.user_data = Data
                        self.Done_button.disabled = False
                        self.Edit_bio_button.disabled = False
                        await interaction.edit_original_message(view=self)
                        await interaction.followup.send(
                            content='Selected : CyberTuber',
                            ephemeral=True
                        )

                    else:
                        Data = {
                            'id':user_id,
                            'WEBID':f'{user_id}', # For Website account searching
                            'name':user_name,
                            'bio':'> `None`',
                            'N_economy_Data':{
                                'Money':1000,
                                'NetWorth':0,
                                'Shard':0,
                                'Level':1,
                                'MaxExp':100,
                                'Exp':0
                            },
                            'Jobs_Data':{
                                'CJobs':'CyberProgramming',
                                'CSall':100, # Money that use get when answer question (only when right)
                                'CQuest':0   # Total Quest Right
                            },
                            'Cooldown_Data':{
                                'W_CD':0,  # Work cd
                                'HR_CD':0, # hourly reward cd
                                'DR_CD':0, # daily reward cd
                                'WR_CD':0, # weekly reward cd
                                'MR_CD':0  # moonthly reward cd
                            },
                            'Item_Data':{
                                'Sal_Boost':0, # Sallary Booster
                                'C_Boost':0,   # Cooldown Reducer
                                'Xp_Boost':0,  # XP booster
                                'AD_sd':0      # Ancient Data
                            },
                            'Item_Time': {
                                "Item_DT": {
                                  "Sal_Boost": 0, # Sallary Booster Datetime object
                                  "C_Boost": 0,   # Cooldown Reducer Datetime Object
                                  "Xp_Boost": 0   # XP Booster Datetime Object
                                },
                                "Sal_Boost": 0, # Sallary Booster time
                                "C_Boost": 0,   # Coldown Reducer Time
                                "Xp_Boost": 0   # XP booster Time
                            } 
                        }
                        self.user_data = Data
                        self.Done_button.disabled = False
                        self.Edit_bio_button.disabled = False
                        await interaction.edit_original_message(view=self)
                        await interaction.followup.send(
                            content='Selected : CyberProgramming',
                            ephemeral=True
                        )

                @ui.button(label='Done',style=discord.ButtonStyle.green)
                async def Done_button(self, interaction, button:discord.ui.Button):
                    user = f_user
                    user_id = user.id
                    user_name = user.name
                    user_pfp = user.display_avatar.url
                    inter_id = interaction.user.id
                    User_data = self.user_data

                    if inter_id != user_id:
                        await interaction.response.defer()
                        await interaction.followup.send(
                            content=f'Sorry This Menu is controlled by {user_name}',
                            ephemeral=True
                        )
                        return inter_id == user_id

                    await interaction.response.defer()
                    Embed = discord.Embed(
                        title='[‼️] | IMPORTANT',
                        description=(
                            "```\nREMEMBER this is just a discord bot game.\n"
                            "Its just for fun. You don't have to \nbe serious about playing it.\n"
                            "Follow discord rules and our rules!\n```"

                            "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            '```\nRules :\n\n'

                            '1. Follow the rules of discord (TOS)\n'
                            '2. No cheating\n'
                            '3. No exploit errors/bugs\n'
                            '4. Have fun\n```'
                            '━━━━━━━━━━━━━━━━━━━━━━━━━'
                        ),
                        color=color
                    )
                    Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                    Embed.set_thumbnail(url=user_pfp)

                    class Accepting_TOS(discord.ui.View):
                        def __init__(self):
                            super().__init__()

                        @ui.button(label='OK',style=discord.ButtonStyle.green)
                        async def Accept_Button(self, interaction, button: discord.ui.Button):
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
                            cursor.insert_one(User_data)
                            self.Accept_Button.disabled = True
                            self.N_Accept_Button.disabled = True
                            await interaction.edit_original_message(view=self)
                            await interaction.followup.send(
                                content='Successfully Create Account!',
                                ephemeral=True
                            )
                        
                        @ui.button(label='NO',style=discord.ButtonStyle.red)
                        async def N_Accept_Button(self, interaction, button: discord.ui.Button):
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

                            self.Accept_Button.disabled = True
                            self.N_Accept_Button.disabled = True
                            await interaction.response.defer()
                            await interaction.edit_original_message(view=self)
                        
                        async def on_timeout(self):
                            self.Accept_Button.disabled = True
                            self.N_Accept_Button.disabled = True
                            await interaction.edit_original_message(view=self)

                    Accept_View = Accepting_TOS()
                    await interaction.edit_original_message(
                        embed=Embed,
                        view=Accept_View
                    )

                @ui.button(label='Edit Bio',style=discord.ButtonStyle.green)
                async def Edit_bio_button(self, interaction, buttoh:discord.ui.Button):
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
                    
                    modal = Bio_edit()
                    await interaction.response.send_modal(modal)

                    Data = await modal.wait()
                    self.user_data['bio'] = modal.value

                    await interaction.followup.send(
                        content='Successfully Set Bio',
                        ephemeral=True
                    )

                @ui.button(label='❌')
                async def Cancel_button(self, interaction, button:discord.ui.Button):
                    user = user
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
                    
                    self.Jobs_DropDown.disabled = True
                    self.Cancel_button.disabled = True
                    self.Done_button.disabled = True
                    self.Edit_bio_button.disabled = True
                    await interaction.response.defer()
                    await interaction.edit_original_message(view=self)
                    await interaction.followup.send(
                        content='Successfully Canceled',
                        ephemeral=True
                    )

                async def on_timeout(self):
                    self.Jobs_DropDown.disabled = True
                    self.Cancel_button.disabled = True
                    self.Done_button.disabled = True
                    self.Edit_bio_button.disabled = True
                    await interaction.edit_original_message(view=self)

            view = Start_Menu()
            await interaction.followup.send(
                embed=Embed,
                view=view
            )
            return

        else:
            Embed = discord.Embed(
                title=f'{Emoji_1} | Failed To Creating Account',
                description=f'> Sorry {user_name}. you can only have 1 account!',
                color=color
            )
            Embed.set_footer(text=f'Executor : {user_name} | {Time}')
            Embed.set_thumbnail(url=user_pfp.url)
            await interaction.followup.send(embed=Embed)
            return

    @app_commands.command(name='account')
    async def Account(self, interaction: discord.Interaction):
        """See Your Account Profile!"""
        await interaction.response.defer()

        user = interaction.user
        user_id = user.id
        user_pfp = user.display_avatar.url
        user_name = user.name
        
        #-------------------
        
        Guild = self.bot.get_guild(privguild)

        Emoji_1 = discord.utils.get(Guild.emojis, name='CYBLEVEL')
        Emoji_2 = discord.utils.get(Guild.emojis, name='CYBMONEY')
        Emoji_3 = discord.utils.get(Guild.emojis, name='CYBSUBS')
        Emoji_4 = discord.utils.get(Guild.emojis, name='CYBTUBE')
        Emoji_5 = discord.utils.get(Guild.emojis, name='CYBUSER')
        Emoji_6 = discord.utils.get(Guild.emojis, name='CYBLIKE')
        Emoji_7 = discord.utils.get(Guild.emojis, name='CYBDISLIKE')
        Emoji_8 = discord.utils.get(Guild.emojis, name='PROGRAMMING')
        Emoji_9 = discord.utils.get(Guild.emojis, name='CYBERPROFESSION')
        Emoji_10 = discord.utils.get(Guild.emojis, name='CYBEXP')
        Emoji_11 = discord.utils.get(Guild.emojis, name='CYBCOOLDOWN')
        Emoji_13 = discord.utils.get(Guild.emojis, name='CYBSALLARY')
        Emoji_14 = discord.utils.get(Guild.emojis, name='CYBQDONE')
        Emoji_15 = discord.utils.get(Guild.emojis, name='CYBREADY')
        Emoji_16 = discord.utils.get(Guild.emojis, name='CYBNREADY')
        Emoji_17 = discord.utils.get(Guild.emojis, name='CYBSHARD')
        Emoji_18 = discord.utils.get(Guild.emojis, name='CYBERVIEW')

        #-------------------

        check = cursor.find_one({'id':user_id})
        Time = datetime.datetime.utcnow()

        if check is None:
            Embed = discord.Embed(
                title=f'{Emoji_1} | Command Failed',
                description=f'> Sorry {user_name}. you`re not create an account yet.\n> Please Create an account with command ***/start!***',
                color=color
            )
            Embed.set_footer(text=f'Executor : {user_name} | {Time}')
            Embed.set_thumbnail(url=user_pfp)
            await interaction.followup.send(embed=Embed)
            return
        
        else:
            Jobs = check['Jobs_Data']['CJobs']

            if Jobs == 'CyberTuber':

                #Normal Stats
                CBio = check['bio']
                Money = check['N_economy_Data']['Money']
                Nworth = check['N_economy_Data']['NetWorth']
                Shard = check['N_economy_Data']['Shard']
                Level = check['N_economy_Data']['Level']
                Exp = check['N_economy_Data']['Exp']
                MaxExp = check['N_economy_Data']['MaxExp']
                
                #Jobs Stats
                CJobs = check['Jobs_Data']['CJobs']
                CName = check['Jobs_Data']['CName']
                CSubs = check['Jobs_Data']['CSubs']
                CView = check['Jobs_Data']['CView']
                CLike = check['Jobs_Data']['CLike']
                CDlike = check['Jobs_Data']['CDislike']
                CTVideo = len(check['Jobs_Data']['CVideo'])
                CSertificate = check['Jobs_Data']['CSertificate']

                Embed = discord.Embed(
                    title=f'{Emoji_5} | {user_name} Account',
                    description=(
                        f'{Emoji_5} | `Name    :` `{user_name}`\n'           # user name
                        f'{Emoji_2} | `Money   :` `{Money:,}`\n'             # user money
                        f'{Emoji_2} | `NWorth  :` `{Nworth:,}`\n'            # user networth
                        f'{Emoji_17} | `Shard   :` `{Shard:,}`\n'            # user shard
                        f'{Emoji_1} | `Level   :` `{Level:,}`\n'             # user level
                        f'{Emoji_10} | `Exp     :` `{Exp:,}`/{MaxExp:,}\n'   # user exp and max exp
                        f'━━━━━━━━━━━━━━━━━━━━━━━━━\n'      
                        f'{CBio}\n'                                          # user bio
                        f'━━━━━━━━━━━━━━━━━━━━━━━━━\n'  
                        f'{Emoji_9} | `CJobs                  :` `{CJobs}`\n'              # user jobs
                        f'{Emoji_4} | `CName                  :` `{CName}`\n'              # Channel Name
                        f'{Emoji_3} | `CSubs                  :` `{CSubs:,}`\n'            # user total subscriber
                        f'{Emoji_18} | `CView                  :` `{CView:,}`\n'           # user total views
                        f'{Emoji_6} | `CLike                  :` `{CLike:,}`\n'            # user total likes
                        f'{Emoji_7} | `CDLike                 :` `{CDlike:,}`\n'           # user total dislike
                        f'{Emoji_4} | `C-Total-Video          :` `{CTVideo:,}`\n'          # user total video
                        f'{Emoji_4} | `C-Monetize-Sertificate :` `{CSertificate}`'         # user sertificate
                    ),
                    color=color
                )
                Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                Embed.set_thumbnail(url=user_pfp)
                await interaction.followup.send(embed=Embed)

            else:

                #Normal Stats
                CBio = check['bio']
                Money = check['N_economy_Data']['Money']
                Nworth = check['N_economy_Data']['NetWorth']
                Shard = check['N_economy_Data']['Shard']
                Level = check['N_economy_Data']['Level']
                Exp = check['N_economy_Data']['Exp']
                MaxExp = check['N_economy_Data']['MaxExp']

                #Jobs Stats
                QDone = check['Jobs_Data']['CQuest']
                CJobs = check['Jobs_Data']['CJobs']
                CSall = check['Jobs_Data']['CSall']

                Embed = discord.Embed(
                    title=f'{Emoji_5} | {user_name} Account',
                    description=(
                        f'{Emoji_5} | Name : `{user_name}`\n'        # user name
                        f'{Emoji_2} | Money : `{Money:,}`\n'         # user money
                        f'{Emoji_2} | NWorth : `{Nworth:,}`\n'       # user networth
                        f'{Emoji_17} | Shard : `{Shard:,}`\n'        # user shard
                        f'{Emoji_1} | Level : `{Level:,}`\n'         # user level
                        f'{Emoji_10} | Exp : `{Exp:,}/{MaxExp:,}`\n' # user exp and max exp
                        f'━━━━━━━━━━━━━━━━━━━━━━━━━\n'
                        f'{CBio}\n'                                  # user BIO
                        f'━━━━━━━━━━━━━━━━━━━━━━━━━\n'
                        f'{Emoji_9} | CJobs : `{CJobs}`\n'
                        f'{Emoji_14} | CQdone : `{QDone}`\n'
                        f'{Emoji_13} | CSall : `{CSall:,}`'
                    ),
                    color=color
                )
                Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                Embed.set_thumbnail(url=user_pfp)
                await interaction.followup.send(embed=Embed)

    @app_commands.command(name='work')
    async def work(self, interaction: discord.Interaction):
        """Lets Earn Some Money!"""
        await interaction.response.defer()

        user = interaction.user
        user_id = user.id
        user_pfp = user.display_avatar.url
        user_name = user.name

        #----------

        Guild = self.bot.get_guild(privguild)

        Emoji_1 = discord.utils.get(Guild.emojis, name='CYBUSER')
        Emoji_2 = discord.utils.get(Guild.emojis, name='CYBERTUBE')
        Emoji_3 = discord.utils.get(Guild.emojis, name='CYBSUBS')
        Emoji_4 = discord.utils.get(Guild.emojis, name='CYBERVIEW')
        Emoji_5 = discord.utils.get(Guild.emojis, name='CYBLIKE')
        Emoji_6 = discord.utils.get(Guild.emojis, name='CYBDISLIKE')
        Emoji_7 = discord.utils.get(Guild.emojis, name='CYBMONEY')
        Emoji_8 = discord.utils.get(Guild.emojis, name='CYBERPROFESSION')
        #----------

        check = cursor.find_one({'id':user_id})
        Time = datetime.datetime.now()

        if check is None:
            Embed = discord.Embed(
                title=f'{Emoji_1} | Command Failed',
                description=f'> Sorry {user_name}. you`re not create an account yet.\n> Please Create an account with command ***/start!***',
                color=color
            )
            Embed.set_footer(text=f'Executor : {user_name} | {Time}')
            Embed.set_thumbnail(url=user_pfp)
            await interaction.followup.send(embed=Embed)
            return
        
        else:
            Job = check['Jobs_Data']['CJobs']
            cd = get_cooldown(user_id, 'W_CD')

            if cd[0] != 0:
                if cd[0] < 60:
                    var_wait = 60 - cd[0]
                    Embed = discord.Embed(
                        title = f'{Emoji_8} | Work Failed',
                        description = f'> Please wait for `{datetime.timedelta(seconds=var_wait)}s`!',
                        color = color
                    )
                    Embed.set_footer(text=f'Executor : {user.name} | {Time}')
                    await interaction.followup.send(embed=Embed)
                    return

            if Job == 'CyberTuber':
                CSubs = check['Jobs_Data']['CSubs']
                CSert = check['Jobs_Data']['CSertificate']

                #------

                Embed = discord.Embed(
                    title=f'{Emoji_2} | Making Video...',
                    description=(
                        f'> Click the button bellow this embed to make\n'
                        f'> Video and earn a subs, like, and ofc **money!**\n'
                        f'> ~~*only if you had an monetize sertificate*~~'
                    ),
                    color=color
                )
                Embed.set_footer(text=f'Executor : {user_name} | {Time}')

                class Video_Modal(ui.Modal,title='Make A Video!'):
                    Video_Title = ui.TextInput(
                        label = 'Video Title',
                        placeholder = 'Put your video title here',
                        max_length = 32,
                        style = discord.TextStyle.short,
                        required = True
                    )

                    Video_desc = ui.TextInput(
                        label = 'Video Description',
                        placeholder = 'Put your video description here',
                        max_length = 250,
                        style = discord.TextStyle.paragraph,
                        default='> `None`'
                    )

                    async def on_submit(self, interaction):
                        await interaction.response.defer()
                        self.value = [self.Video_Title.value, self.Video_desc.value]
                        self.stop()
                
                class Make_Video_BT(discord.ui.Button):
                    def __init__(self):
                        super().__init__(
                            label = 'Make a Video',
                            style = discord.ButtonStyle.green
                        )
                    
                    async def callback(self, interaction):
                        inter_id = interaction.user.id

                        if inter_id != user_id:
                            await interaction.response.defer()
                            await interaction.followup.send(
                                content = f'Sorry, only {user_name} can use this button!',
                                ephemeral = True
                            )
                            return inter_id == user_id
                        else:
                            modal = Video_Modal()
                            await interaction.response.send_modal(modal)
                            await modal.wait()
                            
                            Video_Name = modal.value[0]
                            Video_Desc = modal.value[1]

                            G_View = random.randint(1,CSubs)
                            G_Subs = int(G_View / random.uniform(1,4.25))
                            G_Like = int(G_View / random.uniform(1,2.56))
                            G_DLike = int(G_Like / random.uniform(1,1.54))
                            
                            if CSert != 'None':
                                G_Money = int(random.randint(1,G_View)) * 5
                            else:
                                G_Money = 0

                            Embed = discord.Embed(
                                title=f'{Emoji_2} | {Video_Name}',
                                description=(
                                    f'━━━━━━━━━━━━━━━━━━━━━━━━━\n'
                                    f'{Video_Desc}\n'
                                    f'━━━━━━━━━━━━━━━━━━━━━━━━━\n'
                                    f'{Emoji_3} | `Subs     : +{G_Subs:,}`\n'
                                    f'{Emoji_4} | `Views    : +{G_View:,}`\n'
                                    f'{Emoji_5} | `Likes    : +{G_Like:,}`\n'
                                    f'{Emoji_6} | `Dislikes : +{G_DLike:,}\n`'
                                    f'{Emoji_7} | `Money    : +{G_Money}`'
                                ),
                                color=color
                            )
                            Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                            await interaction.edit_original_message(
                                embed = Embed,
                                view = None
                            )
                            change_cooldown(user_id, 'W_CD')

                            check = cursor.find_one({'id':user_id})
                            check_ = check['N_economy_Data']
                            check = check['Jobs_Data']

                            DB1 = check['CSubs'] + G_Subs
                            DB2 = check['CView'] + G_View
                            DB3 = check['CLike'] + G_Like
                            DB4 = check['CDislike'] + G_DLike
                            DB5 = check_['NetWorth'] + G_Money
                            DB6 = check_['Money'] + G_Money

                            check['CSubs'] = DB1
                            check['CView'] = DB2
                            check['CLike'] = DB3
                            check['CDislike'] = DB4
                            check_['NetWorth'] = DB5
                            check_['Money'] = DB6
                            check['CVideo'].append(f'{Video_Name}')

                            cursor.update_many(
                                {'id':user_id},{'$set':{
                                    'Jobs_Data':check,
                                    'N_Economy_Data':check_
                                }}
                            )
                            change_cooldown(user_id, 'W_CD')

                    
                    async def on_timeout(self):
                        self.disabled = True
                        await interaction.edit_original_message(view=self)

                view = discord.ui.View()
                view.add_item(Make_Video_BT())
                await interaction.followup.send(
                    embed = Embed,
                    view = view
                )

            else:
                Sall = check['Jobs_Data']['CSall']
                Question_Done = check['Jobs_Data']['CQuest']
                Work_Turn = random.randint(2,5)
                Question_Len = len(list(q_cursor.find({})))
                Question_List = []

                for x in range(0,Work_Turn):
                    Qid = f'Qid{random.randint(0,(Question_Len-1))}'
                    Get_Question = q_cursor.find_one({'Qid':Qid})

                    Question = Get_Question['Question']
                    A = Get_Question['Answer']['A']
                    B = Get_Question['Answer']['B']
                    C = Get_Question['Answer']['C']
                    Right_Answer = Get_Question['R_Answer']

                    Put_Data = {
                        'Embed_description':(
                            f'{Question}\n'
                            '━━━━━━━━━━━━━━━━━━━━━━━━━\n'
                            f'> A | {A}\n'
                            f'> B | {B}\n'
                            f'> C | {C}'
                        ),
                        'Question':Question,
                        'Right_Answer':f'{Right_Answer.upper()}',
                        'For_Select':{
                            'Select[1]':{
                                'label':'Answer : A',
                                'description':f'{A}',
                                'value':'A',
                                'emoji':'📄'
                            },

                            'Select[2]':{
                                'label':'Answer : B',
                                'description':f'{B}',
                                'value':'B',
                                'emoji':'📄'
                            },

                            'Select[3]':{
                                'label':'Answer : C',
                                'description':f'{C}',
                                'value':'C',
                                'emoji':'📄'
                            },
                        }
                    }
                    Question_List.append(Put_Data)

                class Menu(discord.ui.View):
                    def __init__(self):
                        super().__init__()
                        self.count = 0
                        self.U_Right_Answer = 0
                        self.U_Wrong_Answer = 0
                    
                    @ui.button(label='Ready',style=discord.ButtonStyle.green, custom_id = 'Ready_Next_BT')
                    async def ready_bt(self, interaction, button: ui.Button):
                        interid = interaction.user.id

                        if interid != user_id:
                            await interaction.response.defer()
                            await interaction.followup.send(
                                content=f'Sorry, this menu is controlled by {user.name}!',
                                ephemeral=True
                            )
                            return interid == user_id
                        
                        await interaction.response.defer()
                        get = discord.utils.get(self.children, custom_id='Select_Answer')

                        if get != None:
                            self.remove_item(get)

                        if self.count == Work_Turn:
                            for item in self.children:
                                item.disabled = True

                            Embed = discord.Embed(
                                title = f'{Emoji_8} | Working Done...',
                                description = (
                                    f'`Right Answer :` {custom_drawbar(self.U_Right_Answer, 10, Work_Turn, "🟦", "⬛")} `| {self.U_Right_Answer}`\n'
                                    f'`Wrong Answer :` {custom_drawbar(self.U_Wrong_Answer, 10, Work_Turn, "🟦", "⬛")} `| {self.U_Wrong_Answer}`\n'
                                    f'`Total Income :` `+{self.U_Right_Answer * Sall:,}` CyberMoney\n'
                                ),
                                color=color
                            )
                            Embed.set_footer(text=f'Executor : {user.name} | {Time}')
                            await interaction.edit_original_message(
                                embed = Embed,
                                view=self
                            )
                            change_cooldown(user_id, 'W_CD')

                            check = cursor.find_one({'id':user_id})
                            check_1 = dict(check['N_economy_Data'])
                            check_2 = dict(check['Jobs_Data'])

                            check_1['Money'] += self.U_Right_Answer * Sall
                            check_1['NetWorth'] += self.U_Right_Answer * Sall
                            check_2['CQuest'] += self.U_Right_Answer

                            cursor.update_many({'id':user_id},{'$set':{
                                'N_economy_Data':check_1,
                                'Jobs_Data':check_2
                            }})
                            return

                        option_now = []
                        r_answer = Question_List[self.count]['Right_Answer']

                        for x in range(1,4):
                            option_append = discord.SelectOption(
                                label = Question_List[self.count]['For_Select'][f'Select[{x}]']['label'],
                                description = Question_List[self.count]['For_Select'][f'Select[{x}]']['description'],
                                value = Question_List[self.count]['For_Select'][f'Select[{x}]']['value'],
                                emoji = Question_List[self.count]['For_Select'][f'Select[{x}]']['emoji']
                            )
                            option_now.append(option_append)

                        class Select(discord.ui.Select):
                            def __init__(self):
                                super().__init__(
                                    placeholder = 'Select Answer',
                                    max_values = 1,
                                    min_values = 1,
                                    options = option_now,
                                    custom_id = 'Select_Answer' 
                                )
                                self.R_Answer = r_answer
                            
                            async def callback(self, interaction):
                                interid = interaction.user.id

                                if interid != user_id:
                                    await interaction.response.defer()
                                    await interaction.followup.send(
                                        content=f'Sorry, this menu is controlled by {user.name}!',
                                        ephemeral=True
                                    )
                                    return interid == user_id
                                
                                await interaction.response.defer()

                                next_bt = discord.utils.get(self.view.children, custom_id = 'Ready_Next_BT')

                                if self.values[0] == self.R_Answer:
                                    self.view.U_Right_Answer += 1
                                    Embed = discord.Embed(
                                        title=f'{Emoji_8} | Question [{self.view.count+1}/{Work_Turn}]',
                                        description=(
                                            f'{Question_List[self.view.count]["Embed_description"]}\n'
                                            '━━━━━━━━━━━━━━━━━━━━━━━━━\n'
                                            '> Your Answer Was Right!'
                                        ),
                                        color=color
                                    )
                                    Embed.set_footer(text=f'Executor : {user.name} | {Time}')

                                else:
                                    self.view.U_Wrong_Answer += 1
                                    Embed = discord.Embed(
                                        title=f'{Emoji_8} | Question [{self.view.count+1}/{Work_Turn}]',
                                        description=(
                                            f'{Question_List[self.view.count]["Embed_description"]}\n'
                                            '━━━━━━━━━━━━━━━━━━━━━━━━━\n'
                                            f'> Sorry, your Answer Was wrong...\n'
                                            f'> The Right Answer is **{Question_List[self.view.count]["Right_Answer"]}**'
                                        ),
                                        color=color
                                    )
                                    Embed.set_footer(text=f'Executor : {user.name} | {Time}')

                                next_bt.disabled = False
                                self.disabled = True
                                self.view.count += 1

                                if self.view.count == Work_Turn:
                                    next_bt.style = discord.ButtonStyle.blurple
                                    next_bt.label = 'Done'

                                await interaction.edit_original_message(
                                    embed = Embed,
                                    view = self.view
                                )
                        
                        self.add_item(Select())
                        self.ready_bt.label = 'Next'
                        self.cancel_bt.disabled = False
                        self.ready_bt.disabled = True
                        self.cancel_bt.label = 'Stop'

                        Embed = discord.Embed(
                            title=f'{Emoji_8} | Question [{self.count+1}/{Work_Turn}]',
                            description=f'{Question_List[self.count]["Embed_description"]}',
                            color=color
                        )
                        Embed.set_footer(text=f'Executor : {user.name} | {Time}')

                        await interaction.edit_original_message(
                            embed=Embed,
                            view=self
                        )

                    @ui.button(label='Cancel',style=discord.ButtonStyle.red)
                    async def cancel_bt(self, interaction, button: ui.Button):
                        interid = interaction.user.id

                        if interid != user_id:
                            await interaction.response.defer()
                            await interaction.followup.send(
                                content=f'Sorry, this menu is controlled by {user.name}!',
                                ephemeral=True
                            )
                            return interid == user_id

                        await interaction.response.defer()

                        if self.count == 0:
                            for item in self.children:
                                item.disabled = True
                            await interaction.edit_original_message(view=self)
                            return
                        
                        for item in self.children:
                            item.disabled = True

                        Embed = discord.Embed(
                            title = f'{Emoji_8} | Working Done...',
                            description = (
                                f'Right Answer : {custom_drawbar(self.U_Right_Answer, 10, Work_Turn, "🟦", "⬛")} `| {self.U_Right_Answer}`\n'
                                f'Wrong Answer : {custom_drawbar(self.U_Wrong_Answer, 10, Work_Turn, "🟦", "⬛")} `| {self.U_Wrong_Answer}`\n'
                                f'Total Income : `+{self.U_Right_Answer * Sall:,}` CyberMoney\n'
                            ),
                            color=color
                        )
                        Embed.set_footer(text=f'Executor : {user.name} | {Time}')
                        await interaction.edit_original_message(
                            embed = Embed,
                            view=self
                        )
                        change_cooldown(user_id, 'W_CD')

                        check = cursor.find_one({'id':user_id})
                        check_1 = dict(check['N_economy_Data'])
                        check_2 = dict(check['Jobs_Data'])

                        check_1['Money'] += self.U_Right_Answer * Sall
                        check_1['NetWorth'] += self.U_Right_Answer * Sall
                        check_2['CQuest'] += self.U_Right_Answer

                        cursor.update_many({'id':user_id},{'$set':{
                            'N_economy_Data':check_1,
                            'Jobs_Data':check_2
                        }})
                        return

                    async def on_timeout(self):
                        for item in self.children:
                            item.disabled = True

                        await interaction.edit_original_message(view=self)

                Embed = discord.Embed(
                    title=f'{Emoji_8} | Working...',
                    description='> If you are ready to work then press the **Ready** button below',
                    color=color
                )
                Embed.set_footer(text=f'Executor : {user.name} | {Time}')
                await interaction.followup.send(
                    embed=Embed,
                    view=Menu()
                )

    @app_commands.command(name='bal')
    async def bal(self, interaction: discord.Interaction, user:discord.Member=None):
        """Checking your CyberMoney or someone else CyberMoney"""
        await interaction.response.defer()

        user = user
        
        if user == None:
            user = interaction.user
        
        user_id = user.id
        user_name = user.name
        user_pfp = user.display_avatar.url
        Time = datetime.datetime.now()

        check = cursor.find_one({'id':user_id})

        #-----------------
        Guild = self.bot.get_guild(privguild)

        Emoji_1 = discord.utils.get(Guild.emojis, name='CYBUSER')
        Emoji_2 = discord.utils.get(Guild.emojis, name='CYBMONEY')
        #-----------------

        if check is None:
            Embed = discord.Embed(
                title=f'{Emoji_1} | Command Failed',
                description=f'> Sorry {user_name}. you`re not create an account yet.\n> Please Create an account with command ***/start!***',
                color=color
            )
            Embed.set_footer(text=f'Executor : {user_name} | {Time}')
            Embed.set_thumbnail(url=user_pfp)
            await interaction.followup.send(embed=Embed)
            return
        
        else:
            Money = check['N_economy_Data']['Money']
            Embed = discord.Embed(
                title = f'{Emoji_1} | {user_name} CyberMoney',
                description = f'> Cyber Money : `{Money:,}`',
                color = color
            )
            Embed.set_footer(text=f'Executor : {user_name} | {Time}')
            await interaction.followup.send(embed=Embed)

    @app_commands.command(name='reward')
    async def reward(self, interaction: discord.Interaction, claim:str=None):
        """Claim or checking user reward!"""
        await interaction.response.defer()
        
        user = interaction.user
        user_id = user.id
        user_name = user.name
        user_pfp = user.display_avatar.url
        Time = datetime.datetime.now()

        check = cursor.find_one({'id':user_id})

        #-----------------
        Guild = self.bot.get_guild(privguild)

        Emoji_1 = discord.utils.get(Guild.emojis, name='CYBUSER')
        Emoji_2 = discord.utils.get(Guild.emojis, name='CYBMONEY')
        Emoji_3 = discord.utils.get(Guild.emojis, name='CYBEXP')
        Emoji_4 = discord.utils.get(Guild.emojis, name='CYBCOOLDOWN')
        #-----------------

        if check is None:
            Embed = discord.Embed(
                title=f'{Emoji_1} | Command Failed',
                description=f'> Sorry {user_name}. you`re not create an account yet.\n> Please Create an account with command ***/start!***',
                color=color
            )
            Embed.set_footer(text=f'Executor : {user_name} | {Time}')
            Embed.set_thumbnail(url=user_pfp)
            await interaction.followup.send(embed=Embed)
            return
        else:
            if claim is None:
                
                holder_1 = get_cooldown(user_id, 'HR_CD')
                dbsecond = holder_1[0]
                if holder_1[0] == 0:
                    holder_1 = '0D : 0h : 0m : 0s'
                    drawbr_1 = custom_drawbar(3600, 10, 3600, '🟦', '⬛')
                else:
                    holder_1 = 3600 - holder_1[0]
                    if holder_1 < 0:
                        holder_1 = '0D : 0h : 0m : 0s'
                        drawbr_1 = custom_drawbar(3600, 10, 3600, '🟦', '⬛')
                    else:
                        drawbr_1 = custom_drawbar(dbsecond, 10, 3600, '🟦', '⬛')
                        holder_1 = inspect_time(holder_1, f'{datetime.timedelta(seconds=holder_1)}')

                holder_2 = get_cooldown(user_id, 'DR_CD')
                dbsecond = holder_2[0]
                if holder_2[0] == 0:
                    holder_2 = '0D : 0h : 0m : 0s'
                    drawbr_2 = custom_drawbar(86400, 10, 86400, '🟦', '⬛')
                else:
                    holder_2 = 86400 - holder_2[0]
                    if holder_2 < 0:
                        holder_2 = '0D : 0h : 0m : 0s'
                        drawbr_2 = custom_drawbar(86400, 10, 86400, '🟦', '⬛')
                    else:
                        drawbr_2 = custom_drawbar(dbsecond, 10, 86400, '🟦', '⬛')
                        holder_2 = inspect_time(holder_2, f'{datetime.timedelta(seconds=holder_2)}')

                holder_3 = get_cooldown(user_id, 'WR_CD')
                dbsecond = holder_3[0]
                if holder_3[0] == 0:
                    holder_3 = '0D : 0h : 0m : 0s'
                    drawbr_3 = custom_drawbar(604800, 10, 604800, '🟦', '⬛')
                else:
                    holder_3 = 604800 - holder_3[0]
                    if holder_3 < 0:
                        holder_3 = '0D : 0h : 0m : 0s'
                        drawbr_3 = custom_drawbar(604800, 10, 604800, '🟦', '⬛')
                    else:
                        drawbr_3 = custom_drawbar(dbsecond, 10, 604800, '🟦', '⬛')
                        holder_3 = inspect_time(holder_3, f'{datetime.timedelta(seconds=holder_3)}')
                
                holder_4 = get_cooldown(user_id, 'MR_CD')
                dbsecond = holder_4[0]
                if holder_4[0] == 0:
                    holder_4 = '0D : 0h : 0m : 0s'
                    drawbr_4 = custom_drawbar(2592000, 10, 2592000, '🟦', '⬛')
                else:
                    holder_4 = 2592000 - holder_4[0]
                    if holder_4 < 0:
                        holder_4 = '0D : 0h : 0m : 0s'
                        drawbr_4 = custom_drawbar(2592000, 10, 2592000, '🟦', '⬛')
                    else:
                        drawbr_4 = custom_drawbar(dbsecond, 10, 2592000, '🟦', '⬛')
                        holder_4 = inspect_time(holder_4, f'{datetime.timedelta(seconds=holder_4)}')
                
                Embed = discord.Embed(
                    title=f'{Emoji_1} | {user_name} Reward Cooldown',
                    description=(
                        f'> Hourly Reward :\n'
                        f'> {drawbr_1} | {holder_1}\n'
                        f'> Daily Reward :\n'
                        f'> {drawbr_2} | {holder_2}\n'
                        f'> Weekly Reward :\n'
                        f'> {drawbr_3} | {holder_3}\n'
                        f'> Moonthly Reward :\n'
                        f'> {drawbr_4} | {holder_4}\n'
                    ),
                    color=color
                )
                Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                await interaction.followup.send(embed=Embed)
            
            else:
                reward_check = reward_list(claim.lower())

                if reward_check is None:
                    Embed = discord.Embed(
                        title=f'{Emoji_1} | Reward Not Found',
                        description=f'> Reward with name **{claim}** is not exist!',
                        color=color
                    )
                    Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                    await interaction.followup.send(embed=Embed)
                
                else:
                    check_cd = get_cooldown(user_id, f'{reward_check["ID"]}')
                    if check_cd[0] == 0:
                        Money_Reward = reward_check['Money']
                        Exp_Reward = reward_check['Exp']

                        check = dict(check)
                        check['N_economy_Data']['Money'] += Money_Reward
                        check['N_economy_Data']['Exp'] += Exp_Reward
                        
                        cursor.update_many({'id':user_id},{'$set':{
                            'N_economy_Data':check['N_economy_Data']
                        }})

                        change_cooldown(user_id, reward_check['ID'])

                        Embed = discord.Embed(
                            title=f'{Emoji_2} | Prize sent succesfully',
                            description=(
                                f'> Prize has been successfully sent to your account\n'
                                f'> {Emoji_2} | `+{Money_Reward:,}` CyberMoney\n'
                                f'> {Emoji_3} | `+{Exp_Reward:,}` Exp'
                            ),
                            color=color
                        )
                        Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                        await interaction.followup.send(embed=Embed)

                    else:
                        cd_holder = reward_cdls(claim.lower()) - check_cd[0]

                        if cd_holder < 0:
                            Money_Reward = reward_check['Money']
                            Exp_Reward = reward_check['Exp']

                            check = dict(check)
                            check['N_economy_Data']['Money'] += Money_Reward
                            check['N_economy_Data']['Exp'] += Exp_Reward
                            
                            cursor.update_many({'id':user_id},{'$set':{
                                'N_economy_Data':check['N_economy_Data']
                            }})

                            change_cooldown(user_id, reward_check['ID'])

                            Embed = discord.Embed(
                                title=f'{Emoji_2} | Prize sent succesfully',
                                description=(
                                    f'> Prize has been successfully sent to your account\n'
                                    f'> {Emoji_2} | `+{Money_Reward:,}` CyberMoney\n'
                                    f'> {Emoji_3} | `+{Exp_Reward:,}` Exp'
                                ),
                                color=color
                            )
                            Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                            await interaction.followup.send(embed=Embed)

                        else:
                            db_holder = custom_drawbar(check_cd[0], 10, reward_cdls(claim.lower()),'🟦' ,'⬛')
                            cd_holder = inspect_time(cd_holder, f'{datetime.timedelta(seconds=cd_holder)}')

                            Embed = discord.Embed(
                                title=f'{Emoji_4} | Reward is on cooldown!',
                                description=(
                                    f'> please wait until the cooldown runs out\n'
                                    f'> {db_holder} | {cd_holder}'
                                ),
                                color=color
                            )
                            Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                            await interaction.followup.send(embed=Embed)

    @reward.autocomplete('claim')
    async def reward_autocomplete(self, interaction: discord.Interaction, claim: str):
        return [
            app_commands.Choice(name= 'hourly', value= 'hourly'),
            app_commands.Choice(name= 'daily', value= 'daily'),
            app_commands.Choice(name= 'weekly', value= 'weekly'),
            app_commands.Choice(name= 'moonthly', value= 'moonthly')
        ]
    
    @app_commands.command(name='level-up')
    async def level_up(self, interaction: discord.Interaction):
        """Make your level increase with exp!"""
        await interaction.response.defer()

        f_user = interaction.user
        user_id = f_user.id
        user_pfp = f_user.display_avatar.url
        user_name = f_user.name

        Time = datetime.datetime.now()
        check = cursor.find_one({'id':user_id})

        #-----------------
        Guild = self.bot.get_guild(privguild)

        Emoji_1 = discord.utils.get(Guild.emojis, name='CYBUSER')
        Emoji_2 = discord.utils.get(Guild.emojis, name='CYBMONEY')
        Emoji_3 = discord.utils.get(Guild.emojis, name='CYBEXP')
        Emoji_4 = discord.utils.get(Guild.emojis, name='CYBLEVEL')
        Emoji_5 = discord.utils.get(Guild.emojis, name='CYBSUBS')
        Emoji_6 = discord.utils.get(Guild.emojis, name='CYBSALLARY')
        #-----------------

        if check is None:
            Embed = discord.Embed(
                title=f'{Emoji_1} | Command Failed',
                description=f'> Sorry {user_name}. you`re not create an account yet.\n> Please Create an account with command ***/start!***',
                color=color
            )
            Embed.set_footer(text=f'Executor : {user_name} | {Time}')
            Embed.set_thumbnail(url=user_pfp)
            await interaction.followup.send(embed=Embed)
            return
        
        else:
            user_profession = check['Jobs_Data']['CJobs']

            if user_profession == 'CyberTuber':
                user_mxp = check['N_economy_Data']['MaxExp']
                user_exp = check['N_economy_Data']['Exp']
                user_lvl = check['N_economy_Data']['Level']

                if user_exp < user_mxp:
                    Embed = discord.Embed(
                        title=f'{Emoji_4} | Level-up Failed...',
                        description=(
                            f'> Sorry {user_name} you cant level-up yet...\n'
                            f'━━━━━━━━━━━━━━━━━━━━━━━━━\n'
                            f'> {Emoji_3} | Your Exp :\n'
                            f'> {custom_drawbar(user_exp, 15, user_mxp, "🟦", "⬛")} | {user_exp:,}/{user_mxp}'
                        ),
                        color=color
                    )
                    Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                    await interaction.followup.send(embed=Embed)
                
                else:
                    for_db = dict(check)

                    Subs_Reward = int(100 * for_db['N_economy_Data']['Level'] / random.uniform(1,2))
                    Money_Reward = int(5000 * for_db['N_economy_Data']['Level'] / random.uniform(1,2))

                    for_db['N_economy_Data']['MaxExp'] += 30
                    for_db['N_economy_Data']['Exp'] -= user_mxp
                    for_db['N_economy_Data']['Money'] += Money_Reward
                    for_db['Jobs_Data']['CSubs'] += Subs_Reward
                    for_db['N_economy_Data']['Level'] += 1

                    cursor.update_many({'id':user_id},{'$set':{
                        'N_economy_Data':for_db['N_economy_Data'],
                        'Jobs_Data':for_db['Jobs_Data']
                    }})

                    Embed = discord.Embed(
                        title=f'{Emoji_4} | Level-up success!',
                        description=(
                            f'> {user_name} Level is now increased!\n'
                            f'━━━━━━━━━━━━━━━━━━━━━━━━━\n'
                            f'> {Emoji_3} | `{user_exp:,}/{user_mxp:,}` -> `{for_db["N_economy_Data"]["Exp"]:,}/{for_db["N_economy_Data"]["MaxExp"]:,}`\n'
                            f'> {Emoji_4} | `{user_lvl:,}` -> `{for_db["N_economy_Data"]["Level"]:,}`\n'
                            f'> {Emoji_5} | `+{Subs_Reward:,}`\n'
                            f'> {Emoji_2} | `+{Money_Reward:,}`'
                        ),
                        color=color
                    )
                    Embed.set_footer(text=f'Executor : {user_name} | Time')
                    await interaction.followup.send(embed=Embed)

            else:
                user_mxp = check['N_economy_Data']['MaxExp']
                user_exp = check['N_economy_Data']['Exp']
                user_lvl = check['N_economy_Data']['Level']
                user_sal = check['Jobs_Data']['CSall']

                if user_exp < user_mxp:
                    Embed = discord.Embed(
                        title=f'{Emoji_4} | Level-up Failed...',
                        description=(
                            f'> Sorry {user_name} you cant level-up yet...\n'
                            f'━━━━━━━━━━━━━━━━━━━━━━━━━\n'
                            f'> {Emoji_3} | Your Exp :\n'
                            f'```{custom_drawbar(user_exp, 15, user_mxp, "🟦", "⬛")} | {user_exp:,}/{user_mxp}```'
                        ),
                        color=color
                    )
                    Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                    await interaction.followup.send(embed=Embed)
                
                else:
                    for_db = dict(check)

                    Money_Reward = int(5000 * for_db['N_economy_Data']['Level'] / random.uniform(1,2))

                    for_db['N_economy_Data']['MaxExp'] += 30
                    for_db['N_economy_Data']['Exp'] -= user_mxp
                    for_db['N_economy_Data']['Money'] += Money_Reward
                    for_db['N_economy_Data']['Level'] += 1
                    for_db['Jobs_Data']['CSall'] += 30

                    cursor.update_many({'id':user_id},{'$set':{
                        'N_economy_Data':for_db['N_economy_Data'],
                        'Jobs_Data':for_db['Jobs_Data']
                    }})

                    Embed = discord.Embed(
                        title=f'{Emoji_4} | Level-up success!',
                        description=(
                            f'> {user_name} Level is now increased!\n'
                            f'━━━━━━━━━━━━━━━━━━━━━━━━━\n'
                            f'> {Emoji_3} | `{user_exp:,}/{user_mxp:,}` -> `{for_db["N_economy_Data"]["Exp"]:,}/{for_db["N_economy_Data"]["MaxExp"]:,}`\n'
                            f'> {Emoji_4} | `{user_lvl:,}` -> `{for_db["N_economy_Data"]["Level"]:,}`\n'
                            f'> {Emoji_6} | `{user_sal:,}` -> `{for_db["Jobs_Data"]["CSall"]:,}`\n'
                            f'> {Emoji_2} | `+{Money_Reward:,}`'
                        ),
                        color=color
                    )
                    Embed.set_footer(text=f'Executor : {user_name} | Time')
                    await interaction.followup.send(embed=Embed)

    @app_commands.command(name='leaderboard')
    async def lb(self, interaction: discord.Interaction):
        """See a global money leaderboard"""
        await interaction.response.defer()

        f_user = interaction.user
        user_id = f_user.id
        user_name = f_user.name
        user_pfp = f_user.display_avatar.url

        Time = datetime.datetime.now()
        check = cursor.find_one({'id':user_id})
        
        #-----------------
        Guild = self.bot.get_guild(privguild)

        Emoji_1 = discord.utils.get(Guild.emojis, name='CYBUSER')
        Emoji_2 = discord.utils.get(Guild.emojis, name='CYBMONEY')
        #-----------------

        State_check = None
        User_poss = 0

        if check is None:
            State_check = 'No Account'
            User_poss = 'None'
        
        else:
            State_check = 'Account'
        
        All_Data = list(cursor.find({}))
        Get_Data = sorted(All_Data, key=lambda get: get['N_economy_Data']['Money'], reverse=True)
        Svd_Data = [0]
        Svd_count = 1

        for Get in Get_Data:
            Svd_count += 1

            if Svd_count >= 10:
                if State_check == 'No Account':
                    break

            elif Svd_count >= 100 and State_check == 'Account':
                User_poss = f'{Svd_count}+'
                break

            if Get['name'] == user_name:
                User_poss = Svd_count
                Svd_Data.append(
                    f'{Get["name"]} - {Get["N_economy_Data"]["Money"]:,} CyberMoney\n'
                )   
                break

            Svd_Data.append(
                f'{Get["name"]} - {Get["N_economy_Data"]["Money"]:,} CyberMoney\n'
            )
        
        Embed_Message = ['Holder']

        for x in range(1,11):
            try:
                Embed_Message.append(f'`{x}` | {Svd_Data[x]}')
            except:
                Embed_Message.append(f'`{x}` | -\n')
        
        Embed_Message.pop(0)
        Embed_Message = "".join(Embed_Message)

        if not Embed_Message:
            Embed_Message = '> No Data...'
            User_poss = 'No Data...'
            Svd_Data.append('No Data...')
        
        Embed = discord.Embed(
            title=f'{Emoji_2} | Leaderboard',
            description=(
                f'```\nTop User : {Svd_Data[1]}'
                f'Your Position : {User_poss-1}\n```'
                '━━━━━━━━━━━━━━━━━━━━━━━━━\n'
                f'{Embed_Message}'
            ),
            color=color
        )
        Embed.set_footer(text=f'Executor : {user_name} | {Time}')
        await interaction.followup.send(embed=Embed)

    @app_commands.command(name='shop')
    async def shop(self, interaction: discord.Interaction):
        """A place to see, buy, and sell item!"""
        await interaction.response.defer()

        f_user = interaction.user
        user_id = f_user.id
        user_name = f_user.name
        user_pfp = f_user.display_avatar.url

        Time = datetime.datetime.now()
        check = cursor.find_one({'id':user_id})

        #-----------------
        Guild = self.bot.get_guild(privguild)

        Emoji_1 = discord.utils.get(Guild.emojis, name='CYBUSER')
        Emoji_2 = discord.utils.get(Guild.emojis, name='CYBMONEY')
        Emoji_3 = discord.utils.get(Guild.emojis, name='CYBSAL_BOOSTER')
        Emoji_4 = discord.utils.get(Guild.emojis, name='CYBERS_BOOSTER')
        Emoji_5 = discord.utils.get(Guild.emojis, name='CYBV_BOOSTER')
        Emoji_6 = discord.utils.get(Guild.emojis, name='CYBEXP')
        Emoji_7 = discord.utils.get(Guild.emojis, name='CYBCOOLDOWN')
        Emoji_8 = discord.utils.get(Guild.emojis, name='CYBSHARD')
        #-----------------

        if check is None:
            Embed = discord.Embed(
                title=f'{Emoji_1} | Command Failed',
                description=f'> Sorry {user_name}. you`re not create an account yet.\n> Please Create an account with command ***/start!***',
                color=color
            )
            Embed.set_footer(text=f'Executor : {user_name} | {Time}')
            Embed.set_thumbnail(url=user_pfp)
            await interaction.followup.send(embed=Embed)
            return
        
        else:
            Money = check['N_economy_Data']['Money']
            Shard = check['N_economy_Data']['Shard']

            Shop_Embed = [
                {
                    'Page_Name':'Main Page',
                    'Index':0,
                    'Embed': (
                            f"> Welcome to CyberBot Shop {user_name}!\n"
                            "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"> {Emoji_2} | **CyberMoney** :" "`{Money}`\n"
                            f"> {Emoji_8} | **Shard** :" "`{Shard}`\n"
                            "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            "> `🟩` | Want to buy an item? use **Buy** Button and enter the item id.\n"
                            "> `🟥` | Want to sell an item? use **Sell** Button and enter the item id.\n"
                            "> `🟪` | Want to see other shop categories? you can use **select [CATEGORY]**.\n"
                            "> `⬛` | Want to end **Interaction**? use **End** Button.\n"
                            "> `🟦` | Want to go to this menu again? use `🏠` **(Home)** Button\n\n"

                            "> If you wanna see the item that are can be sell or not, \n"
                            "> you can see with select page. if item can be sell there will be\n"
                            "> **[SELLABLE]** in the right of the item name...\n"
                            "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            "> Please note, some item prices are subject to\n"
                            "> change at any time, be careful when buying items!"
                        )
                },
                {
                    'Page_Name':'Normal Shop [Booster - Reducer]',
                    'Index':1,
                    'Embed':discord.Embed(
                        title=f'{Emoji_1} | {user_name} shop panel',
                        description=(
                            (f"""
                                ```py
                                Normal Item Shop '[Booster - Reducer]'
                                ```
                                ━━━━━━━━━━━━━━━━━━━━━━━━━
                                > {Emoji_2} | **Money** : `{Money:,}`
                                > {Emoji_8} | **Shard** : `{Shard:,}`
                                ━━━━━━━━━━━━━━━━━━━━━━━━━

                                > {Emoji_6} | **Exp Booster**
                                ```py
                                Effect : Increasing exp from work by 35%
                                Time   : 15 Minute
                                Cost   : 20,000 CyberMoney
                                ID     : EB1
                                ```

                                > {Emoji_7} | **Cooldown Reducer**
                                ```py
                                Effect : Reducing cooldown time by 15 Seconds
                                Time   : 4 Hours
                                Cost   : 35,000 CyberMoney
                                ID     : CR1
                                ```

                                > {Emoji_3} | **Sallary Booster** **[PROGRAMMING ONLY]**
                                ```py
                                Effect : Increasing the salary of your work by 20%.
                                Time   : 20 Minute
                                Cost   : 40,000 CyberMoney
                                ID     : SB1
                                ```

                                > {Emoji_4} | **Subs Booster** **[CYBERTUBER ONLY]**
                                ```py
                                Effect : Increasing Subs earned from working by 120
                                Time   : 5 Hours
                                Cost   : 20,000 CyberMoney
                                ID     : SB2
                                ```

                                > {Emoji_5} | **Viewer Increaser** **[CYBERTUBER ONLY]**
                                ```py
                                Effect : Increasing Viewer earned from working by 235
                                Time   : 5 Hours
                                Cost   : 14,000 CyberMoney
                                ID     : VB1
                                ```
                                ━━━━━━━━━━━━━━━━━━━━━━━━━
                        """).replace('    ', '')
                        ),
                        color=color
                    )
                }
            ]
            Misc_Embed = [
                {
                    'Page_Name':'Buy - Sell Not Found',
                    'Embed': """
                        > Sorry {user}, Item with id **{ID}** could not be found.
                        > Please put the right id to buy or sell an item!
                        ━━━━━━━━━━━━━━━━━━━━━━━━━
                        ```py
                        State : Not Found
                        Item  : None
                        Cost  : None
                        Id    : {ID}
                        ```
                        ━━━━━━━━━━━━━━━━━━━━━━━━━
                     """.replace('   ', ''),
                    'Index':0
                },
                {
                    'Page_Name':'Buy - sell Found',
                    'Embed': """
                        > Item with id **{ID}** has been found!
                        ━━━━━━━━━━━━━━━━━━━━━━━━━
                        ```py
                        State : Found
                        Item  : {Item_Name}
                        Cost  : {Item_Cost}
                        Id    : {ID}
                        ```
                        ━━━━━━━━━━━━━━━━━━━━━━━━━
                        > If you want to buy this item you can press the **Buy** button again bellow, 
                        > otherwise you can return home by pressing the **Home** button
                    """.replace('   ', ''),
                    'Index':1
                },
                {
                    'Page_Name':'Jobs Aren`t Macth',
                    'Embed':"""
                        > Item with id **{ID}** has been found!
                        ━━━━━━━━━━━━━━━━━━━━━━━━━
                        ```py
                        State : Found
                        Item  : {Item_Name}
                        Cost  : {Item_Cost}
                        Id    : {ID}
                        ```
                        ━━━━━━━━━━━━━━━━━━━━━━━━━
                        > Item was found but you cant buy this item because
                        > The Jobs aren't match. This Item is for **{Item_Jobs}** Jobs
                    """.replace('   ', ''),
                    'Index':2
                },
                {
                    'Page_Name':'Money isn`t enough',
                    'Embed':"""
                        > Sorry {user} but your money isn't enough to buy this item.
                        ━━━━━━━━━━━━━━━━━━━━━━━━━
                        ```py
                        State : Found
                        Item  : {Item_Name}
                        Cost  : {Item_Cost}
                        Id    : {ID}
                        ```
                        ━━━━━━━━━━━━━━━━━━━━━━━━━
                        > `🟦` | {user} CyberMoney : `{u_money}`
                        > `🟦` | Total Item : `{Total_Amount}`
                        > `🟦` | Cost Total : `{Total_Cost}`
                    """.replace('   ', ''),
                    'index':3
                },
                {
                    'Page_Name':'Success Buying-Selling',
                    'Embed':"""
                        > Success Buying A {Item_Name}!
                        ━━━━━━━━━━━━━━━━━━━━━━━━━
                        ```py
                        State : Found
                        Item  : {Item_Name}
                        Cost  : {Item_Cost}
                        Id    : {ID}
                        ```
                        ━━━━━━━━━━━━━━━━━━━━━━━━━
                        > `🟦` | {user} {Item_Name} : +`{Total_Amount}`
                        > `🟦` | {user} CyberMoney : -`{Total_Cost}`
                    """.replace('   ', ''),
                    'index':4
                },
                {
                    'Page_Name':'Items cannot be sold',
                    'Embed':"""
                        > Item with id **{ID}** has been found!
                        ━━━━━━━━━━━━━━━━━━━━━━━━━
                        ```py
                        State : Found
                        Item  : {Item_Name}
                        Cost  : {Item_Cost}
                        Id    : {ID}
                        ```
                        ━━━━━━━━━━━━━━━━━━━━━━━━━
                        > Sorry {user}, this item cannot be sold. You can return 
                        > to the first menu by clicking the **HOME** Button
                    """.replace('   ', ''),
                    'index':5
                },
                {
                    'Page_Name':'Item isnt enough',
                    'Embed':"""
                        > Item with id **{ID}** has been found!
                        ━━━━━━━━━━━━━━━━━━━━━━━━━
                        ```py
                        State : Found
                        Item  : {Item_Name}
                        Cost  : {Item_Cost}
                        Id    : {ID}
                        ```
                        ━━━━━━━━━━━━━━━━━━━━━━━━━
                        > Sorry {user}, but {Item_Name} Amount in your
                        > inventory is not enough to sell...

                        > `🟦` | Amount {Item_Name} To Sell : `{Amount}`
                        > `🟦` | Amount {Item_Name} in inventory : `{U_Amount}`
                        ━━━━━━━━━━━━━━━━━━━━━━━━━
                    """.replace('   ', ''),
                    'index':6 
                },
                {

                }
            ]

            Options = []
            for get in Shop_Embed:
                if not get['Index'] == 0:
                    Options.append(
                        discord.SelectOption(
                            label=get['Page_Name'],
                            value=get['Index']
                        )
                    )
            
            class Buy_Sell_Modal(ui.Modal,title='Buy - Sell Item'):
                Item_id = ui.TextInput(
                    label='Item Id :',
                    required=True,
                    max_length=10
                )

                Amount = ui.TextInput(
                    label='Amount :',
                    max_length=10
                )

                async def on_submit(self, interaction):
                    await interaction.response.defer()

                    Item_Id = self.Item_id.value
                    Amount = self.Amount.value.isnumeric()

                    if Amount == False:
                        Amount = 1
                    else:
                        Amount = int(self.Amount.value)
                    
                    if Amount < 1:
                        Amount = 1
                            
                    self.value = {
                        'Item_Id':str(Item_Id),
                        'Amount':Amount
                    }

                    self.stop()
            
            class shop_menu(discord.ui.View):
                def __init__(self):
                    super().__init__()
                    
                    self.Item_Selection = None
                    self.Modal = Buy_Sell_Modal
                
                @ui.select(placeholder='[CATEGORY]',max_values=1,min_values=1,options=Options)
                async def shop_select_menu(self, interaction, select: discord.ui.Select):
                    await interaction.response.defer()

                    user = f_user
                    user_id = user.id
                    user_name = user.name
                    inter_id = interaction.user.id

                    if inter_id != user_id:
                        await interaction.followup.send(
                            content=f'Sorry This Menu is controlled by {user_name}',
                            ephemeral=True
                        )
                        return inter_id == user_id

                    Embed = Shop_Embed[int(select.values[0])]['Embed']
                    Embed.set_footer(text=f'Executor : {user_name} | {Time}')

                    await interaction.message.edit(embed=Embed)
                
                @ui.button(label='Buy',style=discord.ButtonStyle.green)
                async def Buy_Button(self, interaction, button: discord.ui.Button):

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
                    
                    check = cursor.find_one({'id':user_id})
                    
                    if self.Item_Selection is None:
                        modal = self.Modal()

                        await interaction.response.send_modal(modal)
                        await modal.wait()

                        modal = modal.value
                        Item = s_cursor.find_one({'ID':f'{modal["Item_Id"]}'})

                        if Item is None:
                            Embed = discord.Embed(
                                title=f'{Emoji_1} | {user_name} shop panel',
                                description=(
                                    Misc_Embed[0]['Embed']
                                        .replace('{ID}',f'{modal["Item_Id"]}')
                                        .replace('{user}', f'{user_name}')
                                ),
                                color=color
                            )
                            Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                            await interaction.message.edit(embed=Embed)
                            return

                        Item_Name = Item['ITEM']
                        Item_Cost = Item['COST']
                        Item_Jobs = Item['JOBS']

                        if not Item_Jobs == 'None':
                            if check['Jobs_Data']['CJobs'] != Item_Jobs:
                                Embed = discord.Embed(
                                    title=f'{Emoji_1} | {user_name} shop panel',
                                    description=(
                                        Misc_Embed[2]['Embed']
                                            .replace('{ID}',f'{modal["Item_Id"]}')
                                            .replace('{user}', f'{user_name}')
                                            .replace('{Item_Name}', f'{Item_Name}')
                                            .replace('{Item_Cost}', f'{Item_Cost:,}')
                                            .replace('{Item_Jobs}', f'{Item_Jobs}')
                                    ),
                                    color=color
                                )
                                await interaction.message.edit(embed=Embed)
                                return

                        Embed = discord.Embed(
                            title=f'{Emoji_1} | {user_name} shop panel',
                            description=(
                                Misc_Embed[1]['Embed']
                                    .replace('{ID}',f'{modal["Item_Id"]}')
                                    .replace('{user}', f'{user_name}')
                                    .replace('{Item_Name}', f'{Item_Name}')
                                    .replace('{Item_Cost}', f'{Item_Cost:,}')
                            ),
                            color=color
                        )
                        Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                        self.Item_Selection = (f'{Item["ID"]}', modal['Amount'])
                        self.Sell_Button.disabled = True
                        self.shop_select_menu.disabled = True
                        await interaction.message.edit(
                            embed=Embed,
                            view=self
                        )
                    
                    else:
                        await interaction.response.defer()

                        check = cursor.find_one({'id':user_id})
                        Items = s_cursor.find_one({'ID':self.Item_Selection[0]})
                        Item_Name = Items['ITEM']
                        Item_Cost = Items['COST']
                        Item_ID = Items['ID']
                        Cost_Total = Items['COST'] * self.Item_Selection[1]

                        user_money = check['N_economy_Data']['Money']
                        user_items = check['Item_Data']

                        if user_money < Cost_Total:
                            Embed = discord.Embed(
                                title=f'{Emoji_1} | {user_name} shop panel',
                                description=(
                                    Misc_Embed[3]['Embed']
                                        .replace('{user}', user_name)
                                        .replace('{Item_Name}', Item_Name)
                                        .replace('{u_money}', f'{user_money:,}')
                                        .replace('{Total_Cost}', f'{Cost_Total:,}')
                                        .replace('{Total_Amount}', f'{self.Item_Selection[1]:,}')
                                        .replace('{Item_Cost}', f'{Item_Cost:,}')
                                        .replace('{ID}', Item_ID)
                                ),
                                color=color
                            )

                            self.shop_select_menu.disabled = False
                            self.Sell_Button.disabled = False

                            await interaction.message.edit(
                                embed=Embed,
                                view=self
                            )
                        
                        else:
                            check = dict(check)
                            check['Item_Data'][f'{Items["AKA"]}'] += self.Item_Selection[1]
                            check['N_economy_Data']['Money'] -= Cost_Total

                            Items = s_cursor.find_one({'ID':self.Item_Selection[0]})
                            Item_Name = Items['ITEM']
                            Item_Cost = Items['COST']
                            Item_ID = Items['ID']
                            Cost_Total = Item_Cost * self.Item_Selection[1]

                            user_money = check['N_economy_Data']['Money']
                            user_items = check['Item_Data']

                            Embed = discord.Embed(
                                title=f'{Emoji_1} | {user_name} shop panel',
                                description=(
                                    Misc_Embed[4]['Embed']
                                        .replace('{user}', user_name)
                                        .replace('{Item_Name}', Item_Name)
                                        .replace('{u_money}', f'{user_money:,}')
                                        .replace('{Total_Cost}', f'{Cost_Total:,}')
                                        .replace('{Total_Amount}', f'{self.Item_Selection[1]:,}')
                                        .replace('{Item_Cost}', f'{Item_Cost:,}')
                                        .replace('{ID}', Item_ID)
                                ),
                                color=color
                            )
                            Embed.set_footer(text=f'Executor : {user_name} | {Time}')

                            cursor.update_many({'id':user_id},{'$set':{
                                'N_economy_Data':check['N_economy_Data'],
                                'Item_Data':check['Item_Data']
                            }})

                            self.Item_Selection = None

                            await interaction.message.edit(
                                embed=Embed,
                                view=self
                            )
                                          
                @ui.button(label='Sell',style=discord.ButtonStyle.red)
                async def Sell_Button(self, interaction, button: discord.ui.Button):

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
                    
                    check = cursor.find_one({'id':user_id})
                    
                    if self.Item_Selection is None:
                        modal = self.Modal()

                        await interaction.response.send_modal(modal)
                        await modal.wait()

                        modal = modal.value
                        Item = s_cursor.find_one({'ID':f'{modal["Item_Id"]}'})

                        if Item is None:
                            Embed = discord.Embed(
                                title=f'{Emoji_1} | {user_name} shop panel',
                                description=(
                                    Misc_Embed[0]['Embed']
                                        .replace('{ID}',f'{modal["Item_Id"]}')
                                        .replace('{user}', f'{user_name}')
                                ),
                                color=color
                            )
                            Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                            await interaction.message.edit(embed=Embed)
                            return
                        
                        Item_Name = Item['ITEM']
                        Item_Cost = Item['COST']
                        Item_State = Item['SELLABLE']

                        if not Item_State == True:
                            Embed = discord.Embed(
                                title=f'{Emoji_1} | {user_name} shop panel',
                                description=(
                                    Misc_Embed[5]['Embed']
                                        .replace('{ID}',f'{modal["Item_Id"]}')
                                        .replace('{Item_Name}',f'{Item_Name}')
                                        .replace('{Item_Cost}',f'{Item_Cost}')
                                        .replace('{user}',f'{user_name}')
                                ),
                                color=color
                            )
                            Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                            await interaction.message.edit(embed=Embed)
                            return
                        
                        else:
                            Embed = discord.Embed(
                                title=f'{Emoji_1} | {user_name} shop panel',
                                description=(
                                    Misc_Embed[1]['Embed']
                                        .replace('{ID}',f'{modal["Item_Id"]}')
                                        .replace('{user}', f'{user_name}')
                                        .replace('{Item_Name}', f'{Item_Name}')
                                        .replace('{Item_Cost}', f'{Item_Cost:,}')
                                        .replace('Buy','Sell')
                                        .replace('buy','Sell')
                                ),
                                color=color
                            )
                            Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                            self.Item_Selection = (f'{Item["ID"]}', modal['Amount'])
                            self.Buy_Button.disabled = True
                            self.shop_select_menu.disabled = True
                            await interaction.message.edit(
                                embed=Embed,
                                view=self
                            )

                    else:
                        await interaction.response.defer()

                        check = cursor.find_one({'id':user_id})
                        Items = s_cursor.find_one({'ID':self.Item_Selection[0]})

                        Item_Name = Items['ITEM']
                        Item_Cost = Items['COST']
                        Item_AKA = Items['AKA']
                        Item_ID = Items['ID']

                        user_money = check['N_economy_Data']['Money']
                        user_items = check['Item_Data']

                        if user_items[f'{Item_AKA}'] < self.Item_Selection[1]:
                            Embed = discord.Embed(
                                title = f'{Emoji_1} | {user_name} shop panel',
                                description = (
                                    Misc_Embed[6]['Embed']
                                        .replace('{user}',user_name)
                                        .replace('{ID}',Item_ID)
                                        .replace('{Item_Name}',Item_Name)
                                        .replace('{Item_Cost}',f'{Item_Cost}')
                                        .replace('{Amount}',f'{self.Item_Selection[1]:,}')
                                        .replace('{U_Amount}',f"{user_items[f'{Item_AKA}']:,}")
                                ),
                                color=color 
                            )
                            Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                            await interaction.message.edit(embed=Embed)
                            return

                        else:
                            Sell_Total = Items['COST'] * self.Item_Selection[1]
                            user_money = check['N_economy_Data']['Money'] - Sell_Total
                            user_item = check['Item_Data'][f'{Items["AKA"]}'] + self.Item_Selection[1]


                            check['Item_Data'][f'{Items["AKA"]}'] -= self.Item_Selection[1]
                            check['N_economy_Data']['Money'] += Sell_Total

                            cursor.update_many({'id':user_id},{'$set':{
                                'N_economy_Data':check['N_economy_Data'],
                                'Item_Data':check['Item_Data']
                            }})

                            Embed = discord.Embed(
                                title=f'{Emoji_1} | {user_name} shop panel',
                                description=(
                                    Misc_Embed[4]['Embed']
                                        .replace('{user}', user_name)
                                        .replace('{Item_Name}', Item_Name)
                                        .replace('{u_money}', f'{user_money:,}')
                                        .replace('-`{Total_Cost}`', f'+`{Sell_Total:,}`')
                                        .replace('+`{Total_Amount}`', f'-`{self.Item_Selection[1]:,}`')
                                        .replace('{Item_Cost}', f'{Item_Cost}')
                                        .replace('{ID}', Item_ID)
                                        .replace('Buying','Selling')
                                ),
                                color=color
                            )
                            Embed.set_footer(text=f'Executor : {user_name} | {Time}')

                            self.Item_Selection = None

                            await interaction.message.edit(
                                embed=Embed,
                                view=self
                            )
                
                @ui.button(label='🏠',style=discord.ButtonStyle.blurple)
                async def Home_Button(self, interaction, button: discord.ui.Button):
                    await interaction.response.defer()

                    user = f_user
                    user_id = user.id
                    user_name = user.name
                    inter_id = interaction.user.id

                    if inter_id != user_id:
                        await interaction.followup.send(
                            content=f'Sorry This Menu is controlled by {user_name}',
                            ephemeral=True
                        )
                        return inter_id == user_id
                    
                    check = cursor.find_one({'id':user_id})

                    Money = check['N_economy_Data']['Money']
                    Shard = check['N_economy_Data']['Shard']

                    Embed = discord.Embed(
                        title=f'{Emoji_1} | {user_name} shop panel',
                        description = (
                            Shop_Embed[0]['Embed']
                                .replace('{Money}',f'{Money:,}')
                                .replace('{Shard}',f'{Shard:,}')
                        ),
                        color=color
                    )
                    Embed.set_footer(text=f'Executor : {user_name} | {Time}')

                    for child in self.children:
                        child.disabled = False

                    await interaction.message.edit(
                        embed=Embed,
                        view=self
                    )

                @ui.button(label='End')
                async def end_button(self, interaction, button: discord.ui.Button):
                    await interaction.response.defer()

                    user = f_user
                    user_id = user.id
                    user_name = user.name
                    inter_id = interaction.user.id

                    if inter_id != user_id:
                        await interaction.followup.send(
                            content=f'Sorry This Menu is controlled by {user_name}',
                            ephemeral=True
                        )
                        return inter_id == user_id
                    
                    for children in self.children:
                        children.disabled = True
                    
                    await interaction.message.edit(view=self)
                
                async def on_timeout(self):
                    for children in self.children:
                        children.disabled = True

                    await interaction.edit_original_message(view=self)

            Embed = discord.Embed(
                title=f'{Emoji_1} | {user_name} shop panel',
                description = (
                    Shop_Embed[0]['Embed']
                        .replace('{Money}',f'{Money:,}')
                        .replace('{Shard}',f'{Shard:,}')
                ),
                color=color
            )
            Embed.set_footer(text=f'Executor : {user_name} | {Time}')

            await interaction.followup.send(
                embed=Embed,
                view=shop_menu()
            )

    @app_commands.command(name='inventory')
    async def inv(self, interaction: discord.Interaction):
        """Show list of item in yours Inventory"""
        await interaction.response.defer()

        f_user = interaction.user
        user_id = f_user.id
        user_name = f_user.name
        user_pfp = f_user.display_avatar.url

        Time = datetime.datetime.now()
        check = cursor.find_one({'id':user_id})

        #-----------------
        Guild = self.bot.get_guild(privguild)

        Emoji_1 = discord.utils.get(Guild.emojis, name='CYBUSER')
        Emoji_2 = discord.utils.get(Guild.emojis, name='CYBMONEY')
        #-----------------

        if check is None:
            Embed = discord.Embed(
                title=f'{Emoji_1} | Command Failed',
                description=f'> Sorry {user_name}. you`re not create an account yet.\n> Please Create an account with command ***/start!***',
                color=color
            )
            Embed.set_footer(text=f'Executor : {user_name} | {Time}')
            Embed.set_thumbnail(url=user_pfp)
            await interaction.followup.send(embed=Embed)
            return

        else:
            Items = list(s_cursor.find({}))
            List_Item = []

            for get in Items:
                try:
                    I_Name = get['ITEM']
                    U_Item = check['Item_Data'][f'{get["AKA"]}']

                    List_Item.append(
                        f'`🟦` | {user_name} {I_Name} : `{U_Item:,}`'
                    )

                except:
                    pass

            Embed = discord.Embed(
                title=f'{Emoji_1} | {user_name} Inventory',
                description=("\n".join(List_Item)),
                color=color
            )
            Embed.set_footer(text=f'Executor : {user_name} | {Time}')
            await interaction.followup.send(embed=Embed)

    @app_commands.command(name='use-item')
    async def use(self, interaction: discord.Interaction, item:str=None, amount:int=1):
        """Use An item in your inventory like a Sallary Booster!"""
        await interaction.response.defer()

        f_user = interaction.user
        user_id = f_user.id
        user_pfp = f_user.display_avatar.url
        user_name = f_user.name

        check = cursor.find_one({'id':user_id})
        Time = datetime.datetime.now()

        #-----------------
        Guild = self.bot.get_guild(privguild)

        Emoji_1 = discord.utils.get(Guild.emojis, name='CYBUSER')
        Emoji_2 = discord.utils.get(Guild.emojis, name='CYBMONEY')
        #-----------------

        if check is None:
            Embed = discord.Embed(
                title=f'{Emoji_1} | Command Failed',
                description=f'> Sorry {user_name}. you`re not create an account yet.\n> Please Create an account with command ***/start!***',
                color=color
            )
            Embed.set_footer(text=f'Executor : {user_name} | {Time}')
            Embed.set_thumbnail(url=user_pfp)
            await interaction.followup.send(embed=Embed)
            return

        else:
            if item is None:
                Embed = discord.Embed(
                    title=f'{Emoji_1} | Failed to use item!',
                    description="> Sorry User, Please put item name in **item** params!",
                    color=color
                )
                Embed.set_footer(text=f"Executor : {user_name} | {Time}")
                await interaction.followup.send(embed=Embed)
                return

            else:
                Item = check['Item_Data'].get(f'{item}')

                if Item is None:
                    Embed = discord.Embed(
                        title=f'{Emoji_1} | Item Not Found',
                        description=f'> Sorry user, item with name **{item}** is not exist in your inventory!',
                        color=color
                    )
                    Embed.set_footer(text=f'Executor : {user_name} | Time')
                    await interaction.followup.send(embed=Embed)
                    return
                
                else:
                    if check['Item_Data'][item] < amount:
                        Embed = discord.Embed(
                            title=f'{Emoji_1} | number of items is less..',
                            description=f'> Sorry user, the amount of item that you try to use is not enough!',
                            color=color
                        )
                        Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                        await interaction.followup.send(embed=Embed)
                        return

                    else:
                        Item_Name = s_cursor.find_one({"AKA":item})['ITEM']

                        Before = effect_time(user_id, item) 
                        Change = effect_time_add(user_id, item, amount)
                        After = effect_time(user_id, item)

                        check['Item_Data'][item] -= amount
                        cursor.update_many({'id':user_id},{'$set':{
                            'Item_Data':check['Item_Data']
                        }})

                        Embed = discord.Embed(
                            title=f'{Emoji_1} | Successfully using item!',
                            description=f"""
                                > Successfully using **{Item_Name}** `x{amount}!`
                                ━━━━━━━━━━━━━━━━━━━━━━━━━
                                > Before :
                                ```{Before[0]}```
                                > After :
                                ```{After[0]}```
                                ━━━━━━━━━━━━━━━━━━━━━━━━━
                            """.replace('   ',''),
                            color=color
                        )
                        Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                        await interaction.followup.send(embed=Embed)
                        return

    @use.autocomplete('item')
    async def use_autocomplete(self, interaction: discord.Interaction, item:str):
        user = interaction.user
        user_id = user.id
        user_name = user.name

        check = cursor.find_one({'id':user_id})

        if check is None:
            return None

        else:
            if check['Jobs_Data']['CJobs'] == 'CyberProgramming':
                return [
                    app_commands.Choice(name='Exp Booster',value='Xp_Boost'),
                    app_commands.Choice(name='Cooldown Reducer',value='C_Boost'),
                    app_commands.Choice(name='Sallary Booster',value='Sal_Boost')
                ]

            else:
                return [
                    app_commands.Choice(name='Exp Booster',value='Xp_Boost'),
                    app_commands.Choice(name='Cooldown Reducer',value='C_Boost'),
                    app_commands.Choice(name='Subs Booster',value='S_Booster'),
                    app_commands.Choice(name='Viewer Increaser',value='V_Boost')
                ]

    @app_commands.command(name='effect-time')
    async def effect(self, interaction: discord.Interaction, item:str=None):
        """Check how much time a booster effect last for"""
        await interaction.response.defer()

        f_user = interaction.user
        user_id = f_user.id
        user_pfp = f_user.display_avatar.url
        user_name = f_user.name

        check = cursor.find_one({'id':user_id})
        Time = datetime.datetime.now()

        #-----------------
        Guild = self.bot.get_guild(privguild)

        Emoji_1 = discord.utils.get(Guild.emojis, name='CYBUSER')
        Emoji_2 = discord.utils.get(Guild.emojis, name='CYBMONEY')
        #-----------------

        if check is None:
            Embed = discord.Embed(
                title=f'{Emoji_1} | Command Failed',
                description=f'> Sorry {user_name}. you`re not create an account yet.\n> Please Create an account with command ***/start!***',
                color=color
            )
            Embed.set_footer(text=f'Executor : {user_name} | {Time}')
            Embed.set_thumbnail(url=user_pfp)
            await interaction.followup.send(embed=Embed)
            return

        else:
            if item is None:
                List_Item = []

                for get in check['Item_Data']:
                    if get != 'AD_sd':
                        Time_Left = effect_time(user_id,get)
                        Item_Name = s_cursor.find_one({'AKA':get})['ITEM']

                        if Time_Left[1] == 'None':
                            Time_Left = Time_Left[0]
                        else:
                            Time_Left = Time_Left[0]
                        
                        List_Item.append(f'> {Item_Name} :\n```{Time_Left}```')

                List_Item = "\n".join(List_Item)
                Embed = discord.Embed(
                    title=f' {Emoji_1} | {user_name} Item Time',
                    description=f'{List_Item}',
                    color=color
                )
                Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                Embed.set_thumbnail(url=user_pfp)
                await interaction.followup.send(embed=Embed)

            else:
                try:
                    get = check['Item_Data'][f'{item}']
                except:
                    Embed = discord.Embed(
                        title=f' {Emoji_1} | {user_name} Item Time',
                        description=f'> Item With Name **{item}** is not exist!',
                        color=color
                    )
                    Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                    await interaction.followup.send(embed=Embed)
                    return

                if item != 'AD_sd':
                    Time_Left = effect_time(user_id,item)
                    Item_Name = s_cursor.find_one({'AKA':item})['ITEM']

                    if Time_Left[1] == 'None':
                        Time_Left = Time_Left[0]
                    else:
                        Time_Left = Time_Left[0]
                            
                    Item_show = f'> {Item_Name} :\n```{Time_Left}```'

                    Embed = discord.Embed(
                        title=f' {Emoji_1} | {user_name} Item Time',
                        description=f'{Item_show}',
                        color=color
                    )
                    Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                    Embed.set_thumbnail(url=user_pfp)
                    await interaction.followup.send(embed=Embed)
                
                else:
                    Embed = discord.Embed(
                        title=f' {Emoji_1} | {user_name} Item Time',
                        description=f"> Item With Name **{item}** isn't exist or unusable",
                        color=color
                    )
                    Embed.set_footer(text=f'Executor : {user_name} | {Time}')
                    await interaction.followup.send(embed=Embed)
                    return

    @effect.autocomplete('item')
    async def effect_autocomplete(self, interaction: discord.Interaction, item:str):
        user = interaction.user
        user_id = user.id
        user_name = user.name

        check = cursor.find_one({'id':user_id})

        if check is None:
            return None

        else:
            if check['Jobs_Data']['CJobs'] == 'CyberProgramming':
                return [
                    app_commands.Choice(name='Exp Booster',value='Xp_Boost'),
                    app_commands.Choice(name='Cooldown Reducer',value='C_Boost'),
                    app_commands.Choice(name='Sallary Booster',value='Sal_Boost')
                ]

            else:
                return [
                    app_commands.Choice(name='Exp Booster',value='Xp_Boost'),
                    app_commands.Choice(name='Cooldown Reducer',value='C_Boost'),
                    app_commands.Choice(name='Subs Booster',value='S_Booster'),
                    app_commands.Choice(name='Viewer Increaser',value='V_Boost')
                ]

async def setup(bot):
    await bot.add_cog(Economy_Cmd(bot))