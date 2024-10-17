import discord
import nekos
import os
from discord.ext import tasks

# Token bot Discord (thay bằng token của bạn)
TOKEN = 'YOUR_DISCORD_BOT_TOKEN'

# ID của kênh Discord nơi bạn muốn gửi ảnh định kỳ
  # Thay bằng ID của kênh Discord bạn muốn gửi ảnh

WALL_ID = 1295293677828309032
# Tạo client Discord với prefix và intents đầy đủ quyền
client = discord.Client(intents=discord.Intents.all())

# Sự kiện khi bot đã sẵn sàng
@client.event
async def on_ready():
    print(f'Bot đã đăng nhập với tên: {client.user}')
    # Khởi động task gửi ảnh mỗi 1 phút
    send_image_task.start()

# Hàm gửi ảnh từ Nekos API theo lệnh
async def send_nekos_image(command, message):
    try:
        image_url = nekos.img(command)  # Lấy ảnh từ endpoint tương ứng
        await message.channel.send(image_url)
    except Exception as e:
        await message.channel.send(f"Đã xảy ra lỗi: {e}")

# Sự kiện khi bot nhận tin nhắn
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Danh sách các lệnh có sẵn
    commands = ['wallpaper', 'ngif', 'tickle', 'feed', 'gecg', 'gasm', 'slap', 
                'avatar', 'lizard', 'waifu', 'pat', '8ball', 'kiss', 'neko', 
                'spank', 'cuddle', 'fox_girl', 'hug', 'smug', 'goose', 'woof']

    # Kiểm tra lệnh và gửi ảnh
    for command in commands:
        if message.content.startswith(f"!{command}"):
            await send_nekos_image(command, message)
            return

# Tạo task tự động gửi ảnh vào kênh mỗi phút
@tasks.loop(minutes=1)
async def send_image_task():
    # Kiểm tra nếu bot đã sẵn sàng
    if client.is_ready():
        # Lấy kênh bằng ID
        channel = client.get_channel(WALL_ID)
        if channel:
            neko_image_url = nekos.img('wallpaper')  # Lấy ảnh từ endpoint 'neko'




client.run(os.getenv('NT_TOKEN'))