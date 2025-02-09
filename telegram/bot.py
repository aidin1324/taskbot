import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.exceptions import TelegramForbiddenError
from collections import defaultdict
from core.config import get_settings
from builder import multi_agentic_graph

settings = get_settings()
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=settings.telegram_api_key)
dp = Dispatcher()  # No bot passed here

# Хранилище истории чатов в памяти
chat_histories = defaultdict(list)
MAX_HISTORY = 10  # Максимальное количество сообщений в истории

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я Taskbot в Telegram. Отправь мне сообщение, и я помогу тебе организовать задачи.")

@dp.message()
async def handle_message(message: types.Message):
    """
    При получении сообщения от пользователя отправляем его в наш workflow, получаем ответ и отсылаем обратно.
    """
    thread_id = message.chat.id

    # Добавляем сообщение пользователя в историю
    user_msg = {"role": "user", "content": message.text}
    chat_histories[thread_id].append(user_msg)

    # Обрезаем историю до MAX_HISTORY
    chat_histories[thread_id] = chat_histories[thread_id][-MAX_HISTORY:]

    # Формируем текущий state
    state = {"messages": chat_histories[thread_id].copy()}
    config = {"configurable": {"thread_id": thread_id}}

    try:
        # Запускаем асинхронный вызов multi_agentic_graph
        response = await multi_agentic_graph.ainvoke(state, config)

        # Добавляем ответ ассистента в историю
        if "messages" in response:
            assistant_msg = response["messages"][-1]
            chat_histories[thread_id].append(assistant_msg)

            # Отправляем ответ пользователю
            await message.reply(assistant_msg.content, parse_mode="Markdown")

    except TelegramForbiddenError:
        # Если бот не может отправить сообщение, логируем ошибку.
        logging.error("Не удалось отправить сообщение пользователю.")
    except Exception as e:
        logging.exception(f"Ошибка при обработке сообщения: {e}")
        await message.reply(f"Произошла ошибка: {str(e)}", parse_mode="Markdown")




async def start_bot():
        try:
            logging.info("Запуск бота Taskbot в Telegram")
            # Pass the bot instance here
            await dp.start_polling(bot)
        finally:
            await bot.session.close()
            
# testing
# if __name__ == "__main__":
#     asyncio.run(start_bot())