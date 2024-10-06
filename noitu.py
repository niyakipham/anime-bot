import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True  # Cần để xử lý nội dung tin nhắn

bot = commands.Bot(command_prefix="!", intents=intents)

# Các biến toàn cục để theo dõi trạng thái trò chơi
is_game_active = False
last_word = ""
players = []


@bot.event
async def on_ready():
    print(f'{bot.user} đã sẵn sàng!')


@bot.command(name="noitu")
async def start_game(ctx):
    """Trò chơi nối từ bắt đầu"""
    global is_game_active, last_word, players
    if is_game_active:
        await ctx.send("Trò chơi đã được bắt đầu. Vui lòng hoàn thành trò chơi hiện tại trước khi bắt đầu trò chơi mới!")
    else:
        is_game_active = True
        last_word = ""
        players = []
        await ctx.send("Trò chơi nối từ đã bắt đầu! Hãy nói từ đầu tiên.")


@bot.command(name="endnoitu")
async def end_game(ctx):
    """Kết thúc trò chơi nối từ"""
    global is_game_active
    if is_game_active:
        is_game_active = False
        await ctx.send("Trò chơi đã kết thúc!")
    else:
        await ctx.send("Không có trò chơi nào đang diễn ra để kết thúc.")


@bot.event
async def on_message(message):
    global is_game_active, last_word, players

    if message.author == bot.user:
        return  # Không phản hồi lại tin nhắn của bot

    if is_game_active and not message.content.startswith("!"):
        # Lấy nội dung tin nhắn người chơi nhập
        current_phrase = message.content.strip().lower()

        # Nếu chưa có từ bắt đầu
        if not last_word:
            last_word = current_phrase.split()[-1]  # Lưu từ cuối của cụm từ đầu tiên
            players.append(message.author)  # Thêm người chơi vào danh sách
            await message.channel.send(f"{message.author.mention} bắt đầu với từ: {current_phrase}")
        else:
            # Kiểm tra nếu từ đầu của cụm từ mới khớp với từ cuối của cụm từ trước
            if current_phrase.split()[0] == last_word:
                last_word = current_phrase.split()[-1]  # Cập nhật từ cuối mới
                if message.author not in players:
                    players.append(message.author)  # Thêm người chơi mới vào danh sách
                await message.channel.send(f"{message.author.mention} đã nối từ thành công! Từ tiếp theo bắt đầu bằng: '{last_word}'")
            else:
                await message.channel.send(f"{message.author.mention} không nối đúng từ! Trò chơi kết thúc.")
                is_game_active = False

    await bot.process_commands(message)  # Xử lý các lệnh khác


# Thay YOUR_BOT_TOKEN bằng token của bot bạn

bot.run('MTI4OTUyODk5NzA4ODA2NzYwNg.G9R7e3.dlVut9wb5CFjYInBF-YGmSRhcIss6_OnNUat28')
