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

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.mention}! bạn vui lòng sử dụng câu lệnh !hlp để được trai nghiệm bot tốt nhất có thể")

#

@bot.command()
async def hlp(ctx):
    embed = discord.Embed(
        title="Help Command",
        description="SAU ĐÂY LÀ MỘT SỐ LỆNH CỦA BOT ANIME:",
        color=discord.Color.blue()
    )
    embed.add_field(name="!hlp", value="Gợi ý lệnh", inline=False)
    embed.add_field(name="!anime", value="Tìm thông tin về một bộ anime", inline=False)
    embed.add_field(name="!img", value="Ảnh anime ngẫu nhiên", inline=False)
    embed.add_field(name="!hello", value="Chào mừng, khi bạn cần tư vấn", inline=False)
    
    await ctx.send(embed=embed)


count = 0
channel_id = 1291415595488903238

@bot.command()
async def startcount(ctx):
    global count
    count = 0  # Reset số đếm
    await ctx.send("Bắt đầu đếm! Nhập số đầu tiên.")

# Lắng nghe tin nhắn trong kênh để đếm số
@bot.event
async def on_message(message):
    global count

    if message.author.bot:  # Không phản hồi bot khác
        return

    if message.channel.id == channel_id:  # Chỉ đếm trong kênh cụ thể
        try:
            # Kiểm tra xem tin nhắn có phải là số tiếp theo không
            num = int(message.content)
            if num == count + 1:
                count += 1
                await message.channel.send(f"Đã đếm đến {count}")
            else:
                await message.channel.send(f"Số tiếp theo phải là {count + 1}!")
        except ValueError:
            await message.channel.send("Vui lòng nhập một số hợp lệ!")

    # Đừng quên gọi on_message từ lớp cha để các lệnh khác vẫn hoạt động
    await bot.process_commands(message)


#--------------------------------------------------------------

# ID kênh mặc định để gửi ảnh
WAIFU_ID = 1295014200967561328  # Thay thế bằng ID kênh của bạn
NEKO_ID = 1295014835389726783
KISS_ID  = 1295014949189582930
SHINOBU = 1295019163076530319
# Danh sách các loại ảnh (sfw)
awaifu = ["waifu"]
aneko = ["neko"]
akis = ["kiss"]
ashinobu = ["shinobu"]




@tasks.loop(seconds=20)
async def send_waifu_image():
    try:
        # Chọn ngẫu nhiên một loại ảnh
        category = random.choice(ashinobu)
        
        # Gọi API để lấy URL ảnh
        response = requests.get(f"https://api.waifu.pics/sfw/{category}")
        response.raise_for_status() # Kiểm tra lỗi HTTP
        image_url = response.json()["url"]

        # Lấy kênh mặc định
        aashinobu = bot.get_channel(SHINOBU)
        if aashinobu is None:
            print(f"Không tìm thấy kênh có ID {SHINOBU}")
            return
        
        # Gửi ảnh
        await aashinobu.send(image_url)

    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi API: {e}")
    except Exception as e:
        print(f"Lỗi khác: {e}")


@tasks.loop(seconds=20)
async def send_waifu_image():
    try:
        # Chọn ngẫu nhiên một loại ảnh
        category = random.choice(akis)
        
        # Gọi API để lấy URL ảnh
        response = requests.get(f"https://api.waifu.pics/sfw/{category}")
        response.raise_for_status() # Kiểm tra lỗi HTTP
        image_url = response.json()["url"]

        # Lấy kênh mặc định
        aakis = bot.get_channel(KISS_ID)
        if aakis is None:
            print(f"Không tìm thấy kênh có ID {KISS_ID}")
            return
        
        # Gửi ảnh
        await aakis.send(image_url)

    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi API: {e}")
    except Exception as e:
        print(f"Lỗi khác: {e}")

#-----------------------------------
@tasks.loop(seconds=20)
async def send_waifu_image():
    try:
        # Chọn ngẫu nhiên một loại ảnh
        category = random.choice(aneko)
        
        # Gọi API để lấy URL ảnh
        response = requests.get(f"https://api.waifu.pics/sfw/{category}")
        response.raise_for_status() # Kiểm tra lỗi HTTP
        image_url = response.json()["url"]

        # Lấy kênh mặc định
        aaneko = bot.get_channel(NEKO_ID)
        if aaneko is None:
            print(f"Không tìm thấy kênh có ID {NEKO_ID}")
            return
        
        # Gửi ảnh
        await aaneko.send(image_url)

    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi API: {e}")
    except Exception as e:
        print(f"Lỗi khác: {e}")

#-----------------------------------
@tasks.loop(seconds=20)
async def send_waifu_image():
    try:
        # Chọn ngẫu nhiên một loại ảnh
        category = random.choice(awaifu)
        
        # Gọi API để lấy URL ảnh
        response = requests.get(f"https://api.waifu.pics/sfw/{category}")
        response.raise_for_status() # Kiểm tra lỗi HTTP
        image_url = response.json()["url"]

        # Lấy kênh mặc định
        aawaifu = bot.get_channel(WAIFU_ID)
        if aawaifu is None:
            print(f"Không tìm thấy kênh có ID {WAIFU_ID}")
            return
        
        # Gửi ảnh
        await aawaifu.send(image_url)

    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi API: {e}")
    except Exception as e:
        print(f"Lỗi khác: {e}")

@bot.event
async def on_ready():
    print(f"{bot.user} đã kết nối!")
    send_waifu_image.start() # Bắt đầu task

bot.run(os.getenv('DISCORD_TOKEN'))
