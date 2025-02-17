import asyncio
import random

import discord
from discord.ext import commands

from cogs import music, start

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot("!", intents=intents,)


@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен!")
    try:
        synced = await bot.tree.sync()
        print(f"Синхронизировано {len(synced)} команд")
    except Exception as e:
        print(f"Ошибка синхронизации: {e}")


async def main():
    async with bot:
        await bot.add_cog(start.Start(bot))
        await bot.add_cog(music.Music(bot))
        await bot.start('here token')


asyncio.run(main())

