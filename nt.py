from discord.ext import commands, tasks
import requests
import random
import os
from discord import Client

def get_aiohttp_client():
    from aiohttp import ClientSession  # Import aiohttp only when needed
    return ClientSession()

async def some_function(self, ctx):
    async with get_aiohttp_client() as session:
        # Use the session here
        pass
# Token bot Discord của bạn
TOKEN = os.getenv("DISCORD_TOKEN")

# ID kênh bạn muốn gửi ảnh
CHANNEL_ID = 1295293677828309032 # Thay thế bằng ID kênh của bạn

# API Key Pexels của bạn
PEXELS_API_KEY = 'ZUNPocwnNyEFmqeSiJmLaoGZ7JjQWRtlXFKP0h2QimRt86QQzj81VYX4' # Lưu API key trong biến môi trường

# Từ khóa tìm kiếm ảnh nền
SEARCH_QUERY = "Night Time"

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@tasks.loop(seconds=60)  # Mặc định là 1 giờ (3600 giây), thay đổi nếu cần
async def send_wallpaper():
    try:
        # Gọi API Pexels
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": SEARCH_QUERY, "per_page": 100000} # Lấy tối đa 50 ảnh
        response = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params)
        response.raise_for_status() # Kiểm tra lỗi HTTP
        data = response.json()

        # Chọn ngẫu nhiên một ảnh
        if data["photos"]:
            photo = random.choice(data["photos"])
            image_url = photo["src"]["original"] # Sử dụng URL ảnh gốc


            # Lấy kênh
            channel = bot.get_channel(CHANNEL_ID)
            if not channel:
                print(f"Không tìm thấy kênh có ID {CHANNEL_ID}")
                return
            
            # Gửi ảnh bằng embed để hiển thị đẹp hơn
            embed = discord.Embed(title="Hình nền ngẫu nhiên từ Pexels")
            embed.set_image(url=image_url)
            await channel.send(embed=embed)



        else:
            print("Không tìm thấy ảnh nào.")


    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi API Pexels: {e}")
    except Exception as e:
        print(f"Lỗi khác: {e}")



@bot.event
async def on_ready():
    print(f"{bot.user} đã kết nối!")
    send_wallpaper.start()




bot.run(os.getenv('NT'))