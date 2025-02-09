import asyncio
from datetime import datetime
from sqlalchemy import or_, select, update
from aiogram import Bot
from core.config import get_settings
from db.db import get_session
from db.tasks import Task

settings = get_settings()
bot = Bot(token=settings.telegram_api_key)
CHAT_ID = settings.telegram_chat_id 


async def check_and_notify_tasks():
    async with get_session() as session:
        # Select tasks where notify_at is due and not yet notified 
        stmt = select(Task).where(
            (
                Task.notify_at <= datetime.now(),
                Task.notify_status == False
            )
        )
        
        result = await session.execute(stmt)
        tasks = result.scalars().all()
        print(f"Tasks due: {tasks}")
        for task in tasks:
            # Send a message to the user
            await bot.send_message(CHAT_ID, f"Task due: {task.title}")
            
            # Update the notify_status
            stmt = update(Task).where(Task.id == task.id).values(notify_status=True)
            await session.execute(stmt)
        await session.commit()
        

async def scheduler_loop():
    while True:
        await check_and_notify_tasks()
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(scheduler_loop())