import discord
from discord.ext import commands
from discord import app_commands


class Start(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Бот {self.bot.user} запущен!")
        self.bot.tree.clear_commands()
        try:
            synced = await self.bot.tree.sync()
            print(f"Синхронизировано {len(synced)} команд")
        except Exception as e:
            print(f"Ошибка синхронизации: {e}")
