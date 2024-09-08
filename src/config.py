import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.hh.ru"
DB_NAME = os.getenv("DB_NAME", "").strip()
DB_USER = os.getenv("DB_USER", "").strip()
DB_PASSWORD = os.getenv("DB_PASSWORD", "").strip()
DB_HOST = os.getenv("DB_HOST", "").strip()
DB_PORT = os.getenv("DB_PORT", "").strip()

# Проверка наличия всех необходимых переменных
if not all([DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT]):
    raise ValueError("Не все необходимые переменные окружения установлены.")

print(f"Connecting to database: {DB_NAME} on {DB_HOST}:{DB_PORT}")
