import discord, asyncio, aiohttp
import pandas as pd
from discord.ext import commands

# Load the CSV data
anime_data = pd.read_csv('anime.csv')

intents = discord.Intents.default()
intents.message_content = True 

# Create a bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

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

# OPENAI_API_KEY = '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'

# Biến toàn cục để theo dõi trạng thái trò chơi
is_game_active = False
last_word = ""
players = []


@bot.event
async def on_ready():
    print(f'{bot.user} đã sẵn sàng!')


@bot.command()
async def startnoitu(ctx):
    global is_game_active, last_word, players

    if is_game_active:
        await ctx.send("Trò chơi đã đang diễn ra! Hãy tiếp tục chơi.")
    else:
        is_game_active = True
        last_word = ""
        players = []
        await ctx.send("Trò chơi nối từ đã bắt đầu! Người chơi đầu tiên hãy nói cụm từ của mình.")


@bot.command()
async def endnoitu(ctx):
    global is_game_active

    if is_game_active:
        is_game_active = False
        await ctx.send(f"Trò chơi đã kết thúc! Cảm ơn {ctx.author.mention} đã tham gia.")
    else:
        await ctx.send("Hiện tại không có trò chơi nào đang diễn ra.")


@bot.event
async def on_message(message):
    global is_game_active, last_word, players

    # Bỏ qua tin nhắn của chính bot và các lệnh
    if message.author == bot.user:
        return

    if message.content.startswith("!") or not is_game_active:
        await bot.process_commands(message)  # Để xử lý lệnh start, end
        return

    if is_game_active:
        current_phrase = message.content.strip().lower()

        # Nếu đây là lượt đầu tiên của trò chơi
        if not last_word:
            last_word = current_phrase.split()[-1]  # Lấy từ cuối của cụm từ đầu tiên
            players.append(message.author)  # Thêm người chơi vào danh sách
            await message.channel.send(f"{message.author.mention} đã bắt đầu với từ: {current_phrase}")
        else:
            # Kiểm tra nếu từ đầu của cụm từ mới khớp với từ cuối của cụm từ trước
            if current_phrase.split()[0] == last_word:
                last_word = current_phrase.split()[-1]  # Cập nhật từ cuối mới
                if message.author not in players:
                    players.append(message.author)  # Thêm người chơi mới vào danh sách
                await message.channel.send(f"{message.author.mention} đã nối từ thành công! Từ tiếp theo bắt đầu bằng: '{last_word}'")
            else:
                await message.channel.send(f"{message.author.mention} đã nối sai từ! Trò chơi kết thúc.")
                is_game_active = False

    await bot.process_commands(message)  # Để xử lý các lệnh khác


# Run the bot
bot.run('MTI4OTUyODk5NzA4ODA2NzYwNg.G9R7e3.dlVut9wb5CFjYInBF-YGmSRhcIss6_OnNUat28')
