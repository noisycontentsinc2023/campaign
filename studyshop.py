import discord
import asyncio
import os
import requests
import random
import gspread_asyncio
import gspread.utils
import re
import time
import pytz

from google.oauth2.service_account import Credentials
from discord import Embed
from discord import Interaction
from discord.ext import tasks
from discord.ext import commands
from discord.ext.commands import Context
from discord.ui import Select
from datetime import datetime, timedelta, date
from discord.ui import Button, View

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.typing = False
intents.presences = False

TOKEN = os.environ['TOKEN']
PREFIX = os.environ['PREFIX']

prefix = '!'
bot = commands.Bot(command_prefix=prefix, intents=intents)

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds_info = {
  "type": "service_account",
  "project_id": "thematic-bounty-382700",
  "private_key_id": "502d8dd4f035d15b57bff64ee323d544d28aedc4",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQD4Kze3Hn/yxevG\nzHUklYGSDDs8qKQeyYdd1eWaR0PNKZ2+nwKFGmXGENS6vuy3U81dqI3AVgA3w6UW\nHEaVfPvc31OX5yNCIS0eQxxqWWGJJ5+MbvUC06qXi/7hCup0WK+hoqwjHtUX7AYu\nEDgtf6xd29gSvb3YXs6pvi+2tpwPt0SED6HGPU7qPRsAaPnyUsVCj/mW04ca2iea\nxMsIqxKT6ufNssiXX7qhKyziowneM0lp8BB3k2z+/FGPQOCdi/lIscC9zKbDOIcb\nOZw+B2sd2opp7Dwo3JMIkh3NJevw9hjp0+CFeqemGNsCAiSuFkvydx6BagWaWAPs\nC48nZLNZAgMBAAECggEAF3uUbTMZQZZVoAU5CPYOMY0PfmcJR6IDeX8715BKg8N+\nOhtHBGQJ8Rbm4Ehgcxz+i/AfAK4KnXw5dvkEO1E9Lmph+Tfdg9yKjchlLBGK24z4\nqZPWwpaXl/k+7BnJs2pwbROs5PJeEOJMN+fgPvrrqyJ6RNS4Pf0Dond9AZWwOQLL\naJPFZryK7Bmvtt0H8mDDWdfqmCQTtPJ9PUyDEUeenlyhuek8wH3GHcghOSlsCDF1\nW/3YXM9Vr/arE4V6hTLwXofrUnTuXTfo+DcaOIXpHqIPS+nCyzWZ0kAJ7/uKjhnN\nF4kgv9aXDX9Y7S+3irXazRhowfu2rGuPRO/2+FCuMQKBgQD+JRDctOrKvpl9zDaw\nWT2a3qmYuFf90+b8EkKsWzVBM7neEJlw1ZWxUZzkdHXwkxcM7w93BjZeXJRnI7HZ\n5sHMrRw3p7Cwy0REqC3GSbYMCIZ/98y5Ot5sOXamUCOtYnic1NG2PBzr9h94Nt7d\nZu9D7cD/kaogm9Fl9t1VMD3REQKBgQD5+vvxY0nUkzrPEHfAOnPRqt3fM9ryzmk9\n8WyffmWqaDcvb9pl1F/+/51u00cvh2Q6etvL0J850AB0AKC9QdYzIaSj4LeRNzjA\ns+K6Po5+HAYezxC1cYzFh+slAfX3gX9pa11f3aOltj4h7IXvqBB0iH4rl/i2KQ/G\ntSDa62K9yQKBgAXXEDYiKisSijBr2u3efx3p8/fAdLUug2ZTfRi819Jxv9msg/ol\nzlTOzU4qpvMqTiNL8w0HJYSxl+9u0I1zUgzEBZv5zIOjiCQTwUmHNBm+sGiMZzXy\ndl4CTAmyWb+IPcFM2qzXYMrDUyHOEP0BeooTEpZM4J3zNrKjI57rhuAhAoGAKWDC\nE1K8BdPZCC1RpSAHy8zcrPWIaGiCQx6TPFNPwMU/XTrGi9R7j1oAVTfjsJpYnNV5\nTGNb99XWPV1dPfaH3i7TcczglcjuO/eKsAlqzLUWzkK4IVCKXKgC5D1O2Yk17d03\nt4aYb/Wak0LzaJgJIUD2oYCmSoDBe8K/jX0o+wECgYBnxk9HR/23hjWaxrSnXGDB\nHxLXg9Wz5w0N+gdC/FNxknFOft+nsCMKWMocOtGYhJU3OvkTYYqL1iDsKoMb74xG\nVwB1fuoNrNp+aJ/CzbtZVT1WLzXG41e9cu2TuOy+wpDlryfJAZ6KNVgDOmhh8TR2\nz7T0rt1QSfOZILpiwpR4jg==\n-----END PRIVATE KEY-----\n",
  "client_email": "noisycontents@thematic-bounty-382700.iam.gserviceaccount.com",
  "client_id": "107322055541690533468",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/noisycontents%40thematic-bounty-382700.iam.gserviceaccount.com"
}
credentials = Credentials.from_service_account_info(creds_info, scopes=scope)
aio_creds = credentials
  
