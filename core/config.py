from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    telegram_api_key = os.getenv("TELEGRAM_API_KEY")
    database_url = os.getenv("DATABASE_URL")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

def get_settings():
    return Config()