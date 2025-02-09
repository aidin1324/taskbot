from telegram.bot import start_bot

from db.scheduler import scheduler_loop

import asyncio

if __name__ == "__main__":
    async def main():
        asyncio.create_task(scheduler_loop())
        await start_bot()
    asyncio.run(main())