async def get_sheet7():
    client_manager = gspread_asyncio.AsyncioGspreadClientManager(lambda: aio_creds)
    client = await client_manager.authorize()
    spreadsheet = await client.open('서버기록')
    sheet7 = await spreadsheet.worksheet('월드와이드')
    rows = await sheet7.get_all_values()
    return sheet7, rows
  
async def find_user(user, sheet7):
    cell = None
    try:
        username_with_discriminator = f'{user.name}#{user.discriminator}'
        cells = await sheet7.findall(username_with_discriminator)
        if cells:
            cell = cells[0]
    except gspread_asyncio.exceptions.APIError as e:  # Update the exception to gspread_asyncio
        print(f'find_user error: {e}')
    return cell
  
async def get_user_location(sheet, user_cell):
    row = user_cell.row
    for col in range(5, 32):  # E 부터 AE 열
        cell = await sheet.cell(row, col)
        cell_value = cell.value
        if cell_value == "1":
            return col
    return 5  # Default to column E

async def update_user_location(sheet, user_cell, steps):
    current_col = await get_user_location(sheet, user_cell)
    new_col = current_col + steps
    completed_laps = 0

    while new_col > 31:  # AE열
        completed_laps += 1  # 완주 횟수를 1 증가시킵니다.
        new_col = new_col - 27  # E열로 돌아가게 합니다.

    await sheet.update_cell(user_cell.row, current_col, "0")
    await sheet.update_cell(user_cell.row, new_col, "1")
    
    return new_col, completed_laps

