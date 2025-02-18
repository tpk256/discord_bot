import subprocess
import asyncio
import random
import time
from urllib.parse import urlparse, parse_qs


import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp


from db import db

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'extract_audio': True,
            'audio_format': 'mp3',
            'outtmpl': 'temp_audio.%(ext)s'
        }


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot

        self.voice_client = None
        self.playlist = None
        self.__cache = {}

    async def play_next(self):
        try:
            song_url = next(self.playlist)
            print(song_url)
        except StopIteration:
            self.playlist = None
            self.voice_client = None
        else:
            try:
                self.voice_client.play(

                    discord.FFmpegPCMAudio(song_url, **FFMPEG_OPTIONS),
                    after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop)  # executable=r"C:\ffmpeg\bin\ffmpeg.exe"
                )
            except Exception as e:
                print(e)

    def _gen_songs(self, songs):
        for song in songs:
            yield song

    @app_commands.command(name="play_playlist")
    async def play_playlist(self, interaction: discord.Interaction, playlist_name: str):
        __is_cache = False

        for _, _, name_play, play_id in db.get_playlists(interaction.guild.id):
            if playlist_name == name_play:
                __songs_cached = self.__cache.get(playlist_name)
                print(self.__cache)
                if __songs_cached is not None:
                    print("Кеш не нлуь")
                    if __songs_cached.get("expired") > time.time():
                        self.playlist = self._gen_songs(__songs_cached["songs"])
                        __is_cache = True
                        break

                self.playlist = db.get_songs_by_playlist(play_id)
                break

        print("ok")
        print(self.playlist)
        if self.playlist is None:
            await interaction.response.send_message("Такого плейлиста не существует")
            return

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

        self.voice_client = interaction.guild.voice_client

        if __is_cache:
            await self.play_next()
            return

        __songs = []
        for _, url, _ in self.playlist:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            __songs.append(info["url"])
        # print(self.__cache, "before")
        self.__cache[playlist_name] = {
            "expired": time.time() + 3600,
            "songs": __songs
        }
        # print(self.__cache, "after")
        self.playlist = self._gen_songs(__songs)
        await self.play_next()

    @app_commands.command(name="create_playlist")
    async def create_playlist(self, interaction: discord.Interaction, name_playlist: str, *, songs_url: str):
        songs = []
        await interaction.response.send_message("Создаю playlist")
        songs = songs_url.split()
        #
        try:
            if not songs:
                await interaction.followup.send("Введены некоректные urls")
                return

            play_id = random.randint(0, 10**10) % 10**6
            db.add_playlist(
                channel_id=interaction.guild.id,
                name_playlist=name_playlist,
                playlist_id=play_id
            )
            for url in songs:
                db.add_song(url, play_id)
            await interaction.followup.send(f"Плейлист под названием {name_playlist} успешно создан")
        except Exception as e:
            print(e)


    @app_commands.command(name="skip", description="Пропустить текущую песню")
    async def skip(self, interaction: discord.Interaction):

        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()  # Останавливаем воспроизведение
            if self.playlist:
                voice_client.stop()
                await self.play_next()
                await interaction.response.send_message("⏩ Песня в плейлисте пропущена!")
            else:

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

        url = urlparse(запрос)

        if url.scheme not in ("http", "https"):
            await interaction.followup.send_message("Введен некоректный url")
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




