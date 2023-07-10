import os
import discord
import random
import pymongo
import json
import time
import datetime
import prettytable
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
nl = "\n"

#--------------------------------

RPG_DIVISION = {
	"Bronze":{"I":300,"II":450,"III":590,"IV":700},
	"Silver":{"I":900,"II":1100,"III":1300,"IV":1500},
	"Gold":{"I":2000,"II":2300,"III":2500,"IV":3000}
}

#--------------------------------

from PIL import Image, ImageDraw, ImageFont
import aiohttp
import asyncio
import random
import io

#---------------------------------

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

def calc_rank(rank, Division, point):
	while point > max(RPG_DIVISION[rank].values()):
		rank_index = list(RPG_DIVISION.keys()).index(rank) + 1
		if rank_index < len(RPG_DIVISION):
			rank = list(RPG_DIVISION.keys())[rank_index]
		else:
			break

	while point < min(RPG_DIVISION[rank].values()):
		rank_index = list(RPG_DIVISION.keys()).index(rank) - 1
		if rank_index >= 0:
			rank = list(RPG_DIVISION.keys())[rank_index]
		else:
			break
	
	for division, points in RPG_DIVISION[rank].items():
		if point >= points:
			new_division = division
		elif point <= 0:
			new_division = "I"
		else:
			new_division = {1:"I",2:"II",3:"III",4:"IV"}[Division]

	convert_division = {"I":1,"II":2,"III":3,"IV":4}[new_division]
	if new_division == "IV" and rank != "Gold":
		next_rank_index = list(RPG_DIVISION.keys()).index(rank) + 1
		next_rank = list(RPG_DIVISION.keys())[next_rank_index]
		next_division = "I"
		next_requirement = RPG_DIVISION[next_rank][next_division]

	elif new_division == "IV" and rank == "Gold":
		next_division = None
		next_requirement = "MAX"

	else:
		next_division = {1:"I",2:"II",3:"III",4:"IV"}[convert_division+1]
		next_requirement = RPG_DIVISION[rank][next_division]
	
	return [f"{rank}", f"{new_division}", convert_division, next_requirement]

#--------------------------------

async def get_image(url):
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as response:
			data = await response.read()
			return Image.open(io.BytesIO(data))

async def get_card(data:dict=None, PFP_URL=None, name:str=None):
	if data == None:
		return

	Name = name

	Jobs = data['Jobs_Data']['CJobs']
	Level = data['N_economy_Data']['Level']
	Money = data['N_economy_Data']['Money']
	Sallary = None

	Exp = data['N_economy_Data']['Exp']
	Max_Exp = data['N_economy_Data']['MaxExp']

	Badges = [f"{data['SJ-DATA']['RANK_DATA']['C_RANK']}_Badge.png",]
	for BHolder in range(len(data['User_Badges']['Use'])+1):
		try:
			Badges.append(f"{data['User_Badges']['Use'][BHolder]}_Badge.png",)
		except:
			pass

	if Jobs == 'CyberProgramming':
		Sallary = data['Jobs_Data']['CSall']

	base_background = None
	buffer = io.BytesIO()

	#round(int(amount)/(m_length/length))

	with Image.open(f'./img_folder/USER_CARD_RAW_{Jobs}.png') as base_background, Image.open(f'./img_folder/PROGRESS_GRAY.png') as Gray_Line, Image.open(f'./img_folder/PROGRESS_RED.png') as Red_Line:
		base_draw = ImageDraw.Draw(base_background)
		Exp_Line_Lenght = min(round((Exp / Max_Exp * 100) / 100 * 400), (400)) - 185
		
		if PFP_URL != None:
			pfp = await get_image(PFP_URL)
			pfp = pfp.resize((122,122), resample=Image.Resampling.BILINEAR)
			base_background.paste(pfp, (35, 39))

		for Add_BGS in range(len(Badges)):
			with Image.open(f'./img_folder/{Badges[Add_BGS]}') as badge:
				badge = badge.resize((35,35), resample=Image.Resampling.BILINEAR)

				if Add_BGS == 0:
					base_background.paste(badge, (585, 35), mask=badge)
				elif Add_BGS == 1:
					base_background.paste(badge, (545, 35), mask=badge)
				else:
					base_background.paste(badge, (506, 35), mask=badge)

		# EMPTY / DEFAULT BAR
		base_background.paste(Gray_Line, (176, 90), mask=Gray_Line.convert('RGBA'))
		base_background.paste(Gray_Line, (394, 90), mask=Gray_Line.convert('RGBA'))
		base_draw.line(
			(185, 97, 400, 97),
			fill=(115, 115, 115),
			width=16
		)

		base_background.paste(Gray_Line, (176, 119), mask=Gray_Line.convert('RGBA'))
		base_background.paste(Gray_Line, (394, 119), mask=Gray_Line.convert('RGBA'))
		base_draw.line(
			(185, 126, 400, 126),
			fill=(115, 115, 115),
			width=16
		)

		# RED PROGRESS
		base_background.paste(Red_Line, (176, 90), mask=Red_Line.convert('RGBA'))
		if Exp_Line_Lenght == 215:
			base_background.paste(Red_Line, (394, 90), mask=Red_Line.convert('RGBA')) # MAX => 394, 90

		else:
			base_background.paste(
				Red_Line,((176+Exp_Line_Lenght), 90),
				mask=Red_Line.convert('RGBA')
			)

		if Exp_Line_Lenght <= 0:
			Exp_Line_Lenght = 6

		base_draw.line(
			(185, 97, (185+Exp_Line_Lenght), 97),
			fill=(255, 22, 85),
			width=16
		)

		base_draw.text(
			(175, 28), #x (-), y (|)
			f"{Name}",
			font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 35),
			fill=(255, 255, 255)
		)  

		base_draw.text(
			(190, 90), #x (-), y (|)
			f"{Exp:,}/{Max_Exp:,} EXP | {Level:,} LEVEL",
			font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 11),
			fill=(255, 255, 255)
		)  

		base_draw.text(
			(190, 119), #x (-), y (|)
			f"{Money:,} CB",
			font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 11),
			fill=(255, 255, 255)
		)

		if Jobs != 'CyberTuber':
			base_draw.text(
				(472, 100), #x (-), y (|)
				f"{Sallary:,} CB",
				font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 16),
				fill=(255, 255, 255)
			)
			
		base_background.save(buffer, format='png')
		return buffer.getvalue()

	# img_id = random.randint(1,999999999)
	# filename = f'{img_id}.png'
	# base_background.save(f'./img_folder/{filename}')
	# base_background.close()

	# return filename, f'./img_folder/{filename}'