class DiceRollView(View):
    def __init__(self, ctx, sheet7, message):
        super().__init__()
        self.ctx = ctx
        self.sheet7 = sheet7
        self.message = message
        self.cell = None

    async def update_message(self):
        cell = await find_user(self.ctx.author, self.sheet7)  # cell 변수 추가
        user_info_cell = await self.sheet7.acell(f'B{cell.row}')  # self.message.author.row를 cell.row로 변경
        user_location_col = await get_user_location(self.sheet7, cell)
        user_location_cell = await self.sheet7.cell(1, user_location_col)
        user_location_name = user_location_cell.value

        lap_cell = await self.sheet7.acell(f'C{cell.row}')
        completed_laps = lap_cell.value

        embed = discord.Embed(
            title="굴려서 세상속으로",
            description=f"{self.ctx.author.mention}'s game board\n남은 주사위: {user_info_cell.value}\n현재 위치: {user_location_name}\n완주 횟수: {completed_laps}",
            color=discord.Color.blue()
        )
        await self.message.delete()  # 기존 메시지 삭제
        self.message = await self.ctx.send(embed=embed, view=self)
        await self.message.delete(delay=180)  # 새 메시지 삭제

    @discord.ui.button(label='주사위 굴리기', style=discord.ButtonStyle.primary)
    async def roll_the_dice(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        if not self.cell:
            self.cell = await find_user(self.ctx.author, self.sheet7)
            
        cell = await find_user(self.ctx.author, self.sheet7)
        if cell:
            cell_value = await self.sheet7.acell(f'B{cell.row}')
            dice_count = int(cell_value.value)
            if dice_count > 0:
                dice_roll = random.randint(1, 6)
                await interaction.response.defer(ephemeral=True)
                
                new_location_col, completed_laps = await update_user_location(self.sheet7, cell, dice_roll)  # 위치 업데이트
                new_location_cell = await self.sheet7.cell(1, new_location_col)
                new_location_name = new_location_cell.value

                if completed_laps > 0:
                    lap_cell = await self.sheet7.acell(f'C{cell.row}')
                    total_laps = int(lap_cell.value) + completed_laps
                    await self.sheet7.update_cell(cell.row, 3, total_laps)
                    await interaction.followup.send(f'{interaction.user.mention}이(가) {self.ctx.author.mention}의 주사위를 굴려 {dice_roll} 가 나왔습니다! 축하합니다! 완주하셨습니다. 총 완주 횟수: {total_laps}')
                else:
                    await interaction.followup.send(f'{interaction.user.mention}이(가) {self.ctx.author.mention}의 주사위를 굴려 {dice_roll} 가 나왔습니다! {new_location_name}로 이동했습니다. 남은 주사위 횟수: {dice_count - 1}')
    
                await self.sheet7.update_cell(cell.row, 2, dice_count - 1)
                await self.update_message()  # 메시지를 갱신
            else:
                await interaction.response.send_message('남은 주사위가 없어요 :(', ephemeral=True)
        else:
            await interaction.response.send_message('등록되지 않은 멤버입니다', ephemeral=True)
            
        await mission(self.ctx)
            
@bot.command(name='보드')
async def world(ctx):
    sheet7, rows = await get_sheet7()
    user_cell = await find_user(ctx.author, sheet7)
    if not user_cell:
        await ctx.send("User not found in the sheet.")
        return

    user_info_cell = await sheet7.acell(f'B{user_cell.row}')
    user_location_col = await get_user_location(sheet7, user_cell)
    user_location_cell = await sheet7.cell(1, user_location_col)
    user_location_name = user_location_cell.value

    embed = discord.Embed(title="굴려서 세상속으로", description=f"{ctx.author.mention}'님의 \n남은 주사위: {user_info_cell.value}\n현재 위치: {user_location_name}", color=discord.Color.blue())
    message = await ctx.send(embed=embed)
    await message.delete(delay=180)  # 3분 후에 삭제
    view = DiceRollView(ctx, sheet7, message)  # 메시지를 전달
    await message.edit(embed=embed, view=view) 

#---------------------------------------------------------------------------#

async def get_sheet8():
    client_manager = gspread_asyncio.AsyncioGspreadClientManager(lambda: aio_creds)
    client = await client_manager.authorize()
    spreadsheet = await client.open('서버기록')
    sheet8 = await spreadsheet.worksheet('미니상점')
    rows = await sheet8.get_all_values()
    return sheet8, rows
  
async def update_count(sheet8, user):
    existing_users = await sheet8.col_values(1)
    try:
        if str(user) not in existing_users:
            empty_row = len(existing_users) + 1
            await sheet8.update_cell(empty_row, 1, str(user))
            await sheet8.update_cell(empty_row, 2, "1")
        else:
            index = existing_users.index(str(user)) + 1
            current_count = await sheet8.cell(index, 2)
            current_value = current_count.value if current_count.value is not None else 0
            new_count = int(current_value) + 1
            await sheet8.update_cell(index, 2, str(new_count))
        return True
    except:
        return False

class AuthButton(discord.ui.Button):
    def __init__(self, ctx, user):
        super().__init__(style=discord.ButtonStyle.green, label="확인")
        self.ctx = ctx
        self.user = user
        self.stop_loop = False
        self.handled_users = set()  # Store user IDs who have already interacted

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id in self.handled_users:
            return  # Ignore if user has already interacted

        self.handled_users.add(interaction.user.id)  # Remember user as handled

        sheet8, rows = await get_sheet8()
        
        if interaction.user == self.ctx.author:
            return
        existing_users = await sheet8.col_values(1)
        if str(self.user) not in existing_users:
            empty_row = len(existing_users) + 1
            await sheet8.update_cell(empty_row, 1, str(self.user))
            await sheet8.update_cell(empty_row, 2, "1")  # Update B column
        else:
            index = existing_users.index(str(self.user)) + 1
            count_cell = await sheet8.cell(index, 2)  # Get the cell in column B
            current_count = int(count_cell.value or "0")  # If cell is empty, treat as 0
            await sheet8.update_cell(index, 2, str(current_count + 5))  # Increment the count
        self.stop_loop = True
        success = await update_count(sheet8, interaction.user)
        if success:
            await interaction.message.edit(embed=discord.Embed(title="인증완료", description=f"{interaction.user.mention}님이 {self.ctx.author.mention}의 를 인증했습니다🥳\n {self.ctx.author.mention}님, 5 포인트가 누적됐어요!\n{interaction.user.mention}님, 1포인트가 누적됐어요!"), view=None)

class CancelButton(discord.ui.Button):
    def __init__(self, ctx):
        super().__init__(style=discord.ButtonStyle.red, label="취소")
        self.ctx = ctx
        self.stop_loop = False  # Add the stop_loop attribute
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.ctx.author.id:
            await interaction.message.delete()
            self.stop_loop = True
        else:
            await interaction.response.send_message("글 작성자만 취소할 수 있습니다", ephemeral=True)

async def update_embed(ctx, msg):
    button = AuthButton(ctx, ctx.author)  # We no longer pass 'date' here
    cancel = CancelButton(ctx)
    while True:
        try:
            if button.stop_loop or cancel.stop_loop:
                break

            view = discord.ui.View(timeout=None)
            view.add_item(button)
            view.add_item(cancel)

            embed = discord.Embed(title="인증요청", description=f"{ctx.author.mention}님의 인증입니다")  # We no longer use 'date' here
            await msg.edit(embed=embed, view=view)
            await asyncio.sleep(60)
        except discord.errors.NotFound:
            break
            
@bot.command(name='인증')
async def Authentication(ctx):

    embed = discord.Embed(title="인증요청", description=f"{ctx.author.mention}님의 인증 요청입니다")
    view = discord.ui.View()
    button = AuthButton(ctx, ctx.author)
    view.add_item(button)
    view.add_item(CancelButton(ctx))
    msg = await ctx.send(embed=embed, view=view)
    
    asyncio.create_task(update_embed(ctx, msg))

    def check(interaction: discord.Interaction):
        return interaction.message.id == msg.id and interaction.data.get("component_type") == discord.ComponentType.button.value

    await bot.wait_for("interaction", check=check)

async def update_embed_insta(ctx, msg):
    button = InstaAuthButton(ctx, ctx.author)  # We no longer pass 'date' here
    cancel = CancelButton(ctx)
    while True:
        try:
            if button.stop_loop or cancel.stop_loop:
                break

            view = discord.ui.View(timeout=None)
            view.add_item(button)
            view.add_item(cancel)

            embed = discord.Embed(title="확인요청", description=f"{ctx.author.mention}님의 sns 게시물 확인 요청입니다")  # We no longer use 'date' here
            await msg.edit(embed=embed, view=view)
            await asyncio.sleep(60)
        except discord.errors.NotFound:
            break
            
class InstaAuthButton(discord.ui.Button):
    def __init__(self, ctx, user):
        super().__init__(style=discord.ButtonStyle.green, label="확인")
        self.ctx = ctx
        self.user = user
        self.stop_loop = False
        self.handled_users = set()  # Store user IDs who have already interacted

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id in self.handled_users:
            return  # Ignore if user has already interacted

        # Make sure only an admin can interact with this button
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("관리자만 해당 버튼을 클릭할 수 있어요", ephemeral=True)
            return

        self.handled_users.add(interaction.user.id)  # Remember user as handled

        sheet8, rows = await get_sheet8()

        existing_users = await sheet8.col_values(1)
        if str(self.user) not in existing_users:
            empty_row = len(existing_users) + 1
            await sheet8.update_cell(empty_row, 1, str(self.user))
            await sheet8.update_cell(empty_row, 2, "10")  # Update B column with +10
        else:
            index = existing_users.index(str(self.user)) + 1
            count_cell = await sheet8.cell(index, 2)  # Get the cell in column B
            current_count = int(count_cell.value or "0")  # If cell is empty, treat as 0
            await sheet8.update_cell(index, 2, str(current_count + 10))  # Increment the count by 10
        self.stop_loop = True
        await interaction.message.edit(embed=discord.Embed(title="인증완료", description=f"{self.ctx.author.mention}님의 sns게시글이 정상적으로 확인되어 10 포인트가 누적됐어요!"), view=None)

@bot.command(name='인스타인증')
async def InstaAuthentication(ctx):
    embed = discord.Embed(title="확인요청", description=f"{ctx.author.mention}님의 sns 게시글 확인 요청입니다")
    view = discord.ui.View()
    button = InstaAuthButton(ctx, ctx.author)
    view.add_item(button)
    view.add_item(CancelButton(ctx))
    msg = await ctx.send(embed=embed, view=view)

    asyncio.create_task(update_embed_insta(ctx, msg))

    def check(interaction: discord.Interaction):
        return interaction.message.id == msg.id and interaction.data.get("component_type") == discord.ComponentType.button.value

    await bot.wait_for("interaction", check=check)    


items = [
    {"name": "0. 팬더단", "role_id": "1108296480399302666", "cost": 20},
    {"name": "1. 스터디플래너-영", "role_id": "1108296512015958086", "cost": 30},
    {"name": "2. 스터디플래너-일", "role_id": "1108296523323813978", "cost": 30},
    {"name": "3. 스터디플래너-스", "role_id": "1108296601526612060", "cost": 30},
    {"name": "4. 스터디플래너-프", "role_id": "1108296604923998299", "cost": 30},
    {"name": "5. 스터디플래너-중", "role_id": "1108296607088263202", "cost": 30},
    {"name": "6. 스터디플래너-독", "role_id": "1108296609390923787", "cost": 30},
    {"name": "7. 10% 쿠폰", "role_id": "1108296611114799196", "cost": 30},
    {"name": "8. VOD 한 건 무료", "role_id": "1108296777393786890", "cost": 30},
    {"name": "9. 훈트막스 액자", "role_id": "1108586104187277313", "cost": 30},
    {"name": "10. 훈트막스", "role_id": "1108296850244640769", "cost": 30},
]

1107916119957844038

@bot.command(name='상점')
async def shop(ctx):
    embed = discord.Embed(title="포인트상점에 오신걸 환영합니다!", description=f"{ctx.author.mention}님 원하시는 품목을 선택해주세요!")
    for item in items:
        embed.add_field(name=item['name'], value=f"Cost: {item['cost']}", inline=False)
    message = await ctx.send(embed=embed)
    await message.delete(delay=180)

@bot.command(name='구매')
async def buy(ctx, item_number: int):
    item = items[item_number]

    # Get user points from Google Sheets
    sheet8, _ = await get_sheet8()
    cell = await find_user(ctx.author, sheet8)
    if cell is None:
        await ctx.send("에 참여하지 않은 멤버입니다", ephemeral=True)
        return

    user_points = int((await sheet8.cell(cell.row, 2)).value)

    if user_points < item['cost']:
        await ctx.send("해당 품목을 구매하기에는 포인트가 충분하지 않아요", ephemeral=True)
        return

    # Get the role for the item
    role = discord.utils.get(ctx.guild.roles, id=int(item['role_id']))
    
    # Check if user already has this role
    if role in ctx.author.roles:
        await ctx.send("You have already purchased this item!", ephemeral=True)
        return
      
    # 구매시 기본 획득 롤
    additional_role = discord.utils.get(ctx.guild.roles, id=1107916119957844038)
    
    # Confirm purchase
    message = await ctx.send(f"{role.mention}를(을) 구매하기 위해서는 {item['cost']} 포인트가 필요합니다 . {item['cost']} 포인트를 소모해서 {role.mention}를(을) 구매하시겠어요?", ephemeral=True)
    await message.add_reaction('✅')
    await message.add_reaction('❌')

    def check(reaction, user):
        if user != ctx.author and str(reaction.emoji) in ['✅', '❌']:
            bot.loop.create_task(ctx.send(f"{user.mention}님 당사자만 해당 이모지를 클릭할 수 있어요!", ephemeral=True))
            return False
        return user == ctx.author and str(reaction.emoji) in ['✅', '❌']

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=180.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send('No response...', ephemeral=True)
    else:
        if str(reaction.emoji) == '✅':
            # Deduct points and assign role
            new_points = user_points - item['cost']
            await sheet8.update_cell(cell.row, 2, new_points)
            role = discord.utils.get(ctx.guild.roles, id=int(item['role_id']))
            await ctx.author.add_roles(role)
            await ctx.author.add_roles(additional_role)
            await ctx.send(f"구매완료! 잔여 포인트는 {new_points} 입니다", ephemeral=True)
        else:
            await ctx.send("구매가 취소되었습니다", ephemeral=True)
    
    await message.delete(delay=180)

@bot.command(name="미션")
async def mission(ctx):
    # Create a dictionary where key is a mission and value is the difficulty level
    missions = {
        "스터디미니 앱에 전체 강의 1일차 모음을 다운로드 후 학습해보고 싶은 언어 1일차 학습 후 인증하기": "★★★",
        "가장 가보고 싶은 도시와 왜 가고 싶은지 본인이 학습하는 언어로 써서 공유하기": "★★★",
        "오늘 배운 단어/문법으로 새로운 문장 세개 만들어보기": "★★",
        "본인이 학습하는 언어의 가장 큰 포털 사이트 방문해서 메인페이지 캡쳐해보기": "★★",
        "본인이 학습하는 언어로 된 트위터 / 인스타 등 sns 내용 해석해보기": "★★★",
        "ChatGPT로 간단한(10단어) 단어장 만들어 공유하기 | 예시 프롬프트 : ": "★★★★",
        "오늘 학습한 혹은 써보고 싶은 문장 세 번 써서 공유하기": "★",
        "오늘 학습한 혹은 써보고 싶은 문장  다섯 번 써서 공유하기": "★★",
        "본인이 학습하는 언어로 된 기사 한 번 읽어보고 공유하기(기사 내용이나 기사 전문)": "★★★",
        "외국어로 된 노래 가사 한 줄 번역해보기": "★★★",
        "외국어 노래 한 곡 듣고, 전체 곡 중에서 들리는 문장이나 단어 공유하기": "★★★",
        "본인이 관심있는 나라의 고유한 문화 하나 공유하기": "★★",
        "헷갈리는 단어 예문 찾아서 단어와 예문 한 번씩 써보기": "★★",
        "학습하는 언어권의 영화의 예고편을 해당언어로 듣거나 자막으로 보고 인증하기": "★★★",
        "학습하는 언어권의 유행어 한 번 알아보고 공유하기": "★★★",
        "각 나라의 유명한 디저트 찾아서 공유해보기": "★",
        "학습하는 언어권의 드라마나 영화 한 편 추천하기": "★",
        "학습하는 언어권의 노래 한 곡 추천하기 ": "★",
        "각 나라의 꼭 먹어보고 싶었던 음식 공유하기": "★",
        "학습하는 나라의 유명인 검색해보고 내용 공유하기": "★",
        "ChatGPT에 학습하는 언어와 관련된 질문 한 번 해보기": "★★",
        "본인이 학습하는 언어를 사용하는 나라의 특이한 법 하나 찾아보기 ": "★★★",
        "학습중인 언어로 세 줄 일기 써서 공유하기": "★★★",
        "학습하는 언어의 가장 마음에 드는 문장 써서 공유하기": "★",
        "오늘 해야할 일 외국어로 써서 공유하기": "★",
        "집에 있는 물건 학습하는 언어로 적어서 공유하기": "★",
        "현재 시간 혹은 오늘 날짜 외국어로 적어서 공유하기": "★",
        "학습하는 언어권 브랜드 하나 찾아 공유하기": "★",
        "가장 최근에 학습한 단어 다섯 번 써보기": "★★",
        "가장 최근에 학습한 단어 세 번 써보기": "★",
        "학습하는 언어의 드라마 혹은 영화의 명대사 공유하기": "★★",
        "학습하는 언어권의 속담 하나 알아보고 공유하기": "★★",
        "ChatGPT를 활용 본인의 실력에 맞는 간단한 대화문 만들어 보기 | 예시 프롬프트 : ": "★★★",
        "본인의 학습노트 공유하기": "★★★",
        "올해의 학습목표 학습하는 언어로 써서 공유하기": "★★",
        "오늘 학습한 내용 인증하기": "★★",
    }

    # Randomly select three missions
    # Randomly select three missions
    selected_missions = random.sample(list(missions.items()), 3)
    mission_previews = [mission[:10] + "..." for mission, difficulty in selected_missions]

    embed = discord.Embed(title="오늘의 미션을 선택해주세요", description=f"{ctx.author.mention}님 세 개의 미션 중 하나를 골라 전체 텍스트를 확인하세요!", color=discord.Color.blue())
    for idx, preview in enumerate(mission_previews, start=1):
        embed.add_field(name=f"미션 {idx}", value=preview, inline=False)

    message = await ctx.send(embed=embed, delete_after=60)

    # Add reactions to the message
    for emoji in ["1️⃣", "2️⃣", "3️⃣"]:
        await message.add_reaction(emoji)

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["1️⃣", "2️⃣", "3️⃣"]

    try:
        reaction, _ = await bot.wait_for("reaction_add", timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("1분안에 미션을 선택하지 않아 미션 선택이 종료됐습니다", delete_after=10)
    else:
        selected_mission = ""
        if str(reaction.emoji) == "1️⃣":
            selected_mission = selected_missions[0]
        elif str(reaction.emoji) == "2️⃣":
            selected_mission = selected_missions[1]
        elif str(reaction.emoji) == "3️⃣":
            selected_mission = selected_missions[2]

        # Create an embed message for the selected mission
        embed = discord.Embed(
            title="오늘의 미션",
            description=f"{ctx.author.mention}님이 선택하신 미션입니다!",
            color=discord.Color.blue()
        )
        embed.add_field(name="미션", value=selected_mission[0], inline=False)
        embed.add_field(name="난이도", value=selected_mission[1], inline=True)
        await ctx.send(embed=embed)

@bot.command(name='포인트')
async def points(ctx):
    sheet8, _ = await get_sheet8()
    cell = await find_user(ctx.author, sheet8)
    if cell is None:
        await ctx.send("공부해요 미니상점에 참여중인 멤버가 아닙니다", ephemeral=True)
        return

    user_points = (await sheet8.cell(cell.row, 2)).value
    embed = discord.Embed(title="누적 포인트", description=f"{ctx.author.mention}님의 누적 포인트는 {user_points} 입니다")
    msg = await ctx.send(embed=embed)
    await msg.delete(delay=60)
bot.run(TOKEN)
