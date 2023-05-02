import os
import discord
import pymongo
import datetime
import contextlib
from discord.ext import commands
from discord import app_commands
from discord import ui
import sys
import io

#------

client = pymongo.MongoClient(os.environ['DBLINK'])
db = client.Data
q_cursor = db['Question_Data']
privguild = 979708145905594439
color = 233087

#------

class owner_cmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='create_quest')
    async def CQuest(self, interaction: discord.Interaction):
        """Bot Owners Command"""
        await interaction.response.defer()

        user = interaction.user
        user_id = user.id
        Time = datetime.datetime.now()

        if user_id != 755582460158279800:
            await interaction.followup.send(
                content = "Sorry You Can't use this command!",
                ephemeral = True
            )
            return user_id == 755582460158279800

        total_question = len(list(q_cursor.find({})))
        Question_Data = {
            'Qid':f'Qid{total_question}', # Custom Id
            'Question':'None',            # Question
            'Answer':{                    # Answer Data
                'A':'None',
                'B':'None',
                'C':'None'
            },
            'R_Answer':'None',            # Right_Answers
            'Lang':'None'                 # Program Langguage ( py, js, c++, etc )
        }

        class Custom_Lang(ui.Modal):
            def __init__(self):
                super().__init__(title='Langguage')
                self.add_item(
                    ui.TextInput(
                        label = 'Lang :',
                        required=True
                    )
                )
            async def on_submit(self, interaction):
                await interaction.response.defer()
                self.value = []

                for Data in self.children:
                    self.value.append(Data.value)

                self.stop()

        class Q_Modal(ui.Modal):
            def __init__(self):
                super().__init__(title='New Question')
                self.Question_Data = Question_Data

                self.add_item(
                    ui.TextInput(
                        label = 'Question : ',
                        style = discord.TextStyle.paragraph,
                        required = True,
                        default = self.Question_Data['Question']
                    )
                )

                self.add_item(
                    ui.TextInput(
                        label = 'A : ',
                        required = True,
                        default = self.Question_Data['Answer']['A']
                    )
                )

                self.add_item(
                    ui.TextInput(
                        label = 'B : ',
                        required = True,
                        default = self.Question_Data['Answer']['B']
                    )
                )

                self.add_item(
                    ui.TextInput(
                        label = 'C : ',
                        required = True,
                        default = self.Question_Data['Answer']['C']
                    )
                )

                self.add_item(
                    ui.TextInput(
                        label = 'Right Answer (A / B / C):',
                        required = True,
                        default = self.Question_Data['R_Answer']
                    )
                )

            async def on_submit(self, interaction):
                await interaction.response.defer()
                self.value = []

                for Data in self.children:
                    self.value.append(Data.value)

                self.stop()

        class Menu(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.done_bt.disabled = True
                self.Lang = 'None'

            @ui.select(placeholder='Select The Jobs',max_values=1,min_values=1,options=[
                discord.SelectOption(label=f'Python',value='Python'),
                discord.SelectOption(label=f'Javascript',value='Javascript'),
                discord.SelectOption(label=f'C++',value='C++'),
                discord.SelectOption(label=f'C#',value='C#'),
                discord.SelectOption(label=f'GDScript',value='GDScript'),
                discord.SelectOption(label=f'Other...',value='Custom')
            ])
            async def select_Lang(self, interaction:discord.Interaction, select: discord.ui.Select):
                inter_id = interaction.user.id

                if inter_id != user_id:
                    await interaction.response.defer()
                    await interaction.followup.send(
                        content=f'Sorry, this menu is controlled by {user.name}!',
                        ephemeral=True
                    )
                    return inter_id == user_id

                if select.values[0] == 'Custom':
                    try:
                        modal = Custom_Lang()
                        await interaction.response.send_modal(modal)
                        await modal.wait()
                        self.Lang = modal.value[0]

                    except Exception as for_logs:
                        print(f'[LOGS] ERROR l {for_logs}')
                        return                

                else:
                    self.Lang = select.values[0]
            
            @ui.button(label='Edit',style=discord.ButtonStyle.green)
            async def edit_bt(self, interaction, button: ui.Button):
                inter_id = interaction.user.id

                if inter_id != user_id:
                    await interaction.response.defer()
                    await interaction.followup.send(
                        content=f'Sorry, this menu is controlled by {user.name}!',
                        ephemeral=True
                    )
                    return inter_id == user_id
                
                try:

                    modal = Q_Modal()
                    await interaction.response.send_modal(modal)
                    await modal.wait()
                    self.done_bt.disabled = False

                except Exception as for_logs:
                    print(f'[LOGS] ERROR l {for_logs}')
                    return

                Data_Get = modal.value

                Question_Data['Question'] = Data_Get[0]
                Question_Data['Answer']['A'] = Data_Get[1]
                Question_Data['Answer']['B'] = Data_Get[2]
                Question_Data['Answer']['C'] = Data_Get[3]
                Question_Data['R_Answer'] = Data_Get[4]
                Question_Data['Lang'] = self.Lang

                Embed = discord.Embed(
                    title='Question Menu [OWNER]',
                    description=(
                        f'> Question Preview : {Question_Data["Lang"]} Question\n'
                        '⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n'
                        '> `Question :`\n'
                        f'{Question_Data["Question"]}\n\n'
                        '> `Answer :`\n'
                        f'> `A :` {Question_Data["Answer"]["A"]}\n'
                        f'> `B :` {Question_Data["Answer"]["B"]}\n'
                        f'> `C :` {Question_Data["Answer"]["C"]}\n\n'
                        f'> `Right Answer :` {Question_Data["R_Answer"]}\n'
                        '⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯'
                    )
                    ,
                    color=color
                )
                Embed.set_footer(text=f'Executor : {user.name} | {Time}')
                await interaction.edit_original_message(
                    embed=Embed,
                    view=self
                )

            @ui.button(label='Done',style=discord.ButtonStyle.green)
            async def done_bt(self , interaction, button: ui.Button):
                inter_id = interaction.user.id

                if inter_id != user_id:
                    await interaction.response.defer()
                    await interaction.followup.send(
                        content=f'Sorry, this menu is controlled by {user.name}!',
                        ephemeral=True
                    )
                    return inter_id == user_id
                
                await interaction.response.defer()
                q_cursor.insert_one(Question_Data)
                self.done_bt.disabled = True
                self.edit_bt.disabled = True
                await interaction.edit_original_message(
                    view=self
                )
                await interaction.followup.send(
                    content='Question have been saved to the database!',
                    ephemeral=True
                )

        Embed = discord.Embed(
            title='Question Menu [OWNER]',
            description=(
                '> Question Preview :\n'
                '⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n'
                f'> Question Preview : {Question_Data["Lang"]} Question\n'
                f'{Question_Data["Question"]}\n\n'
                '> `Answer :`\n'
                f'> `A :` {Question_Data["Answer"]["A"]}\n'
                f'> `B :` {Question_Data["Answer"]["B"]}\n'
                f'> `C :` {Question_Data["Answer"]["C"]}\n\n'
                f'> `Right Answer :` {Question_Data["R_Answer"]}\n'
                '⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯'
            )
            ,
            color=color
        )
        Embed.set_footer(text=f'Executor : {user.name} | {Time}')
        await interaction.followup.send(
            embed=Embed,
            view=Menu()
        )

    @app_commands.command(name='edit_quest')
    async def EQuest(self, interaction: discord.Interaction, q_id:str = None):
        """Bot Owners Command"""
        await interaction.response.defer()

        user = interaction.user
        user_id = user.id
        Time = datetime.datetime.now()

        if user_id != 755582460158279800:
            await interaction.followup.send(
                content = "Sorry You Can't use this command!",
                ephemeral = True
            )
            return user_id == 755582460158279800

        Qid_List = list(q_cursor.find({}))
        Lst_Hold = []

        for gets in Qid_List:
            Lst_Hold.append(gets['Qid'])

        Lst_Hold = ", ".join(Lst_Hold)
        if q_id == None:
            Embed = discord.Embed(
                title='command failed',
                description = f'> Please Enter an Qid Qid`indexnum`!\n\nQid_List : ```{Qid_List}```',
                color=color
            ) 
            Embed.set_footer(text=f'Executor : {user.name} | {Time}')
            await interaction.followup.send(embed=Embed)
            return
        
        Question_Data = q_cursor.find_one({'Qid':q_id})

        if Question_Data == None:
            Embed = discord.Embed(
                title='Question Not found!',
                description=f'> Question with id `{q_id}` was not found!',
                color=color
            )
            Embed.set_footer(text=f'Executor : {user.name} | {Time}')
            await interaction.followup.send(embed=Embed)
            return

        Question_Data = dict(Question_Data)

        class E_Modal(ui.Modal, title='Edit Question'):
            def __init__(self):
                super().__init__(title='New Question')
                self.Question_Data = Question_Data

                self.add_item(
                    ui.TextInput(
                        label = 'Question : ',
                        style = discord.TextStyle.paragraph,
                        required = True,
                        default = self.Question_Data['Question']
                    )
                )

                self.add_item(
                    ui.TextInput(
                        label = 'A : ',
                        required = True,
                        default = self.Question_Data['Answer']['A']
                    )
                )

                self.add_item(
                    ui.TextInput(
                        label = 'B : ',
                        required = True,
                        default = self.Question_Data['Answer']['B']
                    )
                )

                self.add_item(
                    ui.TextInput(
                        label = 'C : ',
                        required = True,
                        default = self.Question_Data['Answer']['C']
                    )
                )

                self.add_item(
                    ui.TextInput(
                        label = 'Right Answer (A / B / C):',
                        required = True,
                        default = self.Question_Data['R_Answer']
                    )
                )

            async def on_submit(self, interaction):
                await interaction.response.defer()
                self.value = []

                for Data in self.children:
                    self.value.append(Data.value)

                self.stop()

        class Menu(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.done_bt.disabled = True
            
            @ui.button(label='Edit',style=discord.ButtonStyle.green)
            async def edit_bt(self, interaction, button: ui.Button):
                inter_id = interaction.user.id

                if inter_id != user_id:
                    await interaction.response.defer()
                    await interaction.followup.send(
                        content=f'Sorry, this menu is controlled by {user.name}!',
                        ephemeral=True
                    )
                    return inter_id == user_id
                
                try:

                    modal = E_Modal()
                    await interaction.response.send_modal(modal)
                    await modal.wait()
                    self.done_bt.disabled = False

                except Exception as for_logs:
                    print(f'[LOGS] ERROR l {for_logs}')
                    return

                Data_Get = modal.value

                Question_Data['Question'] = Data_Get[0]
                Question_Data['Answer']['A'] = Data_Get[1]
                Question_Data['Answer']['B'] = Data_Get[2]
                Question_Data['Answer']['C'] = Data_Get[3]
                Question_Data['R_Answer'] = Data_Get[4]

                Embed = discord.Embed(
                    title='Question Menu [OWNER]',
                    description=(
                        '> Question Preview :\n'
                        '⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n'
                        '> `Question :`\n'
                        f'{Question_Data["Question"]}\n\n'
                        '> `Answer :`\n'
                        f'> `A :` {Question_Data["Answer"]["A"]}\n'
                        f'> `B :` {Question_Data["Answer"]["B"]}\n'
                        f'> `C :` {Question_Data["Answer"]["C"]}\n\n'
                        f'> `Right Answer :` {Question_Data["R_Answer"]}\n'
                        '⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯'
                    )
                    ,
                    color=color
                )
                Embed.set_footer(text=f'Executor : {user.name} | {Time}')
                await interaction.edit_original_message(
                    embed=Embed,
                    view=self
                )

            @ui.button(label='Done',style=discord.ButtonStyle.green)
            async def done_bt(self , interaction, button: ui.Button):
                inter_id = interaction.user.id

                if inter_id != user_id:
                    await interaction.response.defer()
                    await interaction.followup.send(
                        content=f'Sorry, this menu is controlled by {user.name}!',
                        ephemeral=True
                    )
                    return inter_id == user_id
                
                await interaction.response.defer()
                q_cursor.delete_one({'Qid':q_id})
                q_cursor.insert_one(Question_Data)
                self.done_bt.disabled = True
                self.edit_bt.disabled = True
                await interaction.edit_original_message(view=self)
                await interaction.followup.send(
                    content='Question have been saved to the database!',
                    ephemeral=True
                )

        Embed = discord.Embed(
            title='Question Menu [OWNER]',
            description=(
                '> Question Preview :\n'
                '⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n'
                '> `Question :`\n'
                f'{Question_Data["Question"]}\n\n'
                '> `Answer :`\n'
                f'> `A :` {Question_Data["Answer"]["A"]}\n'
                f'> `B :` {Question_Data["Answer"]["B"]}\n'
                f'> `C :` {Question_Data["Answer"]["C"]}\n\n'
                f'> `Right Answer :` {Question_Data["R_Answer"]}\n'
                '⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯'
            )
            ,
            color=color
        )
        Embed.set_footer(text=f'Executor : {user.name} | {Time}')
        await interaction.followup.send(
            embed=Embed,
            view=Menu()
        )

    @app_commands.command(name='show_question')
    async def SQuest(self, interaction: discord.Interaction, q_id:str = None):
        """Bot Owners Command"""
        await interaction.response.defer()

        user = interaction.user
        user_id = user.id
        Time = datetime.datetime.now()

        if user_id != 755582460158279800:
            await interaction.followup.send(
                content = "Sorry You Can't use this command!",
                ephemeral = True
            )
            return user_id == 755582460158279800

        Qid_List = list(q_cursor.find({}))
        Lst_Hold = []

        for gets in Qid_List:
            Lst_Hold.append(gets['Qid'])

        Lst_Hold = ", ".join(Lst_Hold)
        if q_id == None:
            Embed = discord.Embed(
                title='command failed',
                description = f'> Please Enter an Qid Qid`indexnum`!\n\nQid_List : ```{Qid_List}```',
                color=color
            ) 
            Embed.set_footer(text=f'Executor : {user.name} | {Time}')
            await interaction.followup.send(embed=Embed)
            return
        
        Question_Data = q_cursor.find_one({'Qid':q_id})

        if Question_Data == None:
            Embed = discord.Embed(
                title='Question Not found!',
                description=f'> Question with id `{q_id}` was not found!',
                color=color
            )
            Embed.set_footer(text=f'Executor : {user.name} | {Time}')
            await interaction.followup.send(embed=Embed)
            return

        Question_Data = dict(Question_Data)
        Embed = discord.Embed(
            title='Question Menu [OWNER]',
            description=(
                '> Question Preview :\n'
                '⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n'
                '> `Question :`\n'
                f'{Question_Data["Question"]}\n\n'
                '> `Answer :`\n'
                f'> `A :` {Question_Data["Answer"]["A"]}\n'
                f'> `B :` {Question_Data["Answer"]["B"]}\n'
                f'> `C :` {Question_Data["Answer"]["C"]}\n'
                '⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯'
            )
            ,color=color
        )
        Embed.set_footer(text=f'Executor : {user.name} | {Time}')
        await interaction.followup.send(embed=Embed)

    @app_commands.command(name='exec')
    async def exec(self, interaction: discord.Interaction):
        """Bot Owners Command"""
        user = interaction.user
        user_id = user.id
        Time = datetime.datetime.now()
        bot = self.bot

        if user_id != 755582460158279800:
            await interaction.followup.send(
                content = "Sorry You Can't use this command!",
                ephemeral = True
            )
            return user_id == 755582460158279800

        class Exec_Modal(ui.Modal, title='Eval'):
            code = ui.TextInput(
                label='Code',
                required=True,
                style=discord.TextStyle.paragraph,
                max_length=3028
            )
            owner_holder = bot

            async def on_submit(self,interaction):
                await interaction.response.defer()
                str_obj = io.StringIO()

                try:
                    with contextlib.redirect_stdout(str_obj):
                        exec(self.code.value)

                except Exception as e:
                    return await interaction.followup.send(f"```py\n{e.__class__.__name__}: {e}\n```")

                await interaction.followup.send(f'```py\n{str_obj.getvalue()}\n```')

        await interaction.response.send_modal(Exec_Modal())

async def setup(bot):
    await bot.add_cog(owner_cmd(bot))