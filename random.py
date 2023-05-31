import discord
import bs4
import asyncio
import os
import urllib
import requests
import openai
import datetime
import random
import json
import json.decoder
import gspread.exceptions
import re
import pytz
import gspread_asyncio
import asyncio
import discord.ui as ui
import time

from google.oauth2.service_account import Credentials
from datetime import date, timedelta
from datetime import datetime
from discord import Embed
from discord import Interaction
from discord.ext import tasks, commands
from discord.ext.commands import Context
from discord.utils import get
from urllib.request import Request
from discord.ui import Select, Button, View

TOKEN = os.environ['TOKEN']
PREFIX = os.environ['PREFIX']


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.typing = False
intents.presences = False


bot = commands.Bot(command_prefix=PREFIX, intents=intents)

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
#------------------------------------------------#
# 스프레드 시트 지정
async def get_sheet3(): 
    client_manager = gspread_asyncio.AsyncioGspreadClientManager(lambda: aio_creds)
    client = await client_manager.authorize()
    spreadsheet = await client.open('서버기록')
    sheet3 = await spreadsheet.worksheet('랜덤미션')
    rows = await sheet3.get_all_values()
    return sheet3, rows 

async def find_user(username, sheet):
    cell = None
    try:
        cells = await sheet.findall(username)
        if cells:
            cell = cells[0]
    except gspread.exceptions.APIError as e:
        print(f'find_user error: {e}')
    return cell

  
class CustomSelect(discord.ui.Select):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "등록":
            await interaction.response.send_message("'!등록' 명령어를 통해 랜덤미션스터디에 등록할 수 있습니다 예시)!등록", ephemeral=True)
        elif self.values[0] == "뽑기":
            await interaction.response.send_message("'!뽑기' 명령어를 통해 50가지 랜덤 미션 중 하나를 뽑을 수 있어요 예시)!뽑기", ephemeral=True)
        elif self.values[0] == "미션누적":
            await interaction.response.send_message("'미션누적' 명령어를 통해 랜덤미션을 몇 회 인증받았는지 확인할 수 있습니다! 6회 이상 인증 확인되면 완주자 역할을 소유하게 됩니다 예시)!미션누적", ephemeral=True)
            
@bot.command(name="")
async def one_per_day(ctx):
    await ctx.message.delete()  # 명령어 삭제
    
    embed = discord.Embed(title="랜덤미션스터디 명령어 모음집", description=f"{ctx.author.mention}님 원하시는 명령어를 아래에서 골라주세요")
    embed.set_footer(text="이 창은 1분 후 자동 삭제됩니다")

    message = await ctx.send(embed=embed, ephemeral=True)

    select = CustomSelect(
        options=[
            discord.SelectOption(label="등록", value="등록"),
            discord.SelectOption(label="뽑기", value="뽑기"),
            discord.SelectOption(label="미션누적", value="미션누적")
        ],
        placeholder="명령어를 선택하세요",
        min_values=1,
        max_values=1
    )

    select_container = discord.ui.View()
    select_container.add_item(select)

    message = await message.edit(embed=embed, view=select_container)

    await asyncio.sleep(60)  # 1분 대기
    await message.delete()  # 임베드 메시지와 셀렉트 메뉴 삭제
    
@bot.command(name='')
async def Register(ctx):
    username = str(ctx.message.author)
    
    sheet3, rows = await get_sheet3()

    # Check if the user is already registered
    registered = False
    row = 2
    while (cell_value := (await sheet3.cell(row, 1)).value):
        if cell_value == username:
            registered = True
            break
        row += 1

    if registered:
        embed = discord.Embed(description=f"{ctx.author.mention}님, 이미 등록하셨어요!", color=0xFF0000)
        await ctx.send(embed=embed)
    else:
        await sheet3.update_cell(row, 1, username)

        role = discord.utils.get(ctx.guild.roles, id=1093781563508015105)
        await ctx.author.add_roles(role)

        embed = discord.Embed(description=f"{ctx.author.mention}님, 랜덤미션스터디에 정상적으로 등록됐습니다!",
                              color=0x00FF00)
        await ctx.send(embed=embed)
    