async def battle_card(data:list=None, PFP_URL:dict=None, name:dict=None):
	buffer = io.BytesIO()
	base_background = None
	time_start = time.time()

	# user + enemy name
	user_name = str(name['User'])[0:7]
	enemy_name = str(name['Enemy'])[0:7]

	if len(user_name) >= 7:
		user_name += "..."

	if len(enemy_name) >= 7:
		enemy_name += "..."

	# getting user + enemy pfp
	user_pfp = await get_image(PFP_URL['User_Pfp'])
	enemy_pfp = await get_image(PFP_URL['EUser_Pfp'])

	user_pfp = user_pfp.resize((153,153), resample=Image.Resampling.BILINEAR)
	enemy_pfp = enemy_pfp.resize((160,160), resample=Image.Resampling.BILINEAR)

	with Image.open("./img_folder/Battle_Background.png") as base_background, Image.open(f'./img_folder/PROGRESS_GRAY.png') as Gray_Line, Image.open(f'./img_folder/PROGRESS_RED.png') as Red_Line:
		base_draw = ImageDraw.Draw(base_background)
		Gray_Line = Gray_Line.resize((44, 44), resample=Image.Resampling.BILINEAR)
		Red_Line = Red_Line.resize((44, 44), resample=Image.Resampling.BILINEAR)

		base_background.paste(user_pfp, (65, 64), mask=user_pfp.convert('RGBA'))
		base_background.paste(enemy_pfp, (1700, 60), mask=enemy_pfp.convert('RGBA'))

		base_draw.text(
			(240, 52), #x (-), y (|)
			f"{user_name}",
			font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 65),
			fill=(255, 255, 255)
		)

		base_draw.text(
			(1680, 115), #x (-), y (|)
			f"{enemy_name}",
			font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 63),
			fill=(255, 255, 255),
			anchor="rs"
		)

		u_img_pointer = 1
		e_img_pointer = 1

		for get in data[0]:
			Computer_Name = get["Comp"]
			Computer_CHealt = get["CHEALT"]
			Computer_Healt = get["C_Hlt"]
			Computer_Damage = f'{get["B_Dmg"]} - {get["M_Dmg"]}'
			Computer_CritRt = get["C_Rte"]
			Computer_CritDm = get["C_Dmg"]
			Computer_Defs = get["B_Def"]
			Computer_Level = get["C_Lvl"]
			Computer_MLevel = get["C_Mlv"]

			with Image.open(f"./img_folder/SideJobs_Img/PC/{Computer_Name}.png") as computer:
				computer = computer.resize((250,250), resample=Image.Resampling.BILINEAR)
				c_name_transform = Computer_Name.replace('_', ' ' )

				Healt_Lenght = min(round((Computer_CHealt / Computer_Healt * 100) / 100 * 457), (457))
				Saved_Lenght = Healt_Lenght # SAVING FOR ANOTHER CALCULATION

				if Healt_Lenght <= 25:
					Healt_Lenght = 25

				if u_img_pointer == 1:
					base_background.paste(computer, (60, 250), mask=computer.convert("RGBA"))
					base_draw.text(
						(310, 300), #x (-), y (|)
						c_name_transform,
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 30),
						fill=(255, 255, 255)
					)

					base_background.paste(Gray_Line, (740, 263), mask=Gray_Line.convert('RGBA'))
					base_draw.line(
						(303, 284, 760, 284), # X Y X Y (-) (|) (-) (|) OR FIRST POINT => REACH POINT
						fill=(115, 115, 115),
						width=44
					)

					base_background.paste(Red_Line, (((303 + Healt_Lenght)-20), 263), mask=Gray_Line.convert('RGBA'))
					base_draw.line(
						(303, 284, (303+ Healt_Lenght), 284), # X Y X Y (-) (|) (-) (|) OR FIRST POINT => REACH POINT
						fill=(255, 22, 85),
						width=44
					)

					base_draw.text(
						(310, 257), #x (-), y (|)
						f"{Computer_CHealt}/{Computer_Healt} HP",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 38),
						fill=(255, 255, 255)
					)

					base_draw.text(
						(400, 381), #x (-), y (|)
						f"{Computer_Damage} DMG",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 22),
						fill=(255, 255, 255)
					)

					base_draw.text(
						(640, 381), #x (-), y (|)
						f"{Computer_Defs} DEF",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 22),
						fill=(255, 255, 255)
					)

					base_draw.text(
						(398, 455), #x (-), y (|)
						f"{Computer_CritDm}% CDMG - {Computer_CritRt}% CR",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 15),
						fill=(255, 255, 255)
					)

				elif u_img_pointer == 2:
					base_background.paste(computer, (60, 500), mask=computer.convert("RGBA"))
					base_draw.text(
						(310, 564), #x (-), y (|)
						c_name_transform,
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 30),
						fill=(255, 255, 255)
					)

					base_background.paste(Gray_Line, (740, 527), mask=Gray_Line.convert('RGBA'))
					base_draw.line(
						(303, 548, 760, 548), # X Y X Y (-) (|) (-) (|) OR FIRST POINT => REACH POINT
						fill=(115, 115, 115),
						width=44
					)

					base_background.paste(Red_Line, (((303 + Healt_Lenght)-20), 527), mask=Gray_Line.convert('RGBA'))
					base_draw.line(
						(303, 548, (303 + Healt_Lenght), 548), # X Y X Y (-) (|) (-) (|) OR FIRST POINT => REACH POINT
						fill=(255, 22, 85),
						width=44
					)

					base_draw.text(
						(310, 520), #x (-), y (|)
						f"{Computer_CHealt}/{Computer_Healt} HP",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 38),
						fill=(255, 255, 255)
					)

					base_draw.text(
						(400, 640), #x (-), y (|)
						f"{Computer_Damage} DMG",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 22),
						fill=(255, 255, 255)
					)

					base_draw.text(
						(640, 640), #x (-), y (|)
						f"{Computer_Defs} DEF",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 22),
						fill=(255, 255, 255)
					)

					base_draw.text(
						(398, 715), #x (-), y (|)
						f"{Computer_CritDm}% CDMG - {Computer_CritRt}% CR",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 15),
						fill=(255, 255, 255)
					)
				
				else:
					base_background.paste(computer, (60, 780), mask=computer.convert("RGBA"))
					base_draw.text(
						(310, 828), #x (-), y (|)
						c_name_transform,
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 30),
						fill=(255, 255, 255)
					)

					base_background.paste(Gray_Line, (740, 790), mask=Gray_Line.convert('RGBA'))
					base_draw.line(
						(303, 811, 760, 811), # X Y X Y (-) (|) (-) (|) OR FIRST POINT => REACH POINT
						fill=(115, 115, 115),
						width=44
					)

					base_background.paste(Red_Line, (((303 + Healt_Lenght)-20), 790), mask=Gray_Line.convert('RGBA'))
					base_draw.line(
						(303, 811, (303 + Healt_Lenght), 811), # X Y X Y (-) (|) (-) (|) OR FIRST POINT => REACH POINT
						fill=(255, 22, 85),
						width=44
					)

					base_draw.text(
						(310, 785), #x (-), y (|)
						f"{Computer_CHealt}/{Computer_Healt} HP",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 38),
						fill=(255, 255, 255)
					)

					base_draw.text(
						(400, 908), #x (-), y (|)
						f"{Computer_Damage} DMG",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 22),
						fill=(255, 255, 255)
					)

					base_draw.text(
						(640, 908), #x (-), y (|)
						f"{Computer_Defs} DEF",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 22),
						fill=(255, 255, 255)
					)

					base_draw.text(
						(398, 983), #x (-), y (|)
						f"{Computer_CritDm}% CDMG - {Computer_CritRt}% CR",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 15),
						fill=(255, 255, 255)
					)

			u_img_pointer += 1

		for get in data[1]:
			Computer_Name = get["Comp"]
			Computer_CHealt = get["CHEALT"]
			Computer_Healt = get["C_Hlt"]
			Computer_Damage = f'{get["B_Dmg"]} - {get["M_Dmg"]}'
			Computer_CritRt = get["C_Rte"]
			Computer_CritDm = get["C_Dmg"]
			Computer_Defs = get["B_Def"]
			Computer_Level = get["C_Lvl"]
			Computer_MLevel = get["C_Mlv"]

			with Image.open(f"./img_folder/SideJobs_Img/PC/{Computer_Name}.png") as computer:
				computer = computer.resize((250,250), resample=Image.Resampling.BILINEAR)
				c_name_transform = Computer_Name.replace('_', ' ')

				Healt_Lenght = min(round((Computer_CHealt / Computer_Healt * 100) / 100 * 500), (500))
				Saved_Lenght = Healt_Lenght # SAVING FOR ANOTHER CALCULATION

				if Healt_Lenght <= 25:
					Healt_Lenght = 25

				if e_img_pointer == 1:
					base_background.paste(computer, (1610, 250), mask=computer.convert("RGBA"))
					base_draw.text(
						(1360, 300), #x (-), y (|)
						c_name_transform,
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 30),
						fill=(255, 255, 255)
					)

					base_background.paste(Gray_Line, ((1115-20), 263), mask=Gray_Line.convert('RGBA'))
					base_draw.line(
						(1115, 284, 1615, 284), # X Y X Y (-) (|) (-) (|) OR FIRST POINT => REACH POINT
						fill=(115, 115, 115),
						width=44
					)

					base_background.paste(Red_Line, (((1615 - Healt_Lenght) - 20), 263), mask=Gray_Line.convert('RGBA'))
					base_draw.line(
						((1615 - Healt_Lenght), 284, 1615, 284), # X Y X Y (-) (|) (-) (|) OR FIRST POINT => REACH POINT
						fill=(255, 22, 85),
						width=44
					)

					base_draw.text(
						(1605, 298), #x (-), y (|)
						f"{Computer_CHealt}/{Computer_Healt} HP",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 38),
						fill=(255, 255, 255),
						anchor="rs"
					)

					base_draw.text(
						(1515, 400), #x (-), y (|)
						f"{Computer_Damage} DMG",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 22),
						fill=(255, 255, 255),
						anchor="rs"
					)

					base_draw.text(
						(1250, 403), #x (-), y (|)
						f"{Computer_Defs} DEF",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 22),
						fill=(255, 255, 255),
						anchor="rs"
					)

					base_draw.text(
						(1515, 473), #x (-), y (|)
						f"{Computer_CritDm}% CDMG - {Computer_CritRt}% CR",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 15),
						fill=(255, 255, 255),
						anchor="rs"
					)

				elif e_img_pointer == 2:
					base_background.paste(computer, (1610, 500), mask=computer.convert("RGBA"))
					base_draw.text(
						(1360, 564), #x (-), y (|)
						c_name_transform,
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 30),
						fill=(255, 255, 255)
					)

					base_background.paste(Gray_Line, ((1115-20), 527), mask=Gray_Line.convert('RGBA'))
					base_draw.line(
						(1115, 548, 1615, 548), # X Y X Y (-) (|) (-) (|) OR FIRST POINT => REACH POINT
						fill=(115, 115, 115),
						width=44
					)

					base_background.paste(Red_Line, (((1615 - Healt_Lenght) - 20), 527), mask=Gray_Line.convert('RGBA'))
					base_draw.line(
						((1615 - Healt_Lenght), 548, 1615, 548), # X Y X Y (-) (|) (-) (|) OR FIRST POINT => REACH POINT
						fill=(255, 22, 85),
						width=44
					)

					base_draw.text(
						(1607, 563), #x (-), y (|)
						f"{Computer_CHealt}/{Computer_Healt} HP",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 38),
						fill=(255, 255, 255),
						anchor="rs"
					)

					base_draw.text(
						(1515, 660), #x (-), y (|)
						f"{Computer_Damage} DMG",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 22),
						fill=(255, 255, 255),
						anchor="rs"
					)

					base_draw.text(
						(1250, 663), #x (-), y (|)
						f"{Computer_Defs} DEF",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 22),
						fill=(255, 255, 255),
						anchor="rs"
					)

					base_draw.text(
						(1515, 733), #x (-), y (|)
						f"{Computer_CritDm}% CDMG - {Computer_CritRt}% CR",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 15),
						fill=(255, 255, 255),
						anchor="rs"
					)
				
				else:
					base_background.paste(computer, (1610, 780), mask=computer.convert("RGBA"))
					base_draw.text(
						(1360, 828), #x (-), y (|)
						c_name_transform,
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 30),
						fill=(255, 255, 255)
					)

					base_background.paste(Gray_Line, ((1115 - 20), 790), mask=Gray_Line.convert('RGBA'))
					base_draw.line(
						(1115, 811, 1615, 811), # X Y X Y (-) (|) (-) (|) OR FIRST POINT => REACH POINT
						fill=(115, 115, 115),
						width=44
					)

					base_background.paste(Red_Line, (((1615 - Healt_Lenght) - 20), 790), mask=Gray_Line.convert('RGBA'))
					base_draw.line(
						((1615 - Healt_Lenght), 811, 1615, 811), # X Y X Y (-) (|) (-) (|) OR FIRST POINT => REACH POINT
						fill=(255, 22, 85),
						width=44
					)

					base_draw.text(
						(1605, 828), #x (-), y (|)
						f"{Computer_CHealt}/{Computer_Healt} HP",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 38),
						fill=(255, 255, 255),
						anchor="rs"
					)

					base_draw.text(
						(1515, 923), #x (-), y (|)
						f"{Computer_Damage} DMG",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 22),
						fill=(255, 255, 255),
						anchor="rs"
					)

					base_draw.text(
						(1260, 926), #x (-), y (|)
						f"{Computer_Defs} DEF",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 22),
						fill=(255, 255, 255),
						anchor="rs"
					)

					base_draw.text(
						(1520, 995), #x (-), y (|)
						f"{Computer_CritDm}% CDMG - {Computer_CritRt}% CR",
						font=ImageFont.truetype('font/OpenSans-ExtraBold.ttf', 15),
						fill=(255, 255, 255),
						anchor="rs"
					)

			e_img_pointer += 1
		
		base_background.save(buffer, format='png')
		return [buffer.getvalue(), f"{round(time.time() - time_start)}s"]

