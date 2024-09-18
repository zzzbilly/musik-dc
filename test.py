import discord 
from discord.ext import commands
import yt_dlp as youtube_dl  # Mengganti youtube_dl dengan yt_dlp
import asyncio

# Inisialisasi bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Konfigurasi untuk yt_dlp
ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': 'True',
    'quiet': True
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# Fungsi untuk mengambil audio dari YouTube
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url']
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

# Perintah untuk memainkan lagu
@bot.command(name='play', help='Play a song from YouTube')
async def play(ctx, url):
    try:
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()

        async with ctx.typing():
            player = await YTDLSource.from_url(url)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

            # Update status aktivitas bot
            await bot.change_presence(activity=discord.Game(name=f'Now playing: {player.title}'))

        await ctx.send(f'Now playing: {player.title}')
    except AttributeError:
        await ctx.send("You need to be in a voice channel to play music.")

# Token bot
TOKEN = 'MTI4MzY1NjQyMjA1MTE1MTkwMw.GQoVSQ.yYCKrHekgGswqfugKxc-JKKa0HSqEztyz5vNMY'

# Menjalankan bot
bot.run(TOKEN)