class RandomMissionView(View):
    def __init__(self, ctx: Context, message: discord.Message):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.message = message

    @discord.ui.button(label='다시 뽑기')
    async def random_mission_button(self, button: Button, interaction: discord.Interaction):
        await self.message.delete()
        await self.ctx.invoke(self.ctx.bot.get_command('再次'))


cooldowns = {}  # 쿨다운 기록

@bot.command(name='')
async def RandomMission(ctx):
    user_id = ctx.author.id
    cooldown_time = 3600  # One hour in seconds

    # Check if the user is not in cooldowns or their cooldown has expired
    if user_id not in cooldowns or cooldowns[user_id] < time.time():
        cooldowns[user_id] = time.time() + cooldown_time

        required_role = discord.utils.get(ctx.guild.roles, id=1093781563508015105)
        allowed_channel_ids = ["1093780375890825246", "922426434633478194", "1057267651405152256"]
        if required_role in ctx.author.roles:
            if str(ctx.channel.id) in allowed_channel_ids:
                await lottery(ctx)
            else:
                await ctx.send("이 채널에서는 사용할 수 없는 명령입니다")
        else:
            embed = discord.Embed(description="랜덤미션스터디 참여자만 !미션 명령어를 사용할 수 있어요", color=0xff0000)
            await ctx.send(embed=embed)

        await asyncio.sleep(cooldown_time)  # Add a delay between command uses

    else:
        # Send the message if the user is still in cooldown
        embed = discord.Embed(description="해당 명령어는 한 시간에 한 번만 쓸 수 있어요!", color=0xff0000)
        await ctx.send(embed=embed)


