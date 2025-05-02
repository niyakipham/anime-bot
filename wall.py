
import discord
from discord.ext import commands
import yt_dlp # Sử dụng yt-dlp cho hiệu năng và tính năng tốt hơn
import asyncio
import nacl # PyNaCl phải được import (cài đặt: pip install PyNaCl)
import os
from dotenv import load_dotenv
from datetime import timedelta, datetime, timezone # <--- THÊM datetime và timezone
from typing import List, Dict, Optional, Tuple, Union # <--- THÊM Union
import traceback # Thêm để dùng print_exc đầy đủ
import time # Có thể cần cho vài thứ (ví dụ decorator benchmark nếu dùng)

# --- ✨ KAGUYA CORE CONFIGURATION ✨ ---
load_dotenv()
# --- QUAN TRỌNG: Không bao giờ hardcode token thật vào code ---
# Sử dụng os.getenv để lấy từ môi trường hoặc file .env
# Token ví dụ dưới đây KHÔNG phải token thật và chỉ mang tính minh họa
DISCORD_TOKEN = (os.getenv('DISCORD_TOKEN'))
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!") # Lấy prefix từ .env hoặc dùng mặc định

# --- 🎼 YT-DLP & FFMPEG SETTINGS 🎼 ---
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0', # Có thể cần cho vài môi trường hosting
    # 'extract_flat': True, # <-- Nên set là False khi lấy info 1 bài, True khi search list
    'skip_download': True,
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -bufsize 64k' # -vn: no video, bufsize nhỏ để giảm latency
}

# --- ⚙️ KAGUYA BOT INITIALIZATION ⚙️ ---
intents = discord.Intents.default()
intents.message_content = True # Cần để đọc lệnh và nội dung tin nhắn
intents.voice_states = True    # Cần để quản lý trạng thái kênh thoại

# Bot được khởi tạo ở gần cuối file sau khi mọi thứ đã định nghĩa xong

# --- 🎨 HÀM TIỆN ÍCH 🎨 ---

# Biến màu sắc chuẩn (TÙY CHỌN - để quản lý màu dễ hơn)
EMBED_COLOR_INFO = discord.Color.blue()
EMBED_COLOR_SUCCESS = discord.Color.green()
EMBED_COLOR_WARNING = discord.Color.gold()
EMBED_COLOR_ERROR = discord.Color.red()
EMBED_COLOR_MUSIC = discord.Color.purple()
EMBED_COLOR_KAGUYA = 0xB026FF # Tím plasma Kaguya

# Hàm trợ giúp tạo embed chuẩn Kaguya (SỬA LỖI TIMESTAMP Ở ĐÂY)
def create_kaguya_embed(title: str, description: str = "", color: discord.Color = EMBED_COLOR_KAGUYA, **kwargs) -> discord.Embed:
    """Tạo Embed với phong cách Kaguya."""
    embed = discord.Embed(title=f"✨ {title}", description=description, color=color, **kwargs)
    # embed.set_footer(text="Powered by Kaguya's Logic 💫", icon_url=bot.user.avatar.url if bot and bot.user and bot.user.avatar else None) # bot chưa được định nghĩa ở đây!

    # *** ✨ SỬA LỖI TIMESTAMP ✨ ***
    # Sử dụng datetime.now(timezone.utc) thay vì discord.utils.utcnow()
    embed.timestamp = datetime.now(timezone.utc)
    return embed

