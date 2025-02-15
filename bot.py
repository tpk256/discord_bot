import asyncio

import discord
from discord.ext import commands

from cogs import music, start

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot("/", intents=intents,)


async def main():
    async with bot:
        await bot.add_cog(start.Start(bot))
        await bot.add_cog(music.Music(bot))
        await bot.start('HERE TOKEN')


asyncio.run(main())

