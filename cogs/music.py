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

    @app_commands.command(name="skip", description="Пропустить текущую песню")
    async def skip(self, interaction: discord.Interaction):

        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()  # Останавливаем воспроизведение
            await voice_client.disconnect()
            await interaction.response.send_message("⏩ Песня пропущена!")
            return

        await interaction.response.send_message("❌ Сейчас нет песни для пропуска!")

    @app_commands.command(name="play", description="Поиск музыки по url")
    @app_commands.describe(запрос="url")
    async def play(self, interaction: discord.Interaction, запрос: str):
        user = interaction.user
        voice_client = interaction.guild.voice_client

        if user.voice is None:
            await interaction.response.send_message("Вам нужно зайти в голосовой канал!")
            return
        elif voice_client is None:
            await user.voice.channel.connect()
        elif user.voice.channel != voice_client.channel:
            await voice_client.move_to(user.voice.channel)

        if voice_client and voice_client.is_playing():
            await interaction.response.send_message("❌ Уже играет другая музыка!")
            return

        await interaction.response.send_message("Начинаю искать музыку")
        url = urlparse(запрос)

        if url.scheme not in ("http", "https"):
            await interaction.response.send_message("Введен некоректный url")
            return

        if url.hostname == "www.youtube.com":
            query_params = parse_qs(url.query)
            v = query_params.get("v", [None])[0]
            if v is not None:
                url = f"https://www.youtube.com/watch?v={v}"
        else:
            url = запрос
        print(url)
        await interaction.response.send_message("Начинаю искать музыку")
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

        print(voice_client)
        voice_client = interaction.guild.voice_client
        if voice_client.is_playing():
            await interaction.followup.send("❌ Уже играет другая музыка!")
            return
        print(voice_client.is_playing())
        try:
            source = discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)
            print(source)
        except Exception as exp:
            print(exp, "ERROR")
            await interaction.followup.send(f"Error {exp}")
        else:
            await interaction.followup.send(f"🎶 Сейчас играет: **{info['title']}**")
            voice_client.play(source)