# --- 🎵 MUSIC COG 🎵 ---
class MusicCog(commands.Cog, name="🎵 Âm Nhạc"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Dùng dictionary riêng trong cog thay vì global guild_states
        self.guild_states: Dict[int, Dict] = {}

    # Override get_guild_state để set icon footer chuẩn
    def create_guild_embed(self, guild_id: int, title: str, description: str = "", color: discord.Color = EMBED_COLOR_KAGUYA, **kwargs) -> discord.Embed:
         """Tạo Embed chuẩn cho guild này, thêm icon bot vào footer."""
         embed = create_kaguya_embed(title, description, color, **kwargs)
         if self.bot.user and self.bot.user.avatar:
              embed.set_footer(text="Powered by Kaguya's Logic 💫", icon_url=self.bot.user.avatar.url)
         else:
              embed.set_footer(text="Powered by Kaguya's Logic 💫")
         return embed

    def get_guild_state(self, guild_id: int) -> Dict:
        """Lấy hoặc tạo trạng thái cho một guild."""
        if guild_id not in self.guild_states:
            self.guild_states[guild_id] = {
                "queue": asyncio.Queue(),
                "now_playing": None,
                "voice_client": None,
                "text_channel": None, # Kênh text nơi gọi lệnh cuối cùng
                "playback_task": None, # Task chạy bài hát hiện tại
                "loop_mode": "off", # off, song, queue
                # "search_results": {}, # Lưu search trong View/Context thay vì state lâu dài
                "lock": asyncio.Lock(), # Lock để tránh race condition
                "volume": 0.5 # Âm lượng mặc định
            }
        return self.guild_states[guild_id]

    async def _ensure_voice(self, ctx: commands.Context) -> Optional[discord.VoiceClient]:
        """Đảm bảo bot đang ở trong kênh thoại của người dùng."""
        state = self.get_guild_state(ctx.guild.id)
        user_vc = ctx.author.voice

        if not user_vc or not user_vc.channel:
            await ctx.send(embed=self.create_guild_embed(ctx.guild.id, "🚫 Lỗi Kết Nối", f"{ctx.author.mention}, cậu phải ở trong kênh thoại mới dùng lệnh này được chứ!", EMBED_COLOR_ERROR))
            return None

        voice_client = state.get("voice_client")
        destination_channel = user_vc.channel

        if voice_client is None or not voice_client.is_connected():
            try:
                # print(f"Connecting to {destination_channel.name}")
                state["voice_client"] = await destination_channel.connect(timeout=30.0, reconnect=True)
                state["text_channel"] = ctx.channel # Lưu kênh text
                await ctx.send(embed=self.create_guild_embed(ctx.guild.id, "🔊 Tham Gia Kênh Thoại", f"Đã kết nối tới `{destination_channel.name}` và sẵn sàng phục vụ!", EMBED_COLOR_SUCCESS))
            except asyncio.TimeoutError:
                 await ctx.send(embed=self.create_guild_embed(ctx.guild.id, "🚫 Lỗi Kết Nối", "Kết nối tới kênh thoại thất bại do timeout!", EMBED_COLOR_ERROR))
                 return None
            except discord.errors.ClientException as e:
                 await ctx.send(embed=self.create_guild_embed(ctx.guild.id, "🚫 Lỗi Kết Nối", f"Đã xảy ra lỗi Client: `{e}` (Bot có thể đang bận kết nối ở đâu đó?)", EMBED_COLOR_ERROR))
                 return None
            except Exception as e:
                await ctx.send(embed=self.create_guild_embed(ctx.guild.id, "🚫 Lỗi Kết Nối", f"Không thể kết nối kênh thoại: `{e}`", EMBED_COLOR_ERROR))
                traceback.print_exc()
                return None
        elif voice_client.channel != destination_channel:
             try:
                # print(f"Moving to {destination_channel.name}")
                await voice_client.move_to(destination_channel)
                state["text_channel"] = ctx.channel # Cập nhật kênh text
                await ctx.send(embed=self.create_guild_embed(ctx.guild.id, "🚀 Di Chuyển Kênh", f"Đã di chuyển tới `{destination_channel.name}`.", EMBED_COLOR_INFO))
             except asyncio.TimeoutError:
                 await ctx.send(embed=self.create_guild_embed(ctx.guild.id, "🚫 Lỗi Di Chuyển", "Di chuyển kênh thoại thất bại do timeout!", EMBED_COLOR_ERROR))
                 return None
             except Exception as e:
                 await ctx.send(embed=self.create_guild_embed(ctx.guild.id, "🚫 Lỗi Di Chuyển", f"Không thể di chuyển kênh: `{e}`", EMBED_COLOR_ERROR))
                 traceback.print_exc()
                 return None
        else:
            # Vẫn ở kênh cũ, cập nhật kênh text nếu gọi từ kênh khác
             state["text_channel"] = ctx.channel

        # Luôn đảm bảo voice_client được cập nhật trong state
        # discord.utils.get không còn hoạt động như trước, lấy trực tiếp từ state là tốt nhất
        # Hoặc kiểm tra guild.voice_client
        state["voice_client"] = ctx.guild.voice_client # Đây là cách chuẩn để lấy voice_client hiện tại của guild
        return state.get("voice_client")


    async def _fetch_song_info(self, query: str, requested_by: discord.Member) -> Optional[Dict]:
         """Lấy thông tin BÀI HÁT ĐƠN LẺ từ yt-dlp (URL hoặc tìm kiếm video ĐẦU TIÊN)."""
         loop = asyncio.get_event_loop()
         ydl_opts_local = YDL_OPTIONS.copy()
         # TẮT 'extract_flat' khi lấy thông tin chi tiết 1 video
         ydl_opts_local['extract_flat'] = False
         # TẮT 'noplaylist' để link playlist có thể lấy video đầu nếu muốn (hoặc xử lý riêng)
         # ydl_opts_local['noplaylist'] = False # Giữ True trong config gốc và chỉ đổi khi cần playlist

         # Xác định có phải URL không để quyết định dùng search hay không
         is_url = query.startswith(('http://', 'https://'))
         search_query = query if is_url else f"ytsearch1:{query}" # Tìm kiếm và chỉ lấy kết quả đầu tiên

         # print(f"Fetching info for: {search_query}")
         try:
             with yt_dlp.YoutubeDL(ydl_opts_local) as ydl:
                 info = await loop.run_in_executor(None, lambda: ydl.extract_info(search_query, download=False))

             if not info:
                # print(f"YDL returned no info for: {query}")
                return None

             # Xử lý cấu trúc trả về khác nhau của yt-dlp
             # ytsearch trả về playlist với entry đầu tiên trong 'entries'
             # URL video trả về dict trực tiếp
             # URL playlist (với noplaylist=False) cũng trả về playlist
             entry = None
             if '_type' in info and info['_type'] == 'playlist':
                 if 'entries' in info and info['entries']:
                    entry = info['entries'][0] # Lấy mục đầu tiên từ kết quả search/playlist URL
             elif 'entries' in info and info['entries']: # Vài search đặc biệt có thể vẫn là list
                 entry = info['entries'][0]
             elif info: # Là video đơn lẻ
                 entry = info

             if not entry:
                 # print(f"Could not extract a valid entry from YDL info for: {query}")
                 return None

             # Ưu tiên lấy URL stream từ format (thường ổn định hơn entry['url'])
             stream_url = None
             best_format = None

             # print(f"Available formats for {entry.get('title', 'N/A')}:")
             for f in entry.get('formats', []):
                # Debug formats if needed:
                # print(f"  - Format: {f.get('format_id')}, acodec: {f.get('acodec')}, vcodec: {f.get('vcodec')}, url: {'Yes' if f.get('url') else 'No'}, abr: {f.get('abr')}")
                # Chọn format CÓ audio, KHÔNG video và CÓ url
                if f.get('acodec') != 'none' and f.get('vcodec') == 'none' and f.get('url'):
                    if best_format is None: # Lấy cái đầu tiên tìm thấy
                         best_format = f
                    # Ưu tiên opus hoặc bitrate cao hơn
                    elif f.get('acodec') == 'opus': # Ưu tiên opus
                         best_format = f
                         break # Đã tìm thấy best
                    elif best_format.get('acodec') != 'opus' and f.get('abr', 0) > best_format.get('abr', 0): # Lấy bitrate cao hơn nếu chưa có opus
                         best_format = f

             stream_url = best_format['url'] if best_format and best_format.get('url') else entry.get('url')

             if not stream_url:
                # print(f"Warning: Could not find direct stream URL for {entry.get('title', query)}. Attempting fallback...")
                # Fallback cuối cùng có thể là URL trang, nhưng FFmpeg có thể không xử lý được
                stream_url = entry.get('webpage_url', entry.get('original_url', entry.get('url')))

             if not stream_url:
                 # print(f"ERROR: No playable URL found for {entry.get('title', query)}")
                 return None # Không thể phát nếu không có URL

             duration_seconds = entry.get('duration')
             # Chuyển duration thành integer nếu có thể
             if duration_seconds is not None:
                 try:
                    duration_seconds = int(duration_seconds)
                 except ValueError:
                    duration_seconds = 0 # Hoặc log lỗi nếu cần
             else:
                 duration_seconds = 0

             duration_str = str(timedelta(seconds=duration_seconds)) if duration_seconds > 0 else "Livestream/N/A"

             return {
                 'title': entry.get('title', 'Không rõ tiêu đề'),
                 'webpage_url': entry.get('webpage_url', query),
                 'stream_url': stream_url, # URL dùng để stream audio
                 'thumbnail': entry.get('thumbnail'),
                 'duration_s': duration_seconds,
                 'duration': duration_str,
                 'uploader': entry.get('uploader', 'Không rõ'),
                 'view_count': entry.get('view_count'),
                 'requested_by': requested_by, # Gán người yêu cầu
                 'id': entry.get('id') # ID hữu ích cho vài việc
             }

         except yt_dlp.utils.DownloadError as e:
            # print(f"yt-dlp DownloadError for '{query}': {e}")
            # Có thể chỉ là không tìm thấy video -> trả về None nhẹ nhàng
             if "video is unavailable" in str(e).lower() or "rejected" in str(e).lower() :
                 #print(f"Video unavailable or private.")
                 pass
             else: # Lỗi khác đáng báo hơn
                 print(f"Unhandled yt-dlp DownloadError for '{query}': {e}")
                 return None
         except Exception as e:
            print(f"!!! Unhandled Exception in _fetch_song_info for '{query}': {e}")
            traceback.print_exc()
            return None

    async def _fetch_search_results(self, query: str, max_results: int = 5) -> List[Dict]:
        """Tìm kiếm NHIỀU KẾT QUẢ bằng yt-dlp."""
        loop = asyncio.get_event_loop()
        ydl_opts_search = YDL_OPTIONS.copy()
        ydl_opts_search['noplaylist'] = False # PHẢI tắt để ytsearchN hoạt động
        # extract_flat giúp search nhanh hơn nhiều
        ydl_opts_search['extract_flat'] = 'in_playlist' # Lấy info cơ bản NHANH

        results = []
        # Đúng cú pháp: ytsearch<Số kết quả>:<Từ khóa>
        search_query = f"ytsearch{max_results}:{query}"

        # print(f"Searching multiple results: {search_query}")
        try:
            with yt_dlp.YoutubeDL(ydl_opts_search) as ydl:
                info = await loop.run_in_executor(None, lambda: ydl.extract_info(search_query, download=False))

                if 'entries' in info:
                    for entry in info.get('entries', []): # Dùng .get cho an toàn
                        # Lọc bỏ kết quả không hợp lệ hoặc channel/playlist links trong search results
                        if entry and entry.get('url') and entry.get('_type', 'video') == 'video':
                             duration_s = entry.get('duration')
                             if duration_s is not None:
                                 try: duration_s = int(duration_s)
                                 except ValueError: duration_s = 0
                             else: duration_s = 0

                             duration_str = str(timedelta(seconds=duration_s)) if duration_s > 0 else "N/A"
                             results.append({
                                 'title': entry.get('title', 'Không rõ tiêu đề'),
                                 'webpage_url': entry.get('webpage_url') or f"https://www.youtube.com/watch?v={entry.get('id')}",
                                 'duration': duration_str,
                                 'duration_s': duration_s,
                                 'id': entry.get('id'), # Lưu ID để lấy full info sau nếu cần
                                 'uploader': entry.get('uploader', 'Không rõ')
                                 # KHÔNG lấy stream_url ở đây vì extract_flat không có
                             })
        except yt_dlp.utils.DownloadError as e:
            print(f"yt-dlp Search DownloadError for '{query}': {e}")
        except Exception as e:
            print(f"!!! Unhandled Exception in _fetch_search_results for '{query}': {e}")
            traceback.print_exc()

        return results


    async def _play_next(self, guild_id: int):
        """Phát bài hát tiếp theo trong hàng đợi. Được gọi nội bộ."""
        state = self.get_guild_state(guild_id)
        # Đảm bảo chỉ 1 task chạy _play_next tại 1 thời điểm cho guild
        async with state["lock"]:
             # print(f"DEBUG [{guild_id}]: Entering _play_next.")
             if state.get("playback_task") and not state["playback_task"].done():
                # Lấy task đang chạy
                running_task = state.get("playback_task")
                if running_task and running_task != asyncio.current_task(): # Đảm bảo không phải chính task này
                    # print(f"DEBUG [{guild_id}]: Another playback task is running or about to run. Exiting.")
                    return # Task khác đang chạy hoặc sắp chạy

             voice_client = state.get("voice_client")
             text_channel = state.get("text_channel")

             if not voice_client or not voice_client.is_connected():
                 # print(f"DEBUG [{guild_id}]: Voice client not found or not connected in _play_next.")
                 # Clear state? Hoặc chờ reconnect? Hiện tại chỉ dừng
                 state["now_playing"] = None
                 state["playback_task"] = None
                 while not state["queue"].empty(): state["queue"].get_nowait() # Xóa queue
                 return

             # Xử lý dừng khi đang phát dở bài trước (ít khi xảy ra nếu dùng lock đúng)
             if voice_client.is_playing() or voice_client.is_paused():
                  # print(f"DEBUG [{guild_id}]: Stopping existing playback before playing next.")
                  voice_client.stop()
                  # Chờ một chút để 'after' (nếu có) kết thúc và lock được giải phóng hoàn toàn
                  # await asyncio.sleep(0.1) # Có thể không cần thiết với lock

             # Đã dừng hoặc chưa bắt đầu -> lấy bài mới

             next_song_request = None
             loop_mode = state.get("loop_mode", "off")
             current_song = state.get("now_playing") # Bài vừa KẾT THÚC hoặc None

             # 1. Xử lý LOOP QUEUE: Đưa bài VỪA PHÁT XONG (nếu có) vào cuối hàng đợi
             if loop_mode == "queue" and current_song:
                 # print(f"DEBUG [{guild_id}]: Looping queue, adding back: {current_song['title']}")
                 await state["queue"].put(current_song.copy()) # Quan trọng: copy để tránh alias
                 state["now_playing"] = None # Nó không còn là now_playing nữa

             # 2. Lấy bài tiếp theo: Tùy loop mode và hàng đợi
             if loop_mode == "song" and current_song:
                  # print(f"DEBUG [{guild_id}]: Looping song: {current_song['title']}")
                  next_song_request = current_song # Dùng lại bài vừa rồi
             elif not state["queue"].empty():
                 # print(f"DEBUG [{guild_id}]: Getting next song from queue.")
                 next_song_request = await state["queue"].get()
             else: # Hàng đợi rỗng và không loop bài
                 # print(f"DEBUG [{guild_id}]: Queue is empty, playback finished.")
                 state["now_playing"] = None
                 state["playback_task"] = None
                 if text_channel:
                     # Tránh gửi embed khi bot tự động dừng (ví dụ timeout không hoạt động)
                     # await text_channel.send(embed=self.create_guild_embed(guild_id, "✅ Hàng Đợi Trống", "Đã phát hết nhạc.", EMBED_COLOR_INFO))
                     pass # Im lặng thì tốt hơn
                 # Lên lịch tự động disconnect nếu muốn
                 # self.bot.loop.create_task(self._schedule_disconnect(guild_id))
                 return

             # Đã có next_song_request -> bắt đầu xử lý
             state["now_playing"] = next_song_request # Đánh dấu là đang xử lý bài này
             # print(f"DEBUG [{guild_id}]: Preparing to play: {next_song_request['title']}")

             # *** Quan trọng: Fetch lại info ĐẦY ĐỦ nếu bài hát lấy từ search/playlist (thiếu stream_url) ***
             # Nếu song_request đã có stream_url VÀ nó chưa hết hạn (khó biết), có thể dùng luôn
             # Fetch lại lúc play luôn an toàn hơn.
             # print(f"DEBUG [{guild_id}]: Fetching full info for playback...")
             full_song_info = await self._fetch_song_info(next_song_request['webpage_url'], next_song_request['requested_by'])

             if not full_song_info or not full_song_info.get('stream_url'):
                message = f"Không thể lấy stream URL cho: `{next_song_request['title']}`"
                if not full_song_info:
                     message = f"Không thể lấy thông tin đầy đủ cho: `{next_song_request['title']}` (Video có thể đã bị xóa hoặc lỗi)"
                print(f"ERROR [{guild_id}]: {message}")
                if text_channel: await text_channel.send(embed=self.create_guild_embed(guild_id, "🚫 Lỗi Playback", f"{message}. Đang bỏ qua và thử bài tiếp theo.", EMBED_COLOR_WARNING))
                state["now_playing"] = None # Không phát được bài này
                # Gọi lại _play_next ngay để thử bài tiếp theo, không cần delay
                # Đảm bảo nó chạy trong task mới để tránh recursion error
                state["playback_task"] = self.bot.loop.create_task(self._play_next(guild_id))
                # Không queue.put_nowait(song_request) vì lỗi, bỏ qua luôn
                return # Quan trọng: return ở đây để task hiện tại kết thúc

             state["now_playing"] = full_song_info # Cập nhật full info

             # Tạo source âm thanh
             try:
                audio_source = discord.FFmpegPCMAudio(full_song_info['stream_url'], **FFMPEG_OPTIONS)
                # Wrap với PCMVolumeTransformer để chỉnh volume
                transformed_audio = discord.PCMVolumeTransformer(audio_source)
                transformed_audio.volume = state.get("volume", 0.5) # Lấy volume từ state
             except Exception as e:
                 print(f"ERROR [{guild_id}]: Failed to create audio source for {full_song_info['title']}: {e}")
                 traceback.print_exc()
                 if text_channel: await text_channel.send(embed=self.create_guild_embed(guild_id, "🚫 Lỗi Âm Thanh", f"Không thể tạo audio source: `{e}`. Thử bài tiếp theo.", EMBED_COLOR_ERROR))
                 state["now_playing"] = None
                 state["playback_task"] = self.bot.loop.create_task(self._play_next(guild_id)) # Thử bài tiếp theo
                 return

             # --- Hàm callback `after` ---
             def after_playback(error):
                 # Hàm này chạy trong context khác, cẩn thận với state và thread safety
                 guild_state_after = self.get_guild_state(guild_id) # Lấy state mới nhất
                 song_that_just_played = guild_state_after["now_playing"] # Bài hát đã kết thúc này
                 guild_state_after["now_playing"] = None # Reset ngay khi xong bài
                 # Không reset playback_task ở đây vì nó do task _play_next quản lý

                 if error:
                    print(f'!!! Playback Error in guild {guild_id}: {error}')
                    err_msg = f"Có lỗi xảy ra khi phát bài `{song_that_just_played['title'] if song_that_just_played else 'N/A'}`: `{error}`"
                    coro = guild_state_after.get("text_channel").send(embed=self.create_guild_embed(guild_id, "⚠️ Lỗi Khi Phát", err_msg, EMBED_COLOR_WARNING)) if guild_state_after.get("text_channel") else None
                 # else:
                    # print(f"DEBUG [{guild_id}]: Finished playing: {song_that_just_played['title'] if song_that_just_played else 'N/A'}")

                 # Logic loop đã được xử lý bên trong _play_next rồi
                 # Chỉ cần gọi task mới để tiếp tục chuỗi phát nhạc

                 # Quan trọng: Gọi _play_next trong event loop của bot
                 # Tạo task mới để _play_next tự xử lý logic (lấy bài mới, loop, etc.)
                 if guild_state_after.get("voice_client"): # Chỉ tạo task mới nếu bot còn kết nối
                     new_task = self.bot.loop.create_task(self._play_next(guild_id))
                     # Lưu task này lại vào state để lệnh khác có thể check
                     # print(f"DEBUG [{guild_id}]: Creating next playback task from 'after' callback.")
                     guild_state_after["playback_task"] = new_task

             # --- Thực hiện Play ---
             try:
                 # print(f"DEBUG [{guild_id}]: Playing audio source for: {full_song_info['title']}")
                 voice_client.play(transformed_audio, after=after_playback)

                 embed_np = self.create_guild_embed(
                      guild_id,
                      f"▶️ Đang Phát",
                      f"**[{full_song_info['title']}]({full_song_info['webpage_url']})**\n"
                      f"`Thời lượng:` {full_song_info['duration']} | `Yêu cầu bởi:` {full_song_info['requested_by'].mention}",
                      EMBED_COLOR_MUSIC
                 )
                 if full_song_info.get('thumbnail'):
                      embed_np.set_thumbnail(url=full_song_info['thumbnail'])

                 # Thêm loop status vào footer của now playing
                 footer_text = embed_np.footer.text
                 current_loop_mode = state.get('loop_mode', 'off')
                 if current_loop_mode != 'off':
                     footer_text += f" | 🔁 Lặp: {current_loop_mode.capitalize()}"
                 embed_np.set_footer(text=footer_text, icon_url=embed_np.footer.icon_url)

                 if text_channel: await text_channel.send(embed=embed_np)

                 # Lưu ý: task _play_next vẫn đang chạy đến đây và sẽ kết thúc
                 # state["playback_task"] nên giữ nguyên task hiện tại cho đến khi after gọi cái mới
                 # Hoặc là set nó = None ở cuối lock này nếu ko dùng after để gọi lại? --> Nên để after quản lý việc tạo task MỚI.
                 # Task _play_next hiện tại kết thúc ở đây, việc phát nhạc do voice_client.play đảm nhiệm.

             except discord.ClientException as e:
                 print(f"ERROR [{guild_id}]: ClientException during play: {e}")
                 if text_channel: await text_channel.send(embed=self.create_guild_embed(guild_id, "🚫 Lỗi Playback Client", f"Không thể phát nhạc: `{e}`", EMBED_COLOR_ERROR))
                 state["now_playing"] = None
                 # Thử phát bài tiếp theo sau lỗi client
                 guild_state_after = self.get_guild_state(guild_id) # Lấy state mới nhất
                 guild_state_after["playback_task"] = self.bot.loop.create_task(self._play_next(guild_id)) # Tạo task mới thay thế
             except Exception as e:
                 print(f"ERROR [{guild_id}]: Unhandled Exception during play call: {e}")
                 traceback.print_exc()
                 if text_channel: await text_channel.send(embed=self.create_guild_embed(guild_id, "🚫 Lỗi Playback Chung", f"Lỗi không xác định khi bắt đầu phát: `{e}`", EMBED_COLOR_ERROR))
                 state["now_playing"] = None
                 guild_state_after = self.get_guild_state(guild_id)
                 guild_state_after["playback_task"] = self.bot.loop.create_task(self._play_next(guild_id))


    # async def _play_next_after_delay(self, guild_id: int, delay: float):
    #     """Hàm helper để gọi _play_next sau một khoảng trễ ngắn."""
    #     # print(f"DEBUG [{guild_id}]: Scheduling _play_next after {delay}s delay.")
    #     await asyncio.sleep(delay)
    #     state = self.get_guild_state(guild_id)
    #     if state.get("voice_client") and not state.get("voice_client").is_playing(): # Chỉ tạo task nếu còn trong vc VÀ không đang phát gì
    #         state["playback_task"] = self.bot.loop.create_task(self._play_next(guild_id))

    async def _handle_queue_addition(self, ctx: commands.Context, song_info_list: List[Dict]):
         """Xử lý thêm một hoặc nhiều bài hát vào hàng đợi và bắt đầu phát nếu cần."""
         state = self.get_guild_state(ctx.guild.id)
         async with state["lock"]:
             if not song_info_list:
                 return 0 # Không có gì để thêm

             added_count = 0
             first_song_info = None # Để hiện thumbnail bài đầu tiên nếu thêm list
             for song_info in song_info_list:
                 if song_info: # Kiểm tra xem info có hợp lệ không
                     song_info['requested_by'] = ctx.author # Luôn gán người yêu cầu
                     await state["queue"].put(song_info)
                     if first_song_info is None: first_song_info = song_info
                     added_count += 1

             if added_count == 0: # Nếu lọc ra không còn gì
                  await ctx.send(embed=self.create_guild_embed(ctx.guild.id, "🤷‍♀️ Không Thêm Được Bài Nào", "Không thể lấy thông tin hợp lệ cho bài hát được yêu cầu.", EMBED_COLOR_WARNING))
                  return 0

             # Tạo embed thông báo
             if added_count == 1 and first_song_info:
                 title = f"✅ Đã Thêm Vào Hàng Đợi"
                 desc = (f"**[{first_song_info['title']}]({first_song_info['webpage_url']})**\n"
                         f"`Thời lượng:` {first_song_info['duration']} | `Yêu cầu bởi:` {ctx.author.mention}")
                 embed_added = self.create_guild_embed(ctx.guild.id, title, desc, EMBED_COLOR_SUCCESS)
                 if first_song_info.get('thumbnail'):
                      embed_added.set_thumbnail(url=first_song_info['thumbnail'])
                 # Ước tính vị trí
                 queue_size = state["queue"].qsize() # Số bài trong queue trước khi task _play_next chạy và get()
                 if state.get("now_playing"): # Nếu có bài đang play/chuẩn bị play
                    position = queue_size # Vị trí là cuối hàng đợi (vì chưa lấy ra)
                 else: # Nếu hàng đợi trống và không có gì đang chạy
                    position = 1 # Bài này sẽ là bài đầu tiên
                 embed_added.set_footer(text=f"Vị trí: #{position} trong hàng đợi | {embed_added.footer.text}", icon_url=embed_added.footer.icon_url)
             else: # Thêm nhiều bài (playlist)
                 embed_added = self.create_guild_embed(ctx.guild.id, "➕ Đã Thêm Playlist/Nhiều Bài", f"Đã thêm thành công **{added_count}** bài hát vào hàng đợi theo yêu cầu của {ctx.author.mention}.", EMBED_COLOR_SUCCESS)
                 queue_size = state["queue"].qsize()
                 embed_added.set_footer(text=f"Tổng số bài trong hàng đợi: {queue_size} | {embed_added.footer.text}", icon_url=embed_added.footer.icon_url)

             await ctx.send(embed=embed_added)

             # Kiểm tra nếu không có gì đang phát/chuẩn bị phát VÀ bot đang ở trong kênh thoại
             # => Bắt đầu chu trình phát nhạc
             vc = state.get("voice_client")
             current_task = state.get("playback_task")
             is_task_running = current_task and not current_task.done()
             is_playing_or_paused = vc and (vc.is_playing() or vc.is_paused())

             # print(f"DEBUG [{ctx.guild.id}]: Checking start playback: is_task_running={is_task_running}, is_playing_or_paused={is_playing_or_paused}")

             if vc and not is_task_running and not is_playing_or_paused:
                 # print(f"DEBUG [{ctx.guild.id}]: Starting playback from queue addition.")
                 state["playback_task"] = self.bot.loop.create_task(self._play_next(ctx.guild.id)) # Khởi chạy task _play_next

             return added_count

    async def _fetch_playlist_entries(self, url: str) -> List[Dict]:
         """Lấy danh sách entry cơ bản từ URL playlist."""
         loop = asyncio.get_event_loop()
         ydl_opts_playlist = YDL_OPTIONS.copy()
         ydl_opts_playlist['noplaylist'] = False # Cho phép đọc playlist
         ydl_opts_playlist['extract_flat'] = True # Lấy nhanh info cơ bản
         ydl_opts_playlist['playlistend'] = 50 # Giới hạn số lượng entry đọc từ API (ví dụ 50)

         entries = []
         # print(f"Fetching playlist entries for: {url}")
         try:
              with yt_dlp.YoutubeDL(ydl_opts_playlist) as ydl:
                   playlist_info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
                   if playlist_info and 'entries' in playlist_info:
                         for entry in playlist_info.get('entries', []):
                            if entry and entry.get('url') and entry.get('_type', 'video') == 'video': # Chỉ lấy video entries hợp lệ
                                 duration_s = entry.get('duration')
                                 if duration_s is not None:
                                     try: duration_s = int(duration_s)
                                     except ValueError: duration_s = 0
                                 else: duration_s = 0
                                 duration_str = str(timedelta(seconds=duration_s)) if duration_s > 0 else "N/A"
                                 entries.append({
                                     'title': entry.get('title', 'Không rõ tiêu đề'),
                                     # Quan trọng: dùng 'url' từ entry (là webpage url với extract_flat)
                                     'webpage_url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}",
                                     'duration': duration_str,
                                     'duration_s': duration_s,
                                     'thumbnail': entry.get('thumbnail'), # Thường là None với extract_flat
                                     'id': entry.get('id'),
                                     # 'stream_url': None # Không có với extract_flat
                                     'uploader': entry.get('uploader', 'Không rõ'),
                                     # 'requested_by' sẽ được gán sau
                                })
         except yt_dlp.utils.DownloadError as e:
              print(f"yt-dlp Playlist DownloadError for '{url}': {e}")
              # Trả về list rỗng hoặc raise lỗi tùy theo muốn xử lý thế nào
         except Exception as e:
              print(f"!!! Unhandled Exception in _fetch_playlist_entries for '{url}': {e}")
              traceback.print_exc()
         # print(f"Finished fetching playlist, got {len(entries)} entries.")
         return entries


    # --- 🎶 LỆNH CHÍNH 🎶 ---

    @commands.command(name='play', aliases=['p'], help='Phát nhạc từ link YouTube/tìm kiếm. Thêm vào cuối hàng đợi.')
    async def play(self, ctx: commands.Context, *, query: str):
        """Phát nhạc từ URL/search. Xử lý playlist. Thêm vào hàng đợi."""
        state = self.get_guild_state(ctx.guild.id)
        # Không cần lock ở đây vì các hàm con (ensure_voice, fetch, handle_queue) đã có lock nếu cần

        voice_client = await self._ensure_voice(ctx)
        if not voice_client: return # Đã gửi lỗi trong _ensure_voice

        is_url = query.startswith(('http://', 'https://'))
        is_playlist = is_url and ('list=' in query or 'playlist' in query.lower())

        if is_playlist:
             # Xử lý Playlist
             processing_msg = await ctx.send(embed=self.create_guild_embed(ctx.guild.id, "⏳ Xử Lý Playlist", f"Đang phân tích playlist: `{query}`...\nViệc này có thể mất một lúc tùy độ dài playlist.", color=EMBED_COLOR_WARNING))
             playlist_entries = await self._fetch_playlist_entries(query)
             try: # Xóa tin nhắn processing sau khi có kết quả
                 await processing_msg.delete()
             except discord.NotFound: pass # Không sao nếu tin nhắn bị xóa bởi người dùng

             if not playlist_entries:
                  await ctx.send(embed=self.create_guild_embed(ctx.guild.id, "🤷‍♀️ Playlist Trống?", "Không tìm thấy bài hát hợp lệ nào trong playlist hoặc link không đúng.", EMBED_COLOR_WARNING))
                  return

             # Thêm các entry vào hàng đợi
             await self._handle_queue_addition(ctx, playlist_entries)

        else:
             # Xử lý Link video đơn / Từ khóa tìm kiếm
             processing_msg = await ctx.send(embed=self.create_guild_embed(ctx.guild.id, "🔎 Đang Xử Lý...", f"`{query}`", EMBED_COLOR_INFO))
             song_info = await self._fetch_song_info(query, ctx.author) # Truyền ctx.author vào đây
             try: # Xóa tin nhắn processing
                 await processing_msg.delete()
             except discord.NotFound: pass

             if not song_info:
                 await ctx.send(embed=self.create_guild_embed(ctx.guild.id, "❌ Không Tìm Thấy", f"Rất tiếc, không tìm thấy kết quả nào cho: `{query}`", EMBED_COLOR_ERROR))
                 return

             # Thêm bài hát vào hàng đợi (hàm này sẽ tự xử lý embed và start playback nếu cần)
             await self._handle_queue_addition(ctx, [song_info]) # Đưa vào list 1 phần tử

    @commands.command(name='search', help='Tìm kiếm 5 bài hát và cho phép chọn.')
    async def search(self, ctx: commands.Context, *, query: str):
        """Tìm kiếm bài hát và hiển thị lựa chọn."""
        state = self.get_guild_state(ctx.guild.id)

        voice_client = await self._ensure_voice(ctx)
        if not voice_client: return # Lỗi đã được gửi

        searching_embed = self.create_guild_embed(ctx.guild.id, "🕵️‍♀️ Đang Tìm Kiếm...", f"Từ khóa: `{query}`", EMBED_COLOR_WARNING)
        searching_msg = await ctx.send(embed=searching_embed)

        results = await self._fetch_search_results(query, max_results=5) # Lấy tối đa 5 kết quả

        if not results:
             await searching_msg.edit(embed=self.create_guild_embed(ctx.guild.id, "🤷‍♀️ Không Tìm Thấy", f"Không có kết quả tìm kiếm nào cho `{query}`.", EMBED_COLOR_WARNING), view=None) # view=None để xóa select cũ nếu edit lại
             return

        # --- Tạo Select Menu (Yêu cầu discord.py v2.0+) ---
        options = []
        select_desc = "Chọn một bài bằng cách nhấn vào menu thả xuống:\n\n"
        for i, res in enumerate(results, 1):
             title = res['title'][:85] + '...' if len(res['title']) > 85 else res['title'] # Giới hạn ký tự title
             duration = res['duration']
             uploader = res.get('uploader', 'N/A')[:10] + "..." if len(res.get('uploader', 'N/A')) > 10 else res.get('uploader', 'N/A') # Giới hạn ký tự desc
             # Value sẽ là index của bài hát trong list results
             options.append(discord.SelectOption(label=f"{i}. {title}", description=f"[{duration}] - {uploader}" , value=str(i-1)))
             # Thêm vào description của embed để người dùng thấy list dễ hơn
             select_desc += f"`{i}.` [{title}]({res['webpage_url']}) `[{duration}]`\n"


        # --- Class Select Menu View ---
        # Cần kế thừa từ discord.ui.View
        class SearchView(discord.ui.View):
            def __init__(self, search_results, guild_state, music_cog, original_ctx, timeout=45.0):
                super().__init__(timeout=timeout)
                self.results = search_results
                self.state = guild_state
                self.cog = music_cog # Tham chiếu tới MusicCog để gọi hàm helper
                self.original_ctx = original_ctx # Lưu context gốc
                self.selection_made = asyncio.Event() # Dùng Event để chờ hoặc timeout

            @discord.ui.select(
                placeholder="Chọn một bài hát từ kết quả tìm kiếm...",
                min_values=1,
                max_values=1,
                options=options # Truyền các option đã tạo
            )
            async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
                # Chỉ người dùng ban đầu mới được tương tác
                if interaction.user != self.original_ctx.author:
                     await interaction.response.send_message("Chỉ người yêu cầu tìm kiếm mới được chọn nhé!", ephemeral=True)
                     return

                # --- Lựa chọn đã được thực hiện ---
                self.selection_made.set() # Báo hiệu đã chọn
                # Vô hiệu hóa Select Menu để không chọn lại được nữa
                select.disabled = True
                # Xóa các thành phần khác nếu có (ví dụ: nút cancel)
                # self.clear_items() # Hoặc chỉ disable nút chọn

                await interaction.response.defer() # Tạm dừng phản hồi để xử lý thêm

                selected_index = int(select.values[0])
                chosen_song_basic_info = self.results[selected_index]

                # *** Fetch full info ngay trước khi thêm vào queue ***
                full_info = await self.cog._fetch_song_info(chosen_song_basic_info['webpage_url'], interaction.user)

                if not full_info:
                     # Edit tin nhắn gốc báo lỗi
                      await interaction.edit_original_response(content=f"🚫 Lỗi khi lấy thông tin chi tiết cho:\n`{chosen_song_basic_info['title']}`\nVui lòng thử lại hoặc tìm kiếm bài khác.", embed=None, view=None)
                      return # Dừng xử lý

                # Thêm bài hát vào hàng đợi qua hàm helper (đã bao gồm lock và start play)
                await self.cog._handle_queue_addition(self.original_ctx, [full_info])

                # Edit tin nhắn search ban đầu để chỉ hiển thị thông báo thành công thay vì kết quả + select nữa
                # Lấy embed từ hàm handle_queue_addition sẽ báo thêm thành công rồi, nên chỉ cần xóa view ở đây
                # Embed báo thành công được gửi riêng bởi _handle_queue_addition
                try:
                     #await interaction.edit_original_response(content=f"✅ Đã chọn: **{full_info['title']}**", embed=None, view=None)
                     # Tốt hơn là xóa luôn view trên tin nhắn gốc, để embed thành công từ handle_queue_addition nổi bật
                      await interaction.edit_original_response(view=None)
                      # Tin nhắn handle_queue_addition sẽ được gửi bởi chính hàm đó
                except discord.NotFound: pass # Có thể tin nhắn đã bị xóa

                self.stop() # Dừng hẳn view này

            # Override on_timeout
            async def on_timeout(self):
                 if not self.selection_made.is_set(): # Chỉ timeout nếu chưa chọn
                      try:
                            # Chỉnh sửa tin nhắn gốc báo hết giờ và xóa View
                            timeout_embed = self.cog.create_guild_embed(self.original_ctx.guild.id, "⌛ Hết Giờ Lựa Chọn", "Bạn đã không chọn bài hát nào.", EMBED_COLOR_WARNING)
                            await self.original_ctx.message.edit(embed=timeout_embed, view=None) # Edit tin nhắn gốc của lệnh !search
                      except discord.NotFound:
                           pass # Tin nhắn có thể đã bị xóa
                      except Exception as e:
                           print(f"Error editing message on timeout: {e}")
                 # Tự động dừng view khi timeout hoặc chọn xong
                 self.stop()

        view = SearchView(search_results=results, guild_state=state, music_cog=self, original_ctx=ctx)

        result_embed = self.create_guild_embed(ctx.guild.id, f"🔍 Kết Quả Tìm Kiếm ({len(results)}): `{query}`", select_desc, EMBED_COLOR_MUSIC)
        #result_embed.set_footer(text=f"Chọn trong {view.timeout} giây | Yêu cầu bởi {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        result_embed.set_footer(text=f"Chọn trong {view.timeout:.0f} giây | {result_embed.footer.text}", icon_url=result_embed.footer.icon_url)

        # Gửi tin nhắn kèm View
        await searching_msg.edit(embed=result_embed, view=view)

        # Chờ cho đến khi view timeout hoặc có lựa chọn
        # await view.wait() -> Không cần chờ ở đây vì logic đã nằm trong callback và timeout


    @commands.command(name='skip', aliases=['s'], help='Bỏ qua bài hát hiện tại.')
    async def skip(self, ctx: commands.Context):
        """Bỏ qua bài hát hiện tại."""
        state = self.get_guild_state(ctx.guild.id)
        async with state["lock"]:
             voice_client = state.get("voice_client")
             now_playing = state.get("now_playing") # Lấy bài đang phát để hiện tên

             if not voice_client or not voice_client.is_playing(): # Chỉ skip khi đang is_playing()
                 await ctx.send(embed=self.create_guild_embed(ctx.guild.id, "🔇 Không Có Gì Để Skip", "Bot hiện không phát bài nào cả.", EMBED_COLOR_WARNING))
                 return

             skipped_song_title = f"`{now_playing['title']}`" if now_playing else "bài hát hiện tại"

             # Dừng bài hiện tại. Hàm `after` trong voice_client.play SẼ TỰ ĐỘNG gọi _play_next
             # print(f"DEBUG [{ctx.guild.id}]: Skipping song...")
             voice_client.stop() # <-- Chỉ cần dòng này
             # await asyncio.sleep(0.1) # Chờ 1 chút để hệ thống xử lý stop nếu cần (thường không cần)

             # await ctx.message.add_reaction("⏭️") # Phản hồi nhanh bằng reaction
             await ctx.send(embed=self.create_guild_embed(ctx.guild.id, "⏭️ Đã Bỏ Qua", f"{ctx.author.mention} đã bỏ qua {skipped_song_title}.", EMBED_COLOR_INFO))

             # Không cần gọi _play_next thủ công ở đây. Callback 'after' của bài hát vừa stop sẽ lo việc đó.
             # Nó sẽ thấy queue (hoặc loop) và tự động bắt đầu bài tiếp theo.

    @commands.command(name='stop', aliases=['leave', 'disconnect', 'dc'], help='Dừng nhạc, xóa hàng đợi và rời kênh.')
    async def stop(self, ctx: commands.Context):
        """Dừng nhạc, xóa hàng đợi và rời kênh."""
        state = self.get_guild_state(ctx.guild.id)
        guild_id = ctx.guild.id

        async with state["lock"]: # Lock để đảm bảo dọn dẹp hoàn chỉnh
            voice_client = state.get("voice_client") # Nên lấy từ state đã lưu

            if not voice_client or not voice_client.is_connected():
                 await ctx.send(embed=self.create_guild_embed(guild_id, "🤷‍♀️ Không Ở Trong Kênh", "Kaguya hiện không ở trong kênh thoại nào.", EMBED_COLOR_INFO))
                 return

            original_channel_name = voice_client.channel.name if voice_client.channel else "kênh thoại"

            # 1. Dừng playback hiện tại (nếu có)
            if voice_client.is_playing() or voice_client.is_paused():
                 # print(f"DEBUG [{guild_id}]: Stopping playback for stop command.")
                 voice_client.stop() # Gọi stop sẽ kích hoạt 'after', nhưng queue rỗng nên ko làm gì
                 state["now_playing"] = None

            # 2. Cancel task playback đang chờ (nếu có, đề phòng race condition)
            if state.get("playback_task") and not state["playback_task"].done():
                 # print(f"DEBUG [{guild_id}]: Cancelling existing playback task.")
                 state["playback_task"].cancel()
                 try:
                     await state["playback_task"] # Chờ cancel xong (không bắt buộc)
                 except asyncio.CancelledError:
                     pass # Chuyện bình thường khi cancel
            state["playback_task"] = None

            # 3. Xóa hàng đợi
            queue_size_before_clear = state["queue"].qsize()
            while not state["queue"].empty():
                 try: state["queue"].get_nowait()
                 except asyncio.QueueEmpty: break
            # print(f"DEBUG [{guild_id}]: Cleared {queue_size_before_clear} songs from queue.")

            # 4. Ngắt kết nối khỏi kênh thoại
            # print(f"DEBUG [{guild_id}]: Disconnecting from voice channel.")
            try:
                await voice_client.disconnect(force=False) # force=False cho ngắt kết nối mềm
                await ctx.send(embed=self.create_guild_embed(guild_id, "👋 Tạm Biệt!", f"Đã dừng nhạc, xóa hàng đợi và rời khỏi `{original_channel_name}` theo yêu cầu của {ctx.author.mention}.", EMBED_COLOR_SUCCESS))
            except Exception as e:
                 await ctx.send(embed=self.create_guild_embed(guild_id, "🚫 Lỗi Ngắt Kết Nối", f"Có lỗi khi rời kênh: `{e}`", EMBED_COLOR_ERROR))
                 traceback.print_exc()

            # 5. Dọn dẹp state hoàn toàn (quan trọng)
            # Reset các giá trị về mặc định hoặc xóa state của guild đi nếu muốn tiết kiệm bộ nhớ
            state["voice_client"] = None
            state["text_channel"] = None
            state["now_playing"] = None
            state["loop_mode"] = "off"
            state["volume"] = 0.5
            # Không cần xóa queue vì đã làm ở trên
            # Có thể xóa luôn guild_id khỏi self.guild_states nếu không dùng nữa
            # del self.guild_states[guild_id] (nhưng get_guild_state sẽ tạo lại)
            # print(f"DEBUG [{guild_id}]: Guild state cleaned.")

    @commands.command(name='queue', aliases=['q'], help='Hiển thị 10 bài hát đầu trong hàng đợi.')
    async def queue(self, ctx: commands.Context):
        """Hiển thị hàng đợi hiện tại (tối đa 10 bài + bài đang phát)."""
        state = self.get_guild_state(ctx.guild.id)
        guild_id = ctx.guild.id

        # Không cần lock mạnh ở đây, đọc snapshot là đủ
        queue_list = list(state["queue"]._queue)[:10] # Chỉ lấy 10 bài đầu
        full_queue_size = state["queue"].qsize()
        now_playing = state.get("now_playing") # Đây là bản sao lúc nó bắt đầu phát

        if not queue_list and not now_playing:
             await ctx.send(embed=self.create_guild_embed(guild_id, "🎶 Hàng Đợi Trống", "Không có bài hát nào được xếp hàng.", EMBED_COLOR_INFO))
             return

        embed = self.create_guild_embed(guild_id, "📜 Hàng Đợi Bài Hát", color=EMBED_COLOR_MUSIC)
        queue_description = ""
        total_duration_s = 0
        song_count = 0 # Đếm cả bài đang phát

        # Hiển thị bài đang phát (nếu có)
        if now_playing:
             song_count += 1
             title = now_playing['title'][:55] + '...' if len(now_playing['title']) > 55 else now_playing['title']
             duration = now_playing['duration']
             requester = now_playing.get('requested_by') # Có thể là None nếu bot tự động thêm?
             requester_mention = requester.mention if requester else "N/A"
             queue_description += f"**`▶️ Đang phát:`** [{title}]({now_playing['webpage_url']}) `[{duration}]` | YC: {requester_mention}\n\n"
             # Cộng duration của bài đang phát? Khó vì không biết còn bao nhiêu
             # Bỏ qua duration bài đang phát cho tổng thời gian

        # Hiển thị các bài trong hàng đợi
        if queue_list:
             queue_description += "**`⏳ Sắp phát:`**\n"
             for i, song in enumerate(queue_list, 1):
                 song_count += 1
                 title = song['title'][:55] + '...' if len(song['title']) > 55 else song['title']
                 duration = song['duration']
                 duration_s = song.get('duration_s', 0)
                 requester = song.get('requested_by')
                 requester_mention = requester.mention if requester else "N/A"
                 queue_description += f"`{i}.` [{title}]({song['webpage_url']}) `[{duration}]` | YC: {requester_mention}\n"
                 if isinstance(duration_s, (int, float)) and duration_s > 0:
                    total_duration_s += duration_s

             if full_queue_size > len(queue_list):
                 remaining = full_queue_size - len(queue_list)
                 queue_description += f"\n... và **{remaining}** bài hát khác."

        embed.description = queue_description.strip()

        footer_parts = []
        footer_parts.append(f"Tổng cộng: {full_queue_size + (1 if now_playing else 0)} bài")

        # Chỉ thêm tổng thời lượng nếu có bài trong queue thực sự
        if total_duration_s > 0:
             total_duration_str = str(timedelta(seconds=int(total_duration_s)))
             footer_parts.append(f"Thời lượng queue: ~{total_duration_str}")

        loop_mode = state.get('loop_mode', 'off')
        if loop_mode != 'off': footer_parts.append(f"🔁 Lặp: {loop_mode.capitalize()}")

        volume = state.get('volume', 0.5)
        footer_parts.append(f"🔊 Âm lượng: {int(volume*100)}%")


        footer_text = " | ".join(footer_parts)
        embed.set_footer(text=footer_text)


        await ctx.send(embed=embed)


    @commands.command(name='nowplaying', aliases=['np'], help='Hiển thị thông tin bài hát đang phát.')
    async def nowplaying(self, ctx: commands.Context):
        """Hiển thị chi tiết bài hát đang phát."""
        state = self.get_guild_state(ctx.guild.id)
        # Không cần lock vì chỉ đọc
        now_playing = state.get("now_playing")
        voice_client = state.get("voice_client") # ctx.voice_client cũng được

        if not voice_client or not now_playing:
            await ctx.send(embed=self.create_guild_embed(ctx.guild.id, "🔇 Chưa Phát Nhạc", "Hiện tại không có bài hát nào đang phát.", EMBED_COLOR_INFO))
            return

        # --- Tính toán thanh tiến trình (khá phức tạp và không hoàn toàn chính xác với stream) ---
        # FFmpegPCMAudio không cung cấp thời gian đã phát trực tiếp.
        # Cách tốt nhất là lưu thời điểm bắt đầu (state['start_time']) khi play()
        # Và tính delta time. Phải xử lý pause/resume phức tạp.
        # Hiện tại chỉ hiển thị thông tin cơ bản.

        embed = self.create_guild_embed(
              ctx.guild.id,
              f"🎶 Đang Phát",
              f"**[{now_playing['title']}]({now_playing['webpage_url']})**\n\n"
              f"`Thời lượng:` {now_playing['duration']}\n"
              f"`Người tải lên:` {now_playing.get('uploader', 'N/A')}\n"
              f"`Yêu cầu bởi:` {now_playing['requested_by'].mention if now_playing.get('requested_by') else 'N/A'}",
              EMBED_COLOR_MUSIC # Màu tím nhạc
         )
        if now_playing.get('thumbnail'):
              embed.set_thumbnail(url=now_playing['thumbnail'])

        # Thêm thông tin Loop & Volume vào footer
        footer_parts = []
        loop_mode = state.get('loop_mode', 'off')
        if loop_mode != 'off': footer_parts.append(f"🔁 Lặp: {loop_mode.capitalize()}")
        volume = state.get('volume', 0.5)
        footer_parts.append(f"🔊 Âm lượng: {int(volume*100)}%")

        if footer_parts:
             footer_text = " | ".join(footer_parts)
             # Lấy footer gốc từ create_guild_embed nếu có
             base_footer = embed.footer.text or "Powered by Kaguya's Logic 💫"
             embed.set_footer(text=f"{base_footer} | {footer_text}", icon_url=embed.footer.icon_url)
        # else: giữ footer gốc

        await ctx.send(embed=embed)


    @commands.command(name='pause', help='Tạm dừng bài hát hiện tại.')
    async def pause(self, ctx: commands.Context):
        state = self.get_guild_state(ctx.guild.id)
        vc = state.get("voice_client")
        if vc and vc.is_playing():
            vc.pause()
            await ctx.send(embed=self.create_guild_embed(ctx.guild.id, "⏸️ Tạm Dừng", f"Đã tạm dừng phát nhạc.", EMBED_COLOR_INFO))
            await ctx.message.add_reaction("⏸️")
        elif vc and vc.is_paused():
            await ctx.send(embed=self.create_guild_embed(ctx.guild.id, "🤔 Đã Tạm Dừng Rồi", f"Nhạc đang tạm dừng sẵn rồi mà.", EMBED_COLOR_WARNING))
        else:
            await ctx.send(embed=self.create_guild_embed(ctx.guild.id, "🔇 Chưa Phát Nhạc", "Không có gì để tạm dừng cả.", EMBED_COLOR_INFO))

    @commands.command(name='resume', help='Tiếp tục phát nhạc đã tạm dừng.')
    async def resume(self, ctx: commands.Context):
        state = self.get_guild_state(ctx.guild.id)
        vc = state.get("voice_client")
        if vc and vc.is_paused():
            vc.resume()
            await ctx.send(embed=self.create_guild_embed(ctx.guild.id, "▶️ Tiếp Tục Phát", f"Đã tiếp tục phát nhạc.", EMBED_COLOR_SUCCESS))
            await ctx.message.add_reaction("▶️")
        elif vc and vc.is_playing():
            await ctx.send(embed=self.create_guild_embed(ctx.guild.id, "🤔 Đang Phát Rồi", f"Nhạc đang phát mà, đâu có tạm dừng đâu.", EMBED_COLOR_WARNING))
        else:
             await ctx.send(embed=self.create_guild_embed(ctx.guild.id, "🔇 Chưa Phát Nhạc", "Không có gì để tiếp tục cả.", EMBED_COLOR_INFO))


    @commands.command(name='volume', aliases=['vol'], help='Đặt âm lượng (0-100).')
    @commands.cooldown(1, 5, commands.BucketType.guild) # Giới hạn tần suất đổi volume
    async def volume(self, ctx: commands.Context, *, vol: int = None):
        """Đặt âm lượng nhạc cho guild này."""
        state = self.get_guild_state(ctx.guild.id)
        guild_id = ctx.guild.id
        vc = state.get("voice_client")

        if vol is None:
            # Chỉ hiển thị âm lượng hiện tại
            current_vol_percent = int(state.get("volume", 0.5) * 100)
            await ctx.send(embed=self.create_guild_embed(guild_id, "🔊 Âm Lượng Hiện Tại", f"Âm lượng đang được đặt là **{current_vol_percent}%**.", EMBED_COLOR_INFO))
            return

        if not 0 <= vol <= 100:
            await ctx.send(embed=self.create_guild_embed(guild_id, "🚫 Giá Trị Không Hợp Lệ", "Âm lượng phải là một số từ 0 đến 100.", EMBED_COLOR_WARNING))
            return

        new_volume_float = vol / 100.0

        # Lưu giá trị mới vào state
        state["volume"] = new_volume_float

        # Nếu bot đang kết nối và có audio source, áp dụng ngay
        if vc and vc.source:
            # PCMVolumeTransformer quản lý source gốc
            if isinstance(vc.source, discord.PCMVolumeTransformer):
                vc.source.volume = new_volume_float
                # print(f"DEBUG [{guild_id}]: Applied volume {new_volume_float} directly to PCMVolumeTransformer.")
            else:
                # Trường hợp source không phải là PCMVolumeTransformer (lạ)
                # print(f"WARNING [{guild_id}]: Voice source is not PCMVolumeTransformer, cannot set volume directly.")
                pass # Không làm gì nếu source không hỗ trợ

        elif vc: # Đang kết nối nhưng chưa phát gì / chưa có source
            # Âm lượng mới sẽ được áp dụng khi bài hát tiếp theo bắt đầu (do _play_next đọc từ state)
            # print(f"DEBUG [{guild_id}]: VC connected but no source, volume {new_volume_float} will be applied on next play.")
             pass


        await ctx.send(embed=self.create_guild_embed(guild_id, "🔊 Đặt Âm Lượng", f"Đã đặt âm lượng thành **{vol}%**.", EMBED_COLOR_SUCCESS))
        await ctx.message.add_reaction("🔊")


    @commands.command(name='loop', help='Thay đổi chế độ lặp (off/song/queue). Không ghi gì để xem.')
    async def loop(self, ctx: commands.Context, mode: str = None):
        """Chuyển đổi hoặc xem chế độ lặp: off, song, queue."""
        state = self.get_guild_state(ctx.guild.id)
        guild_id = ctx.guild.id
        valid_modes = ["off", "song", "queue", "0", "1", "2"] # Chấp nhận cả số cho tiện
        mode_map = {"0": "off", "1": "song", "2": "queue"}
        current_mode = state.get("loop_mode", "off")

        if mode is None:
            # Chỉ hiển thị mode hiện tại
            await ctx.send(embed=self.create_guild_embed(guild_id, "🔁 Trạng Thái Lặp", f"Chế độ lặp hiện tại: **`{current_mode.capitalize()}`**.", EMBED_COLOR_INFO))
            return

        mode_lower = mode.lower()
        # Ánh xạ số sang chữ nếu cần
        resolved_mode = mode_map.get(mode_lower, mode_lower)

        if resolved_mode not in ["off", "song", "queue"]: # Check các giá trị chữ chuẩn
            await ctx.send(embed=self.create_guild_embed(guild_id, "🚫 Sai Chế Độ", f"Chế độ lặp không hợp lệ. Dùng: `off`, `song`, `queue` (hoặc 0, 1, 2).", EMBED_COLOR_WARNING))
            return

        # --- Thực hiện thay đổi ---
        async with state["lock"]: # Lock khi thay đổi state
             state["loop_mode"] = resolved_mode
        await ctx.send(embed=self.create_guild_embed(guild_id, "✅ Cập Nhật Chế Độ Lặp", f"Đã đổi chế độ lặp thành: **`{resolved_mode.capitalize()}`**.", EMBED_COLOR_SUCCESS))
        await ctx.message.add_reaction("🔁")

    # --- Xử lý lỗi chung cho Cog ---
    # Tên hàm chuẩn là `cog_command_error`
    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
         """Xử lý lỗi xảy ra trong các lệnh của Cog Âm Nhạc."""
         guild_id = ctx.guild.id if ctx.guild else "DM"

         # Bỏ qua các lỗi thường gặp không cần thông báo nhiều
         ignored = (commands.CommandNotFound, commands.UserInputError, commands.CheckFailure, commands.NotOwner, commands.MissingPermissions)
         if isinstance(error, ignored):
              return

         # Lỗi Cooldown
         if isinstance(error, commands.CommandOnCooldown):
             retry_after = timedelta(seconds=int(error.retry_after))
             await ctx.send(embed=self.create_guild_embed(guild_id, "⏳ Bình tĩnh nào...", f"Lệnh này đang trong thời gian chờ. Thử lại sau **{retry_after}**.", EMBED_COLOR_WARNING), delete_after=10)
             return

         # Lỗi Thiếu Argument
         if isinstance(error, commands.MissingRequiredArgument):
             param = error.param.name
             await ctx.send(embed=self.create_guild_embed(guild_id, "🤔 Thiếu Gì Đó?", f"Cậu quên cung cấp `{param}` cho lệnh này rồi.", EMBED_COLOR_WARNING))
             # Có thể gửi ctx.command.help ở đây
             return

         # Nếu là lỗi gốc từ command (CommandInvokeError) -> lấy lỗi gốc ra
         original_error = getattr(error, 'original', error)

         # Các lỗi đặc biệt có thể xử lý riêng (ví dụ lỗi API key, ...)
         # if isinstance(original_error, MyCustomAPIError):
         #     await ctx.send("...")
         #     return

         # Log lỗi không mong muốn ra console để debug
         print(f'!!! Unhandled Error in command {ctx.command} (Guild: {guild_id}): {original_error}')
         traceback.print_exception(type(original_error), original_error, original_error.__traceback__)

         # Thông báo lỗi chung cho người dùng
         error_name = type(original_error).__name__
         await ctx.send(embed=self.create_guild_embed(guild_id, "💥 Ôi Không! Có Lỗi Xảy Ra!", f"Đã có sự cố khi thực hiện lệnh `{ctx.invoked_with}`.\n```\n{error_name}: {original_error}\n```\nKaguya đã ghi nhận lại rồi.", EMBED_COLOR_ERROR))


# --- 🚀 KAGUYA BOOT SEQUENCE 🚀 ---
bot = commands.Bot(
    command_prefix=COMMAND_PREFIX,
    intents=intents,
    help_command=commands.DefaultHelpCommand(dm_help=None),
    case_insensitive=True
)

@bot.event
async def on_ready():
    print('------< INFO >------')
    print(f'✨ Kaguya đã đăng nhập với tên: {bot.user.name}')
    print(f'✨ ID: {bot.user.id}')
    print(f'✨ Prefix: {COMMAND_PREFIX}')
    connected_guilds = len(bot.guilds)
    print(f'✨ Đã kết nối tới {connected_guilds} servers')
    
    if bot.user.avatar:
        if isinstance(bot.user.avatar, str):
            avatar_url = f"https://cdn.discordapp.com/avatars/{bot.user.id}/{bot.user.avatar}.png"
        else:
            avatar_url = bot.user.avatar.url
        print(f'✨ Avatar URL: {avatar_url}')
    else:
        print('✨ Bot không có avatar.')
    
    print('------< LOADING COGS >------')
    try:
        print("✅ Cog [MusicCog] đã được tải thành công!")
    except Exception as e:
        print(f"❌ Lỗi khi tải Cog [MusicCog]: {e}")
        traceback.print_exc()

    print('------< BOT READY >------')
    activity = discord.Activity(type=discord.ActivityType.listening, name=f"{COMMAND_PREFIX}help | Trong {connected_guilds} servers")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"✨ Kaguya đã sẵn sàng phục vụ! ✨")

