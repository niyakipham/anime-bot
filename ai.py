import discord, aiohttp, os
import pandas as pd
from discord.ext import commands, tasks
import google.generativeai as genai
import requests
import asyncio
import random
anime_data = pd.read_csv('anime.csv')

intents = discord.Intents.default()
intents.message_content = True 

# Create a bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Command: Fetch anime information by name
@bot.command()
async def anime(ctx, *, anime_name: str):
    # Search for the anime in the dataframe
    result = anime_data[anime_data['name'].str.contains(anime_name, case=False, na=False)]
    
    if result.empty:
        await ctx.send("Anime not found.")
    else:
        for index, row in result.iterrows():
            # Send anime information
            await ctx.send(f"**{row['name']}**\n"
                           f"Thể Loại: {row['genre']}\n"
                           f"Kiểu: {row['type']}\n"
                           f"Số Tập: {row['episodes']}\n"
                           f"Đánh Giá: {row['rating']}\n"
                           f"Lượt Xem: {row['members']}\n"
                           f"-----------")

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

xwa = 'https://api.waifu.pics/nsfw/waifu'
xne = 'https://api.waifu.pics/nsfw/neko'
xtr = 'https://api.waifu.pics/nsfw/trap'
xblo = 'https://api.waifu.pics/nsfw/blowjob'

@bot.command()
async def xwaifu(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get(xwa) as response:
            if response.status == 200:
                data = await response.json()
                image_url = data["url"]
                # Send the image to Discord
                embed = discord.Embed(title="Here is your random anime image!")
                embed.set_image(url=image_url)
                await ctx.send(embed=embed)
            else:
                await ctx.send("Couldn't fetch an anime image at the moment, try again later!")

@bot.command()
async def xneko(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get(xne) as response:
            if response.status == 200:
                data = await response.json()
                image_url = data["url"]
                # Send the image to Discord
                embed = discord.Embed(title="Here is your random anime image!")
                embed.set_image(url=image_url)
                await ctx.send(embed=embed)
            else:
                await ctx.send("Couldn't fetch an anime image at the moment, try again later!")

@bot.command()
async def xtrap(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get(xtr) as response:
            if response.status == 200:
                data = await response.json()
                image_url = data["url"]
                # Send the image to Discord
                embed = discord.Embed(title="Here is your random anime image!")
                embed.set_image(url=image_url)
                await ctx.send(embed=embed)
            else:
                await ctx.send("Couldn't fetch an anime image at the moment, try again later!")

@bot.command()
async def xgif(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get(xblo) as response:
            if response.status == 200:
                data = await response.json()
                image_url = data["url"]
                # Send the image to Discord
                embed = discord.Embed(title="Here is your random anime image!")
                embed.set_image(url=image_url)
                await ctx.send(embed=embed)
            else:
                await ctx.send("Couldn't fetch an anime image at the moment, try again later!")

#-----------------------------------------------------------------------------------

awa = 'https://api.waifu.pics/sfw/waifu'
ane = 'https://api.waifu.pics/sfw/neko'
aki = 'https://api.waifu.pics/sfw/kiss'
acud = 'https://api.waifu.pics/sfw/cuddle'
apa = 'https://api.waifu.pics/sfw/pat'

@bot.command()
async def apat(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get(apa) as response:
            if response.status == 200:
                data = await response.json()
                image_url = data["url"]
                # Send the image to Discord
                embed = discord.Embed(title="Ngoan Ngoan ^^")
                embed.set_image(url=image_url)
                await ctx.send(embed=embed)
            else:
                await ctx.send("Couldn't fetch an anime image at the moment, try again later!")

@bot.command()
async def acuddle(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get(acud) as response:
            if response.status == 200:
                data = await response.json()
                image_url = data["url"]
                # Send the image to Discord
                embed = discord.Embed(title="Ngoan Ngoan ^^")
                embed.set_image(url=image_url)
                await ctx.send(embed=embed)
            else:
                await ctx.send("Couldn't fetch an anime image at the moment, try again later!")

@bot.command()
async def awaifu(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get(awa) as response:
            if response.status == 200:
                data = await response.json()
                image_url = data["url"]
                # Send the image to Discord
                embed = discord.Embed(title="Here is your random anime image!")
                embed.set_image(url=image_url)
                await ctx.send(embed=embed)
            else:
                await ctx.send("Couldn't fetch an anime image at the moment, try again later!")

@bot.command()
async def akis(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get(aki) as response:
            if response.status == 200:
                data = await response.json()
                image_url = data["url"]
                # Send the image to Discord
                embed = discord.Embed(title="@_@ mlem mlem")
                embed.set_image(url=image_url)
                await ctx.send(embed=embed)
            else:
                await ctx.send("Couldn't fetch an anime image at the moment, try again later!")

@bot.command()
async def aneko(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get(ane) as response:
            if response.status == 200:
                data = await response.json()
                image_url = data["url"]
                # Send the image to Discord
                embed = discord.Embed(title="Here is your random anime image!")
                embed.set_image(url=image_url)
                await ctx.send(embed=embed)
            else:
                await ctx.send("Couldn't fetch an anime image at the moment, try again later!")



#--------------------------------------------------------------

CHANNEL_ID = 1295014200967561328

sfw_categories = ["waifu", "neko", "shinobu", "megumin", "bully", "cuddle", "cry", "hug", "awoo", "kiss", "lick", "pat", "smug", "bonk", "yeet", "blush", "smile", "wave", "highfive", "handhold", "nom", "bite", "glomp", "slap", "kill", "kick", "happy", "wink", "poke", "dance", "cringe"]

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@tasks.loop(seconds=20)
async def send_waifu_image():
    try:
        # Chọn ngẫu nhiên một loại ảnh
        category = random.choice(sfw_categories)
        
        # Gọi API để lấy URL ảnh
        response = requests.get(f"https://api.waifu.pics/sfw/{category}")
        response.raise_for_status() # Kiểm tra lỗi HTTP
        image_url = response.json()["url"]

        # Lấy kênh mặc định
        channel = bot.get_channel(CHANNEL_ID)
        if channel is None:
            print(f"Không tìm thấy kênh có ID {CHANNEL_ID}")
            return
        
        # Gửi ảnh
        await channel.send(image_url)

    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi API: {e}")
    except Exception as e:
        print(f"Lỗi khác: {e}")


@bot.event
async def on_ready():
    print(f"{bot.user} đã kết nối!")
    send_waifu_image.start() # Bắt đầu task

bot.run(os.getenv('DISCORD_TOKEN'))
