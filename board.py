import discord
import asyncio
import os
import requests
import random
import gspread_asyncio
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
    except gspread_asyncio.exceptions.APIError as e:
        print(f'find_user error: {e}')
    return cell
# 보드 게임판
board = ["START", "도쿄", "무인도", "이벤트", "4", "5", "6", "7", "8", "9", "10",
         "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
         "21", "22", "23", "24", "25"]

# 보드 게임판의 각 칸 설명
descriptions = ["시작점", "미식의 도시 도쿄! 가장 좋아하는 일본 요리를 일본어로 공유해주세요", "하루 동안 주사위를 굴릴 수 없습니다", "인벤트 버튼을 클릭하세요", "D", "E", "F", "G", "H", "I",
                "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S",
                "T", "U", "V", "W", "X", "Y", "Z"]

class DiceRollView(discord.ui.View):
    def __init__(self, sheet7, current_field, message):
        super().__init__()
        self.sheet7 = sheet7
        self.current_field = current_field
        self.message = message

    async def find_user(self, author):
        username_with_discriminator = f'{author.name}#{author.discriminator}'
        cells = await self.sheet7.findall(username_with_discriminator)
        if cells:
            return cells[0]
        else:
            return None

    async def update_board(self):
        user_cell = await self.find_user(self.message.author)
        if user_cell:
            row = user_cell.row
            if self.current_field >= 25:
                self.current_field %= 25
                laps_completed = int(await self.sheet7.acell(f'D{row}').value) + 1
                await self.sheet7.update_cell(row, 4, laps_completed)
                await self.sheet7.update_cell(row, 2, int(await self.sheet7.acell(f'B{row}').value) + 1)  # Add one dice
                await self.message.channel.send(f"Congratulations! You have completed {laps_completed} laps! You got 1 extra dice.")
            await self.sheet7.update_cell(row, 3, self.current_field)  # Update the new position in column C
            await self.sheet7.update_cell(row, 2, int(await self.sheet7.acell(f'B{row}').value) - 1)  # Decrease the dice count by 1
        else:
            print("User not found in the sheet.")

    async def roll_the_dice(self, button: discord.ui.Button, interaction: discord.Interaction):
        cell = await self.find_user(interaction.user)
        if cell:
            dice_count = int(await self.sheet7.acell(f'B{cell.row}').value)
            if dice_count > 0:
                dice_roll = random.randint(1, 6)
                self.current_field += dice_roll  # Update current position
                await interaction.response.send_message(f"You rolled a {dice_roll} and moved to {board[self.current_field % 25]}.", ephemeral=True)
                await self.update_board()
                await self.game_board_message.edit(embed=self.get_board_embed(), view=self)
            else:
                await interaction.response.send_message('There are no dice to roll.', ephemeral=True)
        else:
            await interaction.response.send_message('User not found in the sheet.', ephemeral=True)

    def get_board_embed(self):
        # Create Embed object
        embed = discord.Embed(title="Game Board", color=discord.Color.blue())

        # Add fields to the game board Embed
        for i in range(25):
            # Show current position
            if i == self.current_field % 25:
                embed.add_field(name=f":red_square: {board[i]}", value=f":arrow_right: {descriptions[i]}", inline=True)
            else:
                embed.add_field(name=board[i], value=descriptions[i], inline=True)

        return embed
      
@bot.command(name='보드')
async def world(ctx):
    sheet7, rows = await get_sheet7()
    user_cell = await find_user(ctx.author, sheet7)
    if not user_cell:
        await ctx.send("User not found in the sheet.")
        return

    current_field = int(rows[user_cell.row - 1][2])  # Get current position from sheet
    embed = discord.Embed(title="Game Board", color=discord.Color.blue())
    for i in range(25):
        # Show current position
        if i == current_field % 25:
            embed.add_field(name=f":red_square: {board[i]}", value=f":arrow_right: {descriptions[i]}", inline=True)
        else:
            embed.add_field(name=board[i], value=descriptions[i], inline=True)

    view = DiceRollView(sheet7, current_field, None)
    game_board_message = await ctx.send(embed=view.get_board_embed(), view=view)
    view.message = game_board_message
                            
bot.run(TOKEN)
