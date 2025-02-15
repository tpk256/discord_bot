import subprocess
import asyncio

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

    @app_commands.command(name="skip", description="Пропустить текущую песню")
    async def skip(self, interaction: discord.Interaction):
        print(12312321)
        ctx: commands.Context = await commands.Context.from_interaction(interaction)
        print(1)
        if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()  # Останавливает воспроизведение
            await interaction.response.send_message("⏩ Песня пропущена, и я отключился от канала!")
            await interaction.guild.voice_client.disconnect()  # Отключаем бота
        else:
            await interaction.response.send_message("❌ Сейчас нет песни для пропуска!")

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


        url = запрос
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
        print(audio_url)
        print(12312312312312)
        vc = ctx.voice_client
        print(vc)
        try:
            source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)
            # source = discord.FFmpegPCMAudio(audio_url, executable="C:/ffmpeg/bin/ffmpeg.exe",  **FFMPEG_OPTIONS)
        except Exception as exp:
            print(exp)
        print(source)
        print(vc, source)
        if not vc.is_playing():
            vc.play(source)
            await ctx.send(f"🎶 Сейчас играет: **{info['title']}**")
        else:
            await ctx.send("❌ Уже играет другая музыка!")