async def lottery(ctx):
    choices = [('3일간 학습한 내용 요약정리하기', '★★★★★', '<#1098477575778599022>'), ('가장 어려웠던 문장 5번 써보기', '★★★', '<#1098477575778599022>'),
               ('가장 어려웠던 문장 4번 써보기', '★★', '<#1098477575778599022>'),
               ('가장 어려웠던 문장 3번 써보기', '★★', '<#1098477575778599022>'), ('가장 어려웠던 문장 2번 써보기', '★', '<#1098477575778599022>'), ('가장 어려웠던 문장 1번 써보기', '★', '<#1098477575778599022>'), ('조용한 독서실에서 30분 학습하기', '★★★', '<#1014721717320560713>'), ('고독한 외국어방에 한 문장 남기기', '★', '<#1014721717320560713>'),
               ('고독한 외국어방에 국가 이모지 입력해서 번역기능 사용해보기', '★', '<#1088639136048619580>'), ('조용한 독서실에서 15분 학습하기', '★', '<#1014721717320560713>'), ('자유게시판 아무 게시판에 가서 댓글 남기기', '★', '<#1056759327668588625>'), 
               ('나만의 학습노트 공유하기 ', '★★★★★', '<#1098477575778599022>'), ('수다챗에 한마디 남기기', '★', '<#922501708175769640>'), ('!운세 입력해서 올해의 외국어 운세보기', '★', '<#1098477575778599022>'), ('학습중인 언어권 노래 하나 추천하기', '★★', '<#1098477575778599022>'), 
               ('학습하는 언어권 문화 한 개 찾아서 공유하기', '★', '<#1098477575778599022>'), ('오늘은 통과!', '★', '없음!'), ('오운완 인증 글 올리기', '★★★★★', '<#1034639972503928863>'), ('올해 외국어 학습목표 써보기', '★', '<#1098477575778599022>'), ('내 책상 위 물건 중 하나 외국어로 적어보기', '★★', '<#1098477575778599022>'),
               ('본인이 가장 좋아하는 영화 제목 학습하는 언어버전으로 적어보기', '★★★', '<#1098477575778599022>'), ('일취월장에 오늘 학습내용 인증하기', '★★★', '<#1098477575778599022>'), ('조용한 독서실에서 15분 학습하기', '★', '<#1014721717320560713>'), ('이번주 학습목표 써보기', '★', '<#1098477575778599022>'), 
               ('학습하는 언어권 명언 찾아서 공유하기', '★★', '<#1098477575778599022>'), ('축! 커피 교환권 당첨! 일대일문의를 통해 글 남겨주세요!', '♥♥♥', '<#1057131667250237460>'), ('출석부에 출석체크 완료하기', '★', '<#1064847315350855730>'), 
               ('좋아하는 단어 본인이 학습하는 언어로  두 개 쓰기', '★', '<#1098477575778599022>'), ('좋아하는 단어 본인이 학습하는 언어로 한 개 쓰기', '★', '<#1098477575778599022>'), ('내 가방 속 물건 중 한 개 학습하는 언어로 써서 공유하기', '★★', '<#1098477575778599022>'), ('보이는 독서실에서 쫓겨나보기', '★', '<#1014721859188699216>'), ('내가 학습중인 언어로 자기소개 작성해서 공유하기', '★★★★', '<#1098477575778599022>'), 
               ('!MBTI 명령어를 입력해서 외국어 MBTI 보기', '★', '<#1098477575778599022>'), ('조용한 독서실에서 60분 학습하기', '★★★★★', '<#1014721717320560713>'), ('학습하는 언어권 명언 찾아서 필사 후 사진 찍어 공유하기', '★★★', '<#1098477575778599022>'), ('외우기 힘들었던 단어 한 개 써보기', '★', '<#1098477575778599022>'),
               ('외우기 힘들었던 단어 두 개 써보기', '★★', '<#1098477575778599022>'), ('외우기 힘들었던 단어 세 개 써보기', '★★★', '<#1098477575778599022>'), ('좋아하는 브랜드 명 본인이 학습하는 언어로 한 번 써보기', '★★', '<#1098477575778599022>'), ('!메뉴추천 써보기', '★', '<#1098477575778599022>'), ('다른 학습자의 랜덤미션 인증버튼 눌러주기', '★', '<#1098477575778599022>'), 
               ('학습하는 언어권 노래 듣고 아는 단어 찾아서 공유하기', '★★★★', '<#1098477575778599022>'), ('가장 좋아하는 외국어 문장 한 번 써보기', '★', '<#1098477575778599022>'), ('가장 좋아하는 외국어 문장 세 번 써보기', '★★★', '<#1098477575778599022>'), ('!역할 입력해서 내가 가진 역할 확인해보기', '★', '<#1098477575778599022>'), 
               ('학습중인 언어로 세 줄 일기 써서 공유하기', '★★★★', '<#1098477575778599022>'), ('!공부 입력해보기', '★', '<#1098477575778599022>'), ('일취월장 채널의 다른 학습자 인증에 격려 댓글 남겨주기', '★★★★', '<#978952156617007114>'),
               ('일취월장 채널의 다른 학습자 인증을 보고 격려 메시지 작성하기', '★★', '<#1098477575778599022>'), ('꼭 가보고 싶은 도시 학습하는 언어로 적어보기', '★', '<#1098477575778599022>'), ('조용한 독서실에서 한 시간 이상 참여 후 커피 교환하기! 이미 받으신 분도 가능! 참여 방법이 궁금하시다면 물어봐 주세요!', '★', '<#1014721717320560713>')]

    embed = discord.Embed(description=f'{ctx.author.mention}님의 미션을 뽑는 중입니다', color=0xff0000)
    message = await ctx.send(embed=embed)
    message_id = message.id
    selected_choices = random.sample(choices, 10)

    for i, (choice, difficulty, location) in enumerate(selected_choices):
        embed.clear_fields()
        embed.add_field(name=f'미션', value=choice, inline=True)
        embed.add_field(name='난이도', value=difficulty, inline=True)
        embed.add_field(name='미션수행장소', value=location, inline=True)
        await message.edit(embed=embed)
        await asyncio.sleep(0.5)

    result, difficulty, location = random.choice(selected_choices)
    embed.description = f"{ctx.author.mention}님의 오늘의 미션입니다!"
    embed.clear_fields()
    embed.add_field(name='오늘의 미션', value=result, inline=False)
    embed.add_field(name='난이도', value=difficulty, inline=False)
    embed.add_field(name='미션수행장소', value=location, inline=False)
    embed.set_footer(text='한 번 더 뽑아보시겠어요?')

    view = RandomMissionView(ctx, message)
    message = await message.edit(embed=embed, view=view)

