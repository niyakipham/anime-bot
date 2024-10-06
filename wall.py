import discord, asyncio, aiohttp
import pandas as pd
from discord.ext import commands

# ID của kênh mà bot sẽ chỉ cho phép gửi ảnh
CHANNEL_ID = 1291045191687475230 # Thay thế bằng ID kênh của bạn

# Khởi tạo intents
intents = discord.Intents.default()
intents.message_content = True

# Tạo một instance bot
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot đã đăng nhập với tên: {bot.user}')

@bot.event
async def on_message(message):
    # Nếu tin nhắn không được gửi trong kênh đã chỉ định hoặc là tin nhắn từ bot thì bỏ qua
    if message.channel.id != CHANNEL_ID or message.author == bot.user:
        return

    # Kiểm tra nếu tin nhắn chứa file đính kèm và tất cả đều là ảnh
    if message.attachments:
        for attachment in message.attachments:
            if not attachment.content_type.startswith('image/'):
                await message.delete()  # Xóa tin nhắn nếu tệp đính kèm không phải ảnh
                await message.channel.send(f"{message.author.mention}, chỉ được gửi hình ảnh trong kênh này!", delete_after=5)
                return
    else:
        # Nếu tin nhắn không chứa file đính kèm thì xóa tin nhắn
        await message.delete()
        await message.channel.send(f"{message.author.mention}, chỉ được gửi hình ảnh trong kênh này!", delete_after=5)

bot.run('MTI5MjM5ODAyODg4NzU2MDE5Mw.GzlcYC.orxY4aPlyk3H5eEPb3p867mvlHPs0G2UJaHbm0')
