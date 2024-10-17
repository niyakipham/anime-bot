import discord
import nekos
import os
from discord.ext import tasks


# ID của kênh Discord nơi bạn muốn gửi ảnh định kỳ
  # Thay bằng ID của kênh Discord bạn muốn gửi ảnh

WALL = 1295293677828309032
# Tạo client Discord với prefix và intents đầy đủ quyền
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
# Sự kiện khi bot đã sẵn sàng
@bot.event
async def on_ready():
    print(f'Bot đã đăng nhập với tên: {bot.user}')
    # Khởi động task gửi ảnh mỗi 1 phút
    send_image_task.start()

# Sự kiện khi bot nhận tin nhắn
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

@tasks.loop(minutes=1)
async def send_image_task():
    # Kiểm tra nếu bot đã sẵn sàng
    if bot.is_ready():
        # Lấy kênh bằng ID
        channel = bot.get_channel(TARGET_CHANNEL_ID)
        if channel:
            neko_image_url = nekos.img('wallpaper')  # Lấy ảnh từ endpoint 'neko'
            await channel.send(f"Tự động gửi ảnh mỗi phút:\n{neko_image_url}")




bot.run(os.getenv('NT_TOKEN'))