@bot.command(name='再次')
async def Relottery(ctx):
    choices = [('3일간 학습한 내용 요약정리하기', '★★★★★', '<#1098477575778599022>'), ('가장 어려웠던 문장 5번 써보기', '★★★', '<#1098477575778599022>'),
               ('가장 어려웠던 문장 4번 써보기', '★★', '<#1098477575778599022>'),
               ('가장 어려웠던 문장 3번 써보기', '★★', '<#1098477575778599022>'), ('가장 어려웠던 문장 2번 써보기', '★', '<#1098477575778599022>'), ('가장 어려웠던 문장 1번 써보기', '★', '<#1098477575778599022>'), ('조용한 독서실에서 30분 학습하기', '★★★', '<#1014721717320560713>'), ('고독한 외국어방에 한 문장 남기기', '★', '<#1014721717320560713>'),
               ('고독한 외국어방에 국가 이모지 입력해서 번역기능 사용해보기', '★', '<#1088639136048619580>'), ('조용한 독서실에서 15분 학습하기', '★', '<#1014721717320560713>'), ('자유게시판 아무 게시판에 가서 댓글 남기기', '★', '<#1056759327668588625>'), 
               ('나만의 학습노트 공유하기 ', '★★★★★', '<#1098477575778599022>'), ('수다챗에 한마디 남기기', '★', '<#922501708175769640>'), ('!운세 입력해서 올해의 외국어 운세보기', '★', '<#1098477575778599022>'), ('학습중인 언어권 노래 하나 추천하기', '★★', '<#1098477575778599022>'), 
               ('학습하는 언어권 문화 한 개 찾아서 공유하기', '★', '<#1098477575778599022>'), ('오늘은 통과!', '★', '없음!'), ('오운완 인증 글 올리기', '★★★★★', '<#1034639972503928863>'), ('올해 외국어 학습목표 써보기', '★', '<#1098477575778599022>'), ('내 책상 위 물건 중 하나 외국어로 적어보기', '★★', '<#1098477575778599022>'),
               ('본인이 가장 좋아하는 영화 제목 학습하는 언어버전으로 적어보기', '★★★', '<#1098477575778599022>'), ('일취월장에 오늘 학습내용 인증하기', '★★★', '<#1098477575778599022>'), ('조용한 독서실에서 15분 학습하기', '★', '<#1014721717320560713>'), ('이번주 학습목표 써보기', '★', '<#1098477575778599022>'), 
               ('학습하는 언어권 명언 찾아서 공유하기', '★★', '<#1098477575778599022>'), ('축! 커피 교환권 당첨! 일대일문의를 통해 글 남겨주세요!', '♥♥♥', '<#1057131667250237460>'), ('출석부에 출석체크 완료하기', '★', '<#1064847315350855730>'), 
               ('좋아하는 단어 본인이 학습하는 언어로  두 개 쓰기', '★', '<#1098477575778599022>'), ('좋아하는 단어 본인이 학습하는 언어로 한 개 쓰기', '★', '<#1098477575778599022>'), ('내 가방 속 물건 중 한 개 학습하는 언어로 써서 공유하기', '★★', '<#1098477575778599022>'), ('보이는 독서실에서 쫓겨나보기', '★', '<#1014721859188699216>'), ('내가 학습중인 언어로 자기소개 작성해서 공유하기', '★★★★', '<#1098477575778599022>'), 
               ('!MBTI 명령어를 입력해서 외국어 MBTI 보기', '★', '<#1098477575778599022>'), ('조용한 독서실에서 60분 학습하기', '★★★★★', '<#1014721717320560713>'), ('학습하는 언어권 명언 찾아서 필사 후 사진 찍어 공유하기', '★★★', '<#1098477575778599022>'), ('외우기 힘들었던 단어 한 개 써보기', '★', '<#1098477575778599022>'),
               ('외우기 힘들었던 단어 두 개 써보기', '★★', '<#1098477575778599022>'), ('외우기 힘들었던 단어 세 개 써보기', '★★★', '<#1098477575778599022>'), ('좋아하는 브랜드 명 본인이 학습하는 언어로 한 번 써보기', '★★', '<#1098477575778599022>'), ('!메뉴추천 써보기', '★', '<#1098477575778599022>'), ('다른 학습자의 랜덤미션 인증버튼 눌러주기', '★', '<#1098477575778599022>'), 
               ('학습하는 언어권 노래 듣고 아는 단어 찾아서 공유하기', '★★★★', '<#1098477575778599022>'), ('가장 좋아하는 외국어 문장 한 번 써보기', '★', '<#1098477575778599022>'), ('가장 좋아하는 외국어 문장 세 번 써보기', '★★★', '<#1098477575778599022>'), ('!역할 입력해서 내가 가진 역할 확인해보기', '★', '<#1098477575778599022>'), 
               ('학습중인 언어로 세 줄 일기 써서 공유하기', '★★★★', '<#1098477575778599022>'), ('!공부 입력해보기', '★', '<#1098477575778599022>'), ('일취월장 채널의 다른 학습자 인증에 격려 댓글 남겨주기', '★★★★', '<#978952156617007114>'),
               ('일취월장 채널의 다른 학습자 인증을 보고 격려 메시지 작성하기', '★★', '<#1098477575778599022>'), ('꼭 가보고 싶은 도시 학습하는 언어로 적어보기', '★', '<#1098477575778599022>'), ('조용한 독서실에서 한 시간 이상 참여 후 커피 교환하기! 이미 받으신 분도 가능! 참여 방법이 궁금하시다면 물어봐 주세요!', '★', '<#1014721717320560713>')]

    embed = discord.Embed(description=f'{ctx.author.mention}님의 미션을 다시 뽑는 중입니다', color=0xff0000)
    message = await ctx.send(embed=embed)
    message_id = message.id
    selected_choices = random.sample(choices, 10)

    for i, (choice, difficulty, location) in enumerate(selected_choices):
        embed.clear_fields()
        embed.add_field(name=f'미션', value=choice, inline=True)
        embed.add_field(name='난이도', value=difficulty, inline=True)
        embed.add_field(name='미션수행장소', value=location, inline=True)
        await message.edit(embed=embed)
        await asyncio.sleep(0.5)

    result, difficulty, location = random.choice(selected_choices)
    embed.description = f"{ctx.author.mention}님의 오늘의 미션입니다!"
    embed.clear_fields()
    embed.add_field(name='오늘의 임무', value=result, inline=False)
    embed.add_field(name='난이도', value=difficulty, inline=False)
    embed.add_field(name='미션수행장소', value=location, inline=False)
    message = await message.edit(embed=embed)

