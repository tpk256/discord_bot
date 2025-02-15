import subprocess
import asyncio
from urllib.parse import urlparse, parse_qs


import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp


FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(name="play", description="Поиск музыки по url")
    @app_commands.describe(запрос="url")
    async def play(self, interaction: discord.Interaction, запрос: str):

        ctx: commands.Context = await commands.Context.from_interaction(interaction)

        if ctx.author.voice is None:
            await interaction.response.send_message("Вам нужно зайти в голосовой канал!"); return
        elif ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
        elif ctx.voice_client.channel != ctx.author.voice.channel:
            await ctx.voice_client.move_to(ctx.author.voice.channel)

        url = urlparse(запрос)
        if url.hostname == "www.youtube.com":
            query_params = parse_qs(url.query)
            v = query_params.get("v", [None])[0]
            if v is not None:
                url = f"https://www.youtube.com/watch?v={v}"
        else:
            url = запрос
        print(url)
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'extract_audio': True,
            'audio_format': 'mp3',
            'outtmpl': 'temp_audio.%(ext)s'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info["url"]
        vc = ctx.voice_client
        print(vc)
        if vc.is_playing():
            await interaction.response.send_message("❌ Уже играет другая музыка!")
            return
        print(vc.is_playing())
        try:
            source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)
        except Exception as exp:
            print(exp, "ERROR")
            await interaction.response.send_message(f"Error {exp}")
        else:
            await interaction.response.send_message(f"🎶 Сейчас играет: **{info['title']}**")
            vc.play(source)


