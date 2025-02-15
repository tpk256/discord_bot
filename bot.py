import asyncio

import discord
from discord.ext import commands

from cogs import music, start

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot("/", intents=intents,)


@bot.command(name="skip", description="Пропустить текущую песню")
async def skip(ctx: commands.Context):

    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()  # Останавливаем воспроизведение
        await ctx.send("⏩ Песня пропущена!")
        await voice_client.disconnect()
    else:
        await ctx.send("❌ Сейчас нет песни для пропуска!")


@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен!")
    bot.tree.clear_commands()
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