kst = pytz.timezone('Asia/Seoul')
now = datetime.now(kst).replace(tzinfo=None)
today1 = now.strftime('%m%d')     
    
@bot.command(name='')
async def random_mission_auth(ctx):
    sheet3, rows = await get_sheet3()  # get_sheet3 호출 결과값 받기
    username = str(ctx.message.author)

    now = datetime.now(kst).replace(tzinfo=None)  # 날짜 업데이트 코드 수정
    today1 = now.strftime('%m%d')

    user_row = None
    for row in await sheet3.get_all_values():
        if username in row:
            user_row = row
            break

    if user_row is None:
        embed = discord.Embed(title='Error', description='스라밸-랜덤미션스터디에 등록된 멤버가 아닙니다')
        await ctx.send(embed=embed)
        return

    user_cell = await find_user(username, sheet3)

    if user_cell is None:
        embed = discord.Embed(title='Error', description='스라밸-랜덤미션스터디에 등록된 멤버가 아닙니다')
        await ctx.send(embed=embed)
        return

    today1_col = None
    for i, col in enumerate(await sheet3.row_values(1)):
        if today1 in col:
            today1_col = i + 1
            break

    if today1_col is None:
        embed = discord.Embed(title='Error', description='랜덤미션스터디 기간이 아닙니다')
        await ctx.send(embed=embed)
        return

    if (await sheet3.cell(user_cell.row, today1_col)).value == '1':
        embed = discord.Embed(title='Error', description='이미 오늘의 미션 인증을 하셨습니다')
        await ctx.send(embed=embed)
        return
      
    # create and send the message with the button
    embed = discord.Embed(title="미션 인증", description=f' 버튼을 눌러 {ctx.author.mention}님의 미션을 인증해주세요')
    button = AuthButton2(ctx, username, today1, sheet3)
    view = discord.ui.View()
    view.add_item(button)
    await update_embed_auth(ctx, username, today1, sheet3)
        
