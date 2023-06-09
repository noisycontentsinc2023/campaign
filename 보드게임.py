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