# Thêm MusicCog vào bot
bot.add_cog(MusicCog(bot))

# --- Chạy Bot ---
if __name__ == "__main__":
    if DISCORD_TOKEN == "YOUR_BOT_TOKEN_IN_ENV_FILE" or not DISCORD_TOKEN:
        print("⛔ LỖI NGHIÊM TRỌNG: Không tìm thấy DISCORD_TOKEN!")
        print("👉 Hãy kiểm tra biến môi trường hoặc tạo file .env cùng cấp với bot.py.")
        print("👉 Trong file .env, thêm dòng: DISCORD_TOKEN='TOKEN_BOT_CUA_BAN'")
    else:
        print("🚀 Kaguya đang khởi động...")
        try:
            bot.run(DISCORD_TOKEN)
        except discord.errors.LoginFailure:
            print("⛔ LỖI LOGIN: Token không hợp lệ. Hãy kiểm tra lại token trong Discord Developer Portal.")
        except discord.errors.PrivilegedIntentsRequired:
             print("⛔ LỖI INTENTS: Bot yêu cầu các quyền Intents chưa được bật!")
             print("👉 Vào Discord Developer Portal -> Application -> Bot")
             print("👉 Bật các mục trong phần 'Privileged Gateway Intents':")
             print("   - PRESENCE INTENT (Có thể không cần thiết cho bot nhạc cơ bản)")
             print("   - SERVER MEMBERS INTENT (Có thể không cần thiết cho bot nhạc cơ bản)")
             print("   - ✅ MESSAGE CONTENT INTENT (!!! RẤT CẦN THIẾT !!!)")
             print("👉 Lưu ý: Nếu bot trên 100 server, bạn cần xin duyệt các intent này.")
        except ImportError as e:
             print(f"⛔ LỖI IMPORT: Thiếu thư viện cần thiết: {e}")
             print("👉 Hãy chạy lệnh: pip install -r requirements.txt (nếu có file requirements)")
             print("👉 Hoặc cài thủ công: pip install discord.py[voice] yt-dlp python-dotenv")
        except Exception as e:
            print(f"💥 Lỗi không xác định khi chạy bot: {e}")
            traceback.print_exc()