#--------------------------------

class Rpg_Cmd(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@app_commands.command(name="battle")
	async def TESTING_BATTLE(self, interaction:discord.Interaction, User:discord.User=None):
		"""Hacking Computer Battle Between Player!"""
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
		Emoji_9 = discord.utils.get(Guild.emojis, name='CYBEXP')

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
			return await interaction.followup.send(embed=Embed)

		#----------

		if User == None:
			ENEMY = list(cursor.find({}))
			SELECTOR = None

			for holder in ENEMY:
				SELECTOR = random.choice(ENEMY)
				if SELECTOR["id"] != user_id:
					break

			ENEMY = SELECTOR
			ENEMY_USER = self.bot.get_user(ENEMY["id"])

			if ENEMY_USER != None:
				ENEMY_NAME = ENEMY_USER.name
				ENEMY_PFP = ENEMY_USER.display_avatar.url

			else:
				ENEMY_NAME = SELECTOR["name"]
				ENEMY_PFP = "https://cdn.discordapp.com/attachments/979708146421489706/1118458604291362816/OIP.jpg"

		else:
			ENEMY = cursor.find_one({"id":User.id})

			if ENEMY is None:
				Embed = discord.Embed(
					title=f'{Emoji_1} | Command Failed',
					description=f"> Can't start the battle because {User.name} didn't have CyberAccount!",
					color=color
				)
				Embed.set_footer(text=f'Executor : {user_name} | {Time}')
				Embed.set_thumbnail(url=User.display_avatar.url)
				return await interaction.followup.send(embed=Embed)

			ENEMY_NAME = User.name
			ENEMY_PFP = User.display_avatar.url

		#----------

		USER_PARTY = check["SJ-DATA"]["COMP_PRTY"]
		ENEM_PARTY = ENEMY["SJ-DATA"]["COMP_PRTY"]

		for comp_hold in  USER_PARTY:
			comp_hold["CHEALT"] = comp_hold["C_Hlt"]

		for enemy_comp_hold in  ENEM_PARTY:
			enemy_comp_hold["CHEALT"] = enemy_comp_hold["C_Hlt"]

		UComp_Select = []
		EComp_Select = []

		UComp_List = []
		EComp_List = []

		Ucount = 0
		Ecount = 0

		#----------

		for U_loop_hold in range(3):
			try:
				USER_PARTY[Ucount]["CHEALT"] = USER_PARTY[U_loop_hold]["C_Hlt"]
				UComp_Select.append(discord.SelectOption(
					label = f"{USER_PARTY[U_loop_hold]['Comp']} | USER",
					description = f"Select {USER_PARTY[U_loop_hold]['Comp'].replace('_', ' ')} To Do Action",
					value = f"U{U_loop_hold}"
				))
				UComp_List.append(f'> [] | {USER_PARTY[U_loop_hold]["Comp"]} - <SU{U_loop_hold}>')

			except:
				UComp_Select.append(discord.SelectOption(
					label = f"NONE",
					description = f"NONE",
					value = f"None {U_loop_hold}"
				))
				UComp_List.append(f'> [] | NONE - <SU{U_loop_hold}>')

		for E_loop_hold in range(3):
			try:
				ENEM_PARTY[Ecount]["CHEALT"] = ENEM_PARTY[E_loop_hold]["C_Hlt"]
				EComp_Select.append(discord.SelectOption(
					label = f"{USER_PARTY[E_loop_hold]['Comp']} | ENEMY",
					description = f"Select {ENEM_PARTY[E_loop_hold]['Comp'].replace('_', ' ')} To Be Attacked",
					value = f"E{E_loop_hold}"
				))
				EComp_List.append(f'> [] | {ENEM_PARTY[E_loop_hold]["Comp"]} - <SE{E_loop_hold}>')

			except:
				EComp_Select.append(discord.SelectOption(
					label = f"NONE",
					description = f"NONE",
					value = f"None {E_loop_hold}"
				))
				EComp_List.append(f'> [] | NONE - <SE{E_loop_hold}>')

		Image_Procces = await battle_card(
			[USER_PARTY, ENEM_PARTY],
			{"User_Pfp":user_pfp, "EUser_Pfp":ENEMY_PFP},
			{"User":user_name,"Enemy":ENEMY_NAME}
		)

		class Menu(discord.ui.View):
			def __init__(self):
				super().__init__()
				self.current_turn = 0

				self.current_user_selected = []
				self.current_enmy_selected = []
				self.battle_current_mssage = []

				self.default_description = (
					f"> **{user_name}'s Computer :**{nl}"
					f"{nl.join(UComp_List)}{nl}{nl}"
					f"> **{ENEMY_NAME}'s Computer :**{nl}"
					f"{nl.join(EComp_List)}{nl}{nl}"
					f"```diff{nl}<Battle Message>```"
				)

				self.based_turn_descript = None
				self.current_turn_action = []
				self.turn_done = []

				self.UComputer_Destroyed = []
				self.EComputer_Destroyed = []

				self.user_dodge_chance = [15,15,15]
				self.enmy_dodge_chance = [15,15,15]
				self.end_turn_button.disabled = True

				self.damage_total = 0
				self.damaged_total = 0
				self.dodge_total = 0

				self.battle_states = None

			@ui.select(placeholder='USER COMPUTER', max_values=3, min_values=1, options=UComp_Select)
			async def u_computer_callback(self, interaction, select:discord.ui.Select):
				interid = interaction.user.id

				if interid != user_id:
					await interaction.response.defer()
					await interaction.followup.send(
						content=f'Sorry, this menu is controlled by {user.name}!',
						ephemeral=True
					)
					return interid == user_id

				await interaction.response.defer()
				if self.based_turn_descript == None:
					Desc_Holder = self.default_description
				else:
					Desc_Holder = self.based_turn_descript

				for get in range(len(select.values)):
					curr = select.values[get].split()[0]
					if curr != "None":
						if curr not in self.current_user_selected and curr not in self.turn_done and curr not in self.UComputer_Destroyed:
							self.current_user_selected.append(select.values[get])
							self.battle_current_mssage.append(f"+ {user_name} SELECTING PC <{select.values[get]}>")
							Desc_Holder = Desc_Holder.replace(f"S{select.values[get]}", f"**SELECTED-{select.values[get]}**")

						elif (curr in self.current_user_selected) or (curr in self.current_user_selected and curr in self.turn_done) or (curr in self.UComputer_Destroyed):
							self.current_user_selected.remove(f"{select.values[get]}")
							self.battle_current_mssage.append(f"+ {user_name} UN-SELECTING PC {select.values[get]}")
							Desc_Holder = Desc_Holder.replace(f"**SELECTED-{select.values[get]}**", f"S{select.values[get]}")

						elif (curr not in self.current_user_selected and curr in self.turn_done):
							self.battle_current_mssage.append(
								f"+ {user_name}'s SELECTING PC <{select.values[get]}> But Failed. Because the PC has been used before"
							)

						elif (curr not in self.current_user_selected and curr in self.UComputer_Destroyed):
							self.battle_current_mssage.append(
								f"+ {user_name}'s SELECTING PC <{select.values[get]}> But Failed. Because the PC has been destyoyed"
							)							

				Desc_Holder = Desc_Holder.replace(f"<Battle Message>", f"{nl.join(self.battle_current_mssage[-5:])}")
				Embed = discord.Embed(
					title=f"{user_name} CyberHack Battle",
					description=Desc_Holder,
					color=color
				)
				Embed.set_footer(text=f"Executor : {user_name} | {Time}")
				Embed.set_image(url=f'attachment://{user_name}_battle.png')
				self.based_turn_descript = Desc_Holder.replace(f"{nl.join(self.battle_current_mssage[-5:])}", "<Battle Message>")
				await interaction.edit_original_message(embed=Embed)

			@ui.select(placeholder='ENEMY COMPUTER', max_values=1, min_values=1, options=EComp_Select)
			async def e_computer_callback(self, interaction, select:discord.ui.Select):
				interid = interaction.user.id

				if interid != user_id:
					await interaction.response.defer()
					await interaction.followup.send(
						content=f'Sorry, this menu is controlled by {user.name}!',
						ephemeral=True
					)
					return interid == user_id

				await interaction.response.defer()
				if self.based_turn_descript == None:
					Desc_Holder = self.default_description
				else:
					Desc_Holder = self.based_turn_descript

				for get in range(len(select.values)):
					curr = select.values[get].split()[0]
					if curr != "None":
						if curr not in self.current_enmy_selected and curr not in self.EComputer_Destroyed:
							self.current_enmy_selected.append(select.values[get])
							self.battle_current_mssage.append(f"- {user_name}'s TARGETTING PC <{select.values[get]}>")
							Desc_Holder = Desc_Holder.replace(f"S{select.values[get]}", "**TARGETTED**")

						elif (curr in self.current_enmy_selected) or (curr in self.current_enmy_selected and curr in self.EComputer_Destroyed):
							self.current_enmy_selected.remove(f"{select.values[get]}")
							self.battle_current_mssage.append(f"- {user_name}'s UN-TARGETTING PC {select.values[get]}")
							Desc_Holder = Desc_Holder.replace(f"**TARGETTED**", f"S{select.values[get]}")

						elif (curr not in self.current_enmy_selected and curr in self.EComputer_Destroyed):
							self.battle_current_mssage.append(
								f"+ {user_name}'s TARGETTING PC <{select.values[get]}> But Failed. Because the enemy PC has been destyoyed"
							)							

				Desc_Holder = Desc_Holder.replace(f"<Battle Message>", f"{nl.join(self.battle_current_mssage[-5:])}")
				Embed = discord.Embed(
					title=f"{user_name} CyberHack Battle",
					description=Desc_Holder,
					color=color
				)
				Embed.set_footer(text=f"Executor : {user_name} | {Time}")
				Embed.set_image(url=f'attachment://{user_name}_battle.png')
				self.based_turn_descript = Desc_Holder.replace(f"{nl.join(self.battle_current_mssage[-5:])}", "<Battle Message>")
				await interaction.edit_original_message(embed=Embed)

			@ui.button(label="ATK", style=discord.ButtonStyle.green)
			async def attack_button(self, interaction, button: ui.Button):
				interid = interaction.user.id

				if interid != user_id:
					await interaction.response.defer()
					await interaction.followup.send(
						content=f'Sorry, this menu is controlled by {user.name}!',
						ephemeral=True
					)
					return interid == user_id

				await interaction.response.defer()

				if len(self.current_user_selected) <= 0 or len(self.current_enmy_selected) <= 0:
					return await interaction.followup.send(
						content=f"{user_name} Please Select Your Pc and Enemy Pc To Do The Action!",
						ephemeral=True
					)

				for get in range(len(self.current_user_selected)):
					if self.current_user_selected[get] not in self.turn_done:
						self.current_turn_action.append(
							[self.current_user_selected[get], "ATTACK", self.current_enmy_selected[0], False]
						)

				Attack_States = None
				Desc_Holder = self.based_turn_descript
				for holder_loops in range(len(self.current_turn_action)):
					states = self.current_turn_action[holder_loops][3]

					if states != True and self.current_turn_action[holder_loops][1] == "ATTACK":
						E_ids = int(self.current_enmy_selected[0].replace("E", ""))
						ids = int(self.current_turn_action[holder_loops][0].replace('U', ''))

						Attack_Message = f"+ {user_name}'s Hacking {ENEMY_NAME}'s PC <{E_ids}> And Dealt " + "{DMG_HOLDER} {DAMAGE_TYPE}!"

						# ATTACKER SECTION

						Computer = USER_PARTY[ids]["Comp"]
						Current_Healt = USER_PARTY[ids]["CHEALT"]

						Start_Damage = USER_PARTY[ids]["B_Dmg"]
						End_Damage = USER_PARTY[ids]["M_Dmg"]

						Crit_Rate = USER_PARTY[ids]["C_Rte"]
						Crit_Damage = USER_PARTY[ids]["C_Dmg"]

						# Generating Random Attack Damage (NO C-RATE / C-DMG)
						Damage_Base = random.randint(Start_Damage, End_Damage)
						Attack_Message = Attack_Message.replace("{DAMAGE_TYPE}", f"Virus Damage")

						# Generating Crit-Damage
						Crit_Rolls = random.randint(1, 100)
						if not Crit_Rate < Crit_Rolls:
							Damage_Base = int(Damage_Base + (Crit_Damage / 100))
							Attack_Message = Attack_Message.replace("Virus Damage", f"Crit-Virus Damage")

						# DEFENDER SECTION
						
						EComputer = ENEM_PARTY[E_ids]["Comp"]
						ECurrent_Healt = ENEM_PARTY[E_ids]["CHEALT"]
						EBase_Defense = USER_PARTY[E_ids]["B_Def"]

						# Reduce Damage That Dealt Using Base_Defence
						Damage_Base -= random.randint(EBase_Defense, (EBase_Defense + random.randint(1, 3)))
						if Damage_Base <= 0:
							Damage_Base = 5

						Attack_Message = Attack_Message.replace("{DMG_HOLDER}", f"<{Damage_Base}>")						

						# Generating Enemy Dodge
						Dodge_Chance = self.enmy_dodge_chance[E_ids]
						Dodge_Rolls = random.randint(1, 100)

						if not Dodge_Chance < Dodge_Rolls:
							Damage_Base = 0
							Attack_Message = f"+ {user_name}'s Trying To Hack {ENEMY_NAME}'s PC but Failed."

						ENEM_PARTY[E_ids]["CHEALT"] -= int(Damage_Base + 10000)
						if ENEM_PARTY[E_ids]["CHEALT"] <= 0:
							ENEM_PARTY[E_ids]["CHEALT"] = 0
							ENEM_PARTY[E_ids]["Computer"] = "Destroyed_Pc"
							self.EComputer_Destroyed.append(f"E{E_ids}")
							self.battle_current_mssage.append(f"+ {ENEMY_NAME}'s PC <E{E_ids}> Has Been Destroyed!")

						self.damage_total += Damage_Base
						self.battle_current_mssage.append(Attack_Message)
						self.current_turn_action[holder_loops].remove(False)
						self.current_turn_action[holder_loops].append(True)
						self.turn_done.append(f"U{ids}")

						Desc_Holder = Desc_Holder.replace(f"<Battle Message>", f"{nl.join(self.battle_current_mssage[-5:])}")
						Desc_Holder = Desc_Holder.replace(f"<**SELECTED-U{ids}**>", "<**TURN-USED**>")
						Attack_States = True

					else:
						Attack_States = False

				if Attack_States:
					Image_Procces = await battle_card(
						[USER_PARTY, ENEM_PARTY],
						{"User_Pfp":user_pfp, "EUser_Pfp":ENEMY_PFP},
						{"User":user_name,"Enemy":ENEMY_NAME}
					)

					if len(self.EComputer_Destroyed) >= len(ENEM_PARTY):
						for items in self.children:
							items.disabled = True
							if items.type == discord.ComponentType.button:
								items.style = discord.ButtonStyle.green

						self.battle_states = "WIN"
						self.end_turn_button.disabled = False

					elif len(self.UComputer_Destroyed) >= len(USER_PARTY):
						for items in self.children:
							items.disabled = True
							if items.type == discord.ComponentType.button:
								items.style = discord.ButtonStyle.red

						self.battle_states = "LOSE"
						self.end_turn_button.disabled = False

					elif len(self.turn_done) >= len(USER_PARTY):
						for items in self.children:
							items.disabled = True

						self.surrender_button.disabled = False
						self.end_turn_button.disabled = False

					Send_Image = discord.File(fp=io.BytesIO(Image_Procces[0]), filename=f'{user_name}_battle.png')
					Embed = discord.Embed(
						title=f"{user_name} CyberHack Battle",
						description=Desc_Holder,
						color=color
					)
					Embed.set_footer(text=f"Executor : {user_name} | {Time}")
					Embed.set_image(url=f'attachment://{user_name}_battle.png')
					self.based_turn_descript = Desc_Holder.replace(f"{nl.join(self.battle_current_mssage[-5:])}", "<Battle Message>")
					return await interaction.edit_original_message(attachments=[Send_Image], embed=Embed, view=self)

				return await interaction.followup.send(content="Please Select Another PC To Do The Action.", ephemeral=True)

			@ui.button(label="DEF", style=discord.ButtonStyle.blurple)
			async def defense_button(self, interaction, button: ui.Button):
				interid = interaction.user.id

				if interid != user_id:
					await interaction.response.defer()
					await interaction.followup.send(
						content=f'Sorry, this menu is controlled by {user.name}!',
						ephemeral=True
					)
					return interid == user_id

				await interaction.response.defer()

				if len(self.current_user_selected) <= 0 or len(self.current_enmy_selected) <= 0:
					return await interaction.followup.send(
						content=f"{user_name} Please Select Your Pc and Enemy Pc To Do The Action!",
						ephemeral=True
					)

				for get in range(len(self.current_user_selected)):
					if self.current_user_selected[get] not in self.turn_done:
						self.current_turn_action.append(
							[self.current_user_selected[get], "DEFF", self.current_enmy_selected[0], False]
						)

				Deff_States  = None
				Desc_Holder = self.based_turn_descript
				for holder_loops in range(len(self.current_turn_action)):
					states = self.current_turn_action[holder_loops][3]

					if states != True and self.current_turn_action[holder_loops][1] == "DEFF":
						ids = int(self.current_turn_action[holder_loops][0].replace('U', ''))

						# Increasing Number of PC Defense By 40% And Increasing PC Dodge Chance By 10%
						Base_deff = USER_PARTY[ids]["B_Def"]
						Base_deff = int(Base_deff * 0.4)
						USER_PARTY[ids]["B_Def"] = Base_deff
						self.user_dodge_chance[ids] += 10

						self.current_turn_action[holder_loops].remove(False)
						self.current_turn_action[holder_loops].append(True)
						self.turn_done.append(f"U{ids}")
						self.battle_current_mssage.append(f"+ {user_name}'s PC <U{ids}> Deffense has been increase by 40%!")

						Desc_Holder = Desc_Holder.replace(f"<Battle Message>", f"{nl.join(self.battle_current_mssage[-5:])}")
						Desc_Holder = Desc_Holder.replace(f"<**SELECTED-U{ids}**>", "<**TURN-USED**>")
						Deff_States = True

					else:
						Deff_States = False

				if Deff_States:
					Image_Procces = await battle_card(
						[USER_PARTY, ENEM_PARTY],
						{"User_Pfp":user_pfp, "EUser_Pfp":ENEMY_PFP},
						{"User":user_name,"Enemy":ENEMY_NAME}
					)

					if len(self.EComputer_Destroyed) >= len(ENEM_PARTY):
						for items in self.children:
							items.disabled = True
							if items.type == discord.ComponentType.button:
								items.style = discord.ButtonStyle.green

						self.battle_states = "WIN"
						self.end_turn_button.disabled = False

					if len(self.UComputer_Destroyed) >= len(USER_PARTY):
						for items in self.children:
							items.disabled = True
							if items.type == discord.ComponentType.button:
								items.style = discord.ButtonStyle.red

						self.battle_states = "LOSE"
						self.end_turn_button.disabled = False

					if len(self.turn_done) >= len(USER_PARTY):
						for items in self.children:
							items.disabled = True

						self.surrender_button.disabled = False
						self.end_turn_button.disabled = False

					Send_Image = discord.File(fp=io.BytesIO(Image_Procces[0]), filename=f'{user_name}_battle.png')
					Embed = discord.Embed(
						title=f"{user_name} CyberHack Battle",
						description=Desc_Holder,
						color=color
					)
					Embed.set_footer(text=f"Executor : {user_name} | {Time}")
					Embed.set_image(url=f'attachment://{user_name}_battle.png')
					self.based_turn_descript = Desc_Holder.replace(f"{nl.join(self.battle_current_mssage[-5:])}", "<Battle Message>")
					return await interaction.edit_original_message(attachments=[Send_Image], embed=Embed, view=self)

				return await interaction.followup.send(content="Please Select Another PC To Do The Action.", ephemeral=True)

			@ui.button(label="OUT", style=discord.ButtonStyle.red)
			async def surrender_button(self, interaction, button: ui.Button):
				interid = interaction.user.id

				if interid != user_id:
					await interaction.response.defer()
					await interaction.followup.send(
						content=f'Sorry, this menu is controlled by {user.name}!',
						ephemeral=True
					)
					return interid == user_id

				await interaction.response.defer()

				# Penalty of surrender
				check = cursor.find_one({"id":user_id})

				check["SJ-DATA"]["RANK_DATA"]["P_RANK"] -= 100
				check["N_economy_Data"]["Money"] -= 2000

				if check["SJ-DATA"]["RANK_DATA"]["P_RANK"] <= 0:
					check["SJ-DATA"]["RANK_DATA"]["P_RANK"] = 0
				if check["N_economy_Data"]["Money"] <= 0:
					check["N_economy_Data"]["Money"] = 0

				cursor.update_many({"id":user_id}, {"$set":{
					"N_economy_Data":check["N_economy_Data"],
					"SJ-DATA":check["SJ-DATA"]
				}})

				Embed = discord.Embed(
					title=f"{user_name} | Battle Lose!",
					description=(
						f"> ```{nl}"
						f"> {user_name} surrendered the match at turn 0,{nl}"
						f"> causing a drop in points and penalty was given!```{nl}"
						f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯{nl}"
						f"```diff{nl}"
						f"+ Damage Dealt  : {self.damage_total} {nl}"
						f"- Damage Taken  : {self.damaged_total} {nl}"
						f"+ Dodge Counter : {self.dodge_total} {nl}"
						f"+ Turn Total    : {self.current_turn} {nl}"
						f"```{nl}"
						f"```cs{nl}"
						f"Rank Point      : -100{nl}"
						f"Battle Cooldown : +100s{nl}"
						f"Money           : -2000 CyberMoney{nl}"
						f"```"
					),
					color=color
				)

				for items in self.children:
					items.disabled = True
				return await interaction.edit_original_message(embed=Embed, view=self)

			@ui.button(label="END TURN", style=discord.ButtonStyle.blurple, custom_id="END_TURN_END_BATTLE")
			async def end_turn_button(self, interaction, button:ui.Button):
				interid = interaction.user.id

				if interid != user_id:
					await interaction.response.defer()
					await interaction.followup.send(
						content=f'Sorry, this menu is controlled by {user.name}!',
						ephemeral=True
					)
					return interid == user_id

				await interaction.response.defer()
				if self.battle_states == "WIN":
					check = cursor.find_one({"id":user_id})

					# RPG Poin Gain Division
					default_gain_point = {"Bronze": 100, "Silver": 80, "Gold": 50} # DEFAULT POINT
					default_division = {"Bronze": 1, "Silver": 2, "Gold": 3}       # DIVISION POINT
					default_win = {"Bronze":1.3, "Silver":1.1, "Gold": 0}          # WIN MULTIPLIER

					U_RANK = check["SJ-DATA"]["RANK_DATA"]["C_RANK"]
					E_RANK = ENEMY["SJ-DATA"]["RANK_DATA"]["C_RANK"]

					U_TURNS = self.current_turn

					# Gainining Normal Point
					gain_points = default_gain_point[U_RANK]
					if (default_division[U_RANK] < default_division[E_RANK]) and (U_RANK != "gold"):
					    gain_points += int(default_gain_point[U_RANK] * default_win[U_RANK])

					# Point calculation by using game turn, taken damage, dealt damage, user destroyed pc
					# and enemy destroyed pc. 
					gain_points -= self.current_turn / 2.5
					gain_points -= self.damaged_total * 0.5
					gain_points -= 20 * len(self.UComputer_Destroyed)
					    
					gain_points += self.damage_total * 0.001
					gain_points += 50 * len(self.EComputer_Destroyed)
					gain_points = int(gain_points)

					if gain_points <= 0:
						gain_points = 10

					calculation_rank = calc_rank(
						check["SJ-DATA"]["RANK_DATA"]["C_RANK"],
						check["SJ-DATA"]["RANK_DATA"]["CRNKRQ"],
						int(check["SJ-DATA"]["RANK_DATA"]["P_RANK"]+gain_points)
					)

					check["SJ-DATA"]["RANK_DATA"]["C_RANK"] = calculation_rank[0]
					check["SJ-DATA"]["RANK_DATA"]["PMRANK"] = calculation_rank[3]
					check["SJ-DATA"]["RANK_DATA"]["CRNKRQ"] = calculation_rank[2]
					check["SJ-DATA"]["RANK_DATA"]["P_RANK"] += gain_points

					Money_gain = random.randint(1000, 10000)
					check["N_economy_Data"]["Money"] += Money_gain

					cursor.update_many({"id":user_id}, {"$set":{
						"N_economy_Data":check["N_economy_Data"],
						"SJ-DATA":check["SJ-DATA"]
					}})

					Embed = discord.Embed(
						title=f"{user_name} | Battle Victory!",
						description=(
							f"```{user_name} defeated {ENEMY_NAME} and won the match!```{nl}"
							f"> ⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯{nl}"
							f"```diff{nl}"
							f"+ Damage Dealt  : {self.damage_total} {nl}"
							f"- Damage Taken  : {self.damaged_total} {nl}"
							f"+ Dodge Counter : {self.dodge_total} {nl}"
							f"+ Turn Total    : {self.current_turn} {nl}"
							f"```{nl}"
							f"```diff{nl}"
							f"- User Pc Destroyed     : {self.current_turn} {nl}"
							f"+ Enemy Pc Destroyed    : {self.current_turn} {nl}"
							f"```{nl}"
							f"> ⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯{nl}"
							f"```cs{nl}"
							f"Rank Point      : +{gain_points}/{check['SJ-DATA']['RANK_DATA']['PMRANK']}{nl}"
							f"Money           : +{Money_gain}{nl}"
							f"Component       : -{nl}"
							f"Scraps          : -{nl}"
							f"```"
						),
						color=color
					)
					for items in self.children:
						items.disabled = True
					await interaction.edit_original_message(embed=Embed,view=self)

			async def on_timeout(self):
				for items in self.children:
					items.disabled = True
				await interaction.edit_original_message(view=self)

		Send_Image = discord.File(fp=io.BytesIO(Image_Procces[0]), filename=f'{user_name}_battle.png')
		Embed = discord.Embed(
			title=f"{user_name} CyberHack Battle",
			description=(
				f"> **{user_name}'s Computer :**{nl}"
				f"{nl.join(UComp_List)}{nl}{nl}"
				f"> **{ENEMY_NAME}'s Computer :**{nl}"
				f"{nl.join(EComp_List)}{nl}{nl}"
				f"```diff{nl}<Battle Message>{nl}```"
			),
			color=color
		)
		Embed.set_footer(text=f"Executor : {user_name} | {Time}")
		Embed.set_image(url=f'attachment://{user_name}_battle.png')
		Embed.set_thumbnail(url=user_pfp)

		await interaction.followup.send(
			file=Send_Image,
			embed=Embed,
			view=Menu()
		)

async def setup(bot):
	await bot.add_cog(Rpg_Cmd(bot))