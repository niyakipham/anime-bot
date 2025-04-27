import discord
import os
import pandas as pd
from discord.ext import commands
import re

# --- Cấu hình ---
BOT_TOKEN = "YOUR_BOT_TOKEN"  # Thay thế bằng token bot của bạn
ANIME_CSV_FILE = 'anime.csv'
COMMAND_PREFIX = '!'
ALLOWED_CHANNEL_IDS = [1326048067073347687, 1313488880808235120, 1326174667756540035, 1294120125259186209, 1294120125259186210, 1294120125259186211]  # Thay thế bằng các ID kênh
THUMBNAIL_URL = "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/e966882e-aa10-42dc-8402-f6211384a5ac/anim=false,width=450/00001-871932184.jpeg"

# --- Biến toàn cục ---
anime_data = None

# --- Hàm hỗ trợ ---
def load_anime_data():
    """Tải dữ liệu anime từ file CSV."""
    global anime_data
    try:
        anime_data = pd.read_csv(ANIME_CSV_FILE)
        print(f"Đã tải {len(anime_data)} anime từ {ANIME_CSV_FILE}")
        print(f"Các cột: {anime_data.columns.tolist()}")
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file {ANIME_CSV_FILE}")
        anime_data = pd.DataFrame()
    except Exception as e:
        print(f"Lỗi: Không thể tải dữ liệu từ {ANIME_CSV_FILE}. Lỗi: {e}")
        anime_data = pd.DataFrame()

def search_by_keywords_and_episode(keywords, episode):
    """Tìm kiếm anime theo tổ hợp từ khóa và số tập."""
    if anime_data is None or anime_data.empty:
        print("Dữ liệu anime chưa được tải.")
        return None

    keyword_list = keywords.lower().split()

    filtered_anime = anime_data.copy()
    for keyword in keyword_list:
        filtered_anime = filtered_anime[filtered_anime['name'].str.lower().str.contains(keyword, case=False, na=False)]

    result = filtered_anime[filtered_anime['episodes'].astype(str) == str(episode)]

    if not result.empty:
        return result.head(3)
    else:
        return None

# --- Kiểm tra kênh ---
def is_allowed_channel():
    """Decorator kiểm tra kênh cho phép."""
    async def predicate(ctx):
        return ctx.channel.id in ALLOWED_CHANNEL_IDS
    return commands.check(predicate)

# --- Bot initialization ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# --- Events ---
@bot.event
async def on_ready():
    print(f'{bot.user} đã kết nối!')
    load_anime_data()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send(f"Lệnh này chỉ hoạt động trong các kênh được cho phép.")
    else:
        print(f"Lỗi: {error}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id in ALLOWED_CHANNEL_IDS: # Thay đổi
        content = message.content.lower()
        match = re.search(r"(.+)\s+tập\s+(\d+)", content)
        if match:
            keywords = match.group(1).strip()
            episode = match.group(2)
            
            print(f"Đang tìm: {keywords} - Tập {episode}")
            result_df = search_by_keywords_and_episode(keywords, episode)
            
            if result_df is not None:
                for index, row in result_df.iterrows():
                    embed = discord.Embed(title=f"📺 {row['name']}", description=f"Tập {episode}", color=discord.Color.from_rgb(52, 152, 219))
                    embed.add_field(name="🔗 Link", value=row['link'], inline=False)
                    embed.set_thumbnail(url=THUMBNAIL_URL)
                    embed.set_footer(text="Dữ liệu cập nhật đến 5/1/2025")
                    await message.channel.send(embed=embed)
            else:
                await message.channel.send(f"Không tìm thấy anime với từ khóa '{keywords}' tập {episode}.")

    await bot.process_commands(message)

# --- Commands ---
@bot.command(name='ani')
@is_allowed_channel()
async def search_anime(ctx, *, anime_name: str):
    """Tìm kiếm thông tin anime."""
    if anime_data is None or anime_data.empty:
        await ctx.send("Dữ liệu anime chưa được tải hoặc bị lỗi.")
        return

    result = anime_data[anime_data['name'].str.contains(anime_name, case=False, na=False)]

    if result.empty:
        await ctx.send("Dữ liệu anime chưa được tải hoặc bị lỗi.")
        return

    embed = discord.Embed(title=f"🔍 Kết quả tìm kiếm cho '{anime_name}'", color=discord.Color.from_rgb(231, 76, 60))
    embed.set_thumbnail(url=THUMBNAIL_URL)

    field_count = 0
    for index, row in result.iterrows():
        if field_count >= 25:
            embed.set_footer(text="Dữ liệu cập nhật đến 5/1/2025")
            await ctx.send(embed=embed)

            embed = discord.Embed(title=f"🔍 Kết quả tìm kiếm cho '{anime_name}' (tiếp theo)", color=discord.Color.from_rgb(231, 76, 60))
            embed.set_thumbnail(url=THUMBNAIL_URL)
            field_count = 0

        embed.add_field(name=f"**{row['name']}**", value=f"📺 Tập: {row['episodes']}\n🔗 Link: {row['link']}", inline=False)
        field_count += 1

    if field_count > 0:
        embed.set_footer(text="Dữ liệu cập nhật đến 5/1/2025")
        await ctx.send(embed=embed)

bot.run(os.getenv('ANIME'))
