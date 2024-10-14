import discord, asyncio, aiohttp, os
import pandas as pd
from discord.ext import commands

TOKEN = os.getenv('DISCORD_TOKEN')

# Khởi tạo intents
intents = discord.Intents.default()
intents.message_content = True

# Tạo một instance bot
bot = commands.Bot(command_prefix='!', intents=intents)

# ID của kênh mà bot sẽ chỉ cho phép gửi ảnh
CHANNEL_IDS = [1295014200967561328, 1295019163076530319, 1295293677828309032]  # WALL và MEME

# ID của người dùng được phép gửi tin nhắn không phải ảnh
ALLOWED_USER_IDS = [1295285744771924042, 1289528997088067606, 1292857374616457281] # Thay thế bằng ID người dùng thực tế

@bot.event
async def on_message(message):
    # Nếu tin nhắn được gửi bởi người dùng được phép, không làm gì cả
    if message.author.id in ALLOWED_USER_IDS:
        await bot.process_commands(message)
        return

    # Nếu tin nhắn không được gửi trong kênh đã chỉ định hoặc là tin nhắn từ bot thì bỏ qua
    if message.channel.id not in CHANNEL_IDS or message.author == bot.user:
        await bot.process_commands(message)
        return

    # Kiểm tra nếu tin nhắn chứa file đính kèm và tất cả đều là ảnh
    if message.attachments:
        for attachment in message.attachments:
            if not attachment.content_type.startswith('image/'):
                await message.delete()
                await message.channel.send(f"{message.author.mention}, chỉ được gửi hình ảnh trong kênh này!", delete_after=5)
                return # Thoát khỏi hàm sau khi xóa tin nhắn
    else:
        # Nếu tin nhắn không chứa file đính kèm thì xóa tin nhắn
        await message.delete()
        await message.channel.send(f"{message.author.mention}, chỉ được gửi hình ảnh trong kênh này!", delete_after=5)
        return # Thoát khỏi hàm sau khi xóa tin nhắn


    await bot.process_commands(message)


bot.run(os.getenv('WALL_TOKEN'))
