import discord, asyncio, aiohttp, os
import pandas as pd
from discord.ext import commands
import google.generativeai as genai

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

genai.configure(api_key='AIzaSyAWfHq_eeR82EB4pdAsxYRS6HFlsAaDaeE')
DISCORD_MAX_MESSAGE_LENGTH=2000
PLEASE_TRY_AGAIN_ERROR_MESSAGE='There was an issue with your question please try again.. '

class GeminiAgent(commands.Cog):

    def __init__(self,bot):
        self.bot = bot
        self.model = genai.GenerativeModel('gemini-pro')

    @commands.Cog.listener()
    async def on_message(self,msg):
        try:
            if msg.content == "ping gemini-agent":
                await msg.channel.send("Agent is connected..")
            elif 'Direct Message' in str(msg.channel) and not msg.author.bot:
                response = self.gemini_generate_content(msg.content)
                dmchannel = await msg.author.create_dm()
                await self.send_message_in_chunks(dmchannel,response) 
        except Exception as e:
            await msg.channel.send(PLEASE_TRY_AGAIN_ERROR_MESSAGE + str(e))

    @commands.command()
    async def query(self,ctx,question):
        try:
            response = self.gemini_generate_content(question)
            await self.send_message_in_chunks(ctx,response)
        except Exception as e:
            await ctx.send(PLEASE_TRY_AGAIN_ERROR_MESSAGE + str(e))

    @commands.command()
    async def pm(self,ctx):
        dmchannel = await ctx.author.create_dm()
        await dmchannel.send('Hi how can I help you today?')

    def gemini_generate_content(self,content):
        try:
            response = self.model.generate_content(content,stream=True)
            return response
        except Exception as e:
            return PLEASE_TRY_AGAIN_ERROR_MESSAGE + str(e)
        
    async def send_message_in_chunks(self,ctx,response):
        message = ""
        for chunk in response:
            message += chunk.text
            if len(message) > DISCORD_MAX_MESSAGE_LENGTH:
                extraMessage = message[DISCORD_MAX_MESSAGE_LENGTH:]
                message = message[:DISCORD_MAX_MESSAGE_LENGTH]
                await ctx.send(message)
                message = extraMessage
        if len(message) > 0:
            while len(message) > DISCORD_MAX_MESSAGE_LENGTH:
                extraMessage = message[DISCORD_MAX_MESSAGE_LENGTH:]
                message = message[:DISCORD_MAX_MESSAGE_LENGTH]
                await ctx.send(message)
                message = extraMessage
            await ctx.send(message)


bot.run(os.getenv('DISCORD_TOKEN'))
