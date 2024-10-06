import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True  # Cần để xử lý nội dung tin nhắn

bot = commands.Bot(command_prefix="!", intents=intents)

# Biến toàn cục để theo dõi trạng thái trò chơi
is_game_active = False
last_word = ""
players = []


@bot.event
async def on_ready():
    print(f'{bot.user} đã sẵn sàng!')


@bot.command()
async def start(ctx):
    global is_game_active, last_word, players

    if is_game_active:
        await ctx.send("Trò chơi đã đang diễn ra! Hãy tiếp tục chơi.")
    else:
        is_game_active = True
        last_word = ""
        players = []
        await ctx.send("Trò chơi nối từ đã bắt đầu! Người chơi đầu tiên hãy nói cụm từ của mình.")


@bot.command()
async def end(ctx):
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
                await message.channel.send(f"{message.author.mention} đã nối từ thành công! Từ tiếp theo bắt đầu là: '{last_word}'")
            else:
                await message.channel.send(f"{message.author.mention} đã nối sai từ! Trò chơi kết thúc.")
                is_game_active = False

    await bot.process_commands(message)  # Để xử lý các lệnh khác


# Thay 'YOUR_BOT_TOKEN' bằng token của bot của bạn

bot.run('MTI4OTUyODk5NzA4ODA2NzYwNg.G9R7e3.dlVut9wb5CFjYInBF-YGmSRhcIss6_OnNUat28')