class AuthButton2(discord.ui.Button):
    def __init__(self, ctx, username, today1, sheet3):
        super().__init__(style=discord.ButtonStyle.green, label="미션인증")
        self.ctx = ctx
        self.username = username
        self.sheet3 = sheet3
        self.auth_event = asyncio.Event()
        self.stop_loop = False
        self.today1 = today1  # 인스턴스 변수로 today1 저장

    async def callback(self, interaction: discord.Interaction):
        if interaction.user == self.ctx.author:
            # If the user is the button creator, send an error message
            embed = discord.Embed(title='Error', description='자신이 생성한 버튼은 사용할 수 없습니다 :(')
            await interaction.response.edit_message(embed=embed, view=None)
            return

        try:
            user_cell = await find_user(self.username, self.sheet3)
            if user_cell is None:
                embed = discord.Embed(title='Error', description='스라밸-랜덤미션스터디에 등록된 멤버가 아닙니다')
                await interaction.response.edit_message(embed=embed, view=None)
                return
            user_row = user_cell.row
        except gspread.exceptions.CellNotFound:
            embed = discord.Embed(title='Error', description='스라밸-랜덤미션스터디에 등록된 멤버가 아닙니다')
            await interaction.response.edit_message(embed=embed, view=None)
            return

        now = datetime.now(kst).replace(tzinfo=None)  # 날짜 업데이트 코드 수정
        self.today = now.strftime('%m%d')

        # Authenticate the user in the spreadsheet
        today1_col = (await self.sheet3.find(self.today)).col
        await self.sheet3.update_cell(user_row, today1_col, '1')

        # Set the auth_event to stop the loop
        self.auth_event.set()

        # Remove the button from the view
        self.view.clear_items()

        # Send a success message
        await interaction.message.edit(embed=discord.Embed(title="인증완료!", description=f"{interaction.user.mention}님이 {self.ctx.author.mention}의 랜덤미션을 인증했습니다🥳"), view=None)
        self.stop_loop = True

async def update_embed_auth(ctx, username, today1, sheet3):
    embed = discord.Embed(title="미션 인증", description=f' 버튼을 눌러 {ctx.author.mention}님의 미션을 인증해주세요')
    button = AuthButton2(ctx, username, today1, sheet3)
    view = discord.ui.View(timeout=None)
    view.add_item(button)
    message = await ctx.send(embed=embed, view=view)

    while not button.stop_loop:
        await asyncio.sleep(60)
        now = datetime.now(kst).replace(tzinfo=None)  # 날짜 업데이트 코드 수정
        today1 = now.strftime('%m%d')
        if not button.stop_loop:
            view = discord.ui.View(timeout=None)
            button = AuthButton2(ctx, username, sheet3)
            view.add_item(button)
            await message.edit(embed=embed, view=view)

    view.clear_items()
    await message.edit(view=view)
            
@bot.command(name='')
async def mission_count(ctx):
    username = str(ctx.message.author)
    sheet3, rows = await get_sheet3()
    
    user_row = None
    for row in await sheet3.get_all_values():
        if username in row:
            user_row = row
            break

    if user_row is None:
        embed = discord.Embed(title='Error', description='스라밸-랜덤미션스터디에 등록된 멤버가 아닙니다')
        await ctx.send(embed=embed)
        return

    user_cell = await sheet3.find(username)
    count = int((await sheet3.cell(user_cell.row, 9)).value)  # 해당 username의 I행을 불러옴

    embed = discord.Embed(description=f"{ctx.author.mention}님은 {count} 회 인증하셨어요!", color=0x00FF00)
    await ctx.send(embed=embed)

    # 참여자가 총 7일 중 6회이상 인증하면
    if count in [6, 7]:
        role = discord.utils.get(ctx.guild.roles, id=1093831438475989033)
        await ctx.author.add_roles(role)
        embed = discord.Embed(description="완주를 축하드립니다! 완주자 롤을 받으셨어요!", color=0x00FF00)
        await ctx.send(embed=embed)
        
#------------------------------------------------#
