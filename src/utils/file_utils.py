import os
from dotenv import load_dotenv
from typing import Dict


def load_config() -> Dict[str, str]:
    """
    Загружает конфигурационные данные из файла .env

    Returns:
        Dict[str, str]: Словарь с конфигурационными данными
    """
    load_dotenv()

    return {
        "DB_NAME": os.getenv("DB_NAME"),
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_PORT": os.getenv("DB_PORT"),
        "BASE_URL": os.getenv("BASE_URL", "https://api.hh.ru"),
    }
