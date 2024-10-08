import discord, asyncio, aiohttp, os
import pandas as pd
from discord.ext import commands
import praw

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


# Set up the Reddit client
reddit = praw.Reddit(
    client_id='7DiD0cU_gsUE7-hCAC2fFA',
    client_secret='K-MdR75pqpLvfo_LYB1UXlE7Vq4xYg',
    user_agent='unixporn/1.0 by niyakipham'
)

# Set up the Discord bot
intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Function to scrape the latest post from r/unixporn
async def get_latest_unixporn_post():
    subreddit = reddit.subreddit('unixporn')
    latest_post = next(subreddit.new(limit=1))  # Get the newest post
    return {
        'title': latest_post.title,
        'image': latest_post.url if latest_post.url.endswith(('.jpg', '.png')) else None,
        'permalink': f"https://reddit.com{latest_post.permalink}"
    }

# Send the latest post to a specific Discord channel
@bot.command(name='fetch_unixporn')
async def fetch_unixporn(ctx):
    post = await get_latest_unixporn_post()
    if post['image']:
        embed = discord.Embed(title=post['title'], url=post['permalink'])
        embed.set_image(url=post['image'])
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"Latest post: {post['title']} \n{post['permalink']}")

# Bot ready event
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    channel = bot.get_channel(1291045191687475230)
    
    # Periodically fetch and post the latest Unixporn post every 10 minutes
    while True:
        post = await get_latest_unixporn_post()
        if post['image']:
            embed = discord.Embed(title=post['title'], url=post['permalink'])
            embed.set_image(url=post['image'])
            await channel.send(embed=embed)
        else:
            await channel.send(f"Latest post: {post['title']} \n{post['permalink']}")
        await asyncio.sleep(600)  # Wait for 10 minutes


bot.run(os.getenv('DISCORD_TOKEN'))
