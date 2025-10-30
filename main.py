import asyncio
from core import BotApp

async def main():
    bot = BotApp()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
