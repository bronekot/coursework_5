import requests
from requests.exceptions import RequestException
from src.abstract_classes.abstract_classes import AbstractAPI
from config import BASE_URL
from typing import List, Optional
import logging

# Import the Vacancy class (assuming it's in the same directory)
from .vacancy import Vacancy

logging.basicConfig(level=logging.INFO)


class HeadHunterAPI(AbstractAPI):
    """
    Класс для взаимодействия с API HeadHunter.
    """

    def __init__(self):
        """
        Инициализация HeadHunterAPI.
        """
        self.base_url = BASE_URL
        self.headers = {"User-Agent": "HH-User-Agent"}

    def get_vacancies(self, query: str, per_page: int, page: int) -> List[Vacancy]:
        """
        Получить список вакансий по запросу.

        Аргументы:
            query (str): Запрос для поиска вакансий.
            per_page (int): Количество вакансий на странице.
            page (int): Номер страницы для получения.

        Возвращает:
            List[Vacancy]: Список вакансий.
        """
        params = {"text": query, "per_page": per_page, "page": page}
        try:
            response = requests.get(
                f"{self.base_url}/vacancies", headers=self.headers, params=params
            )
            response.raise_for_status()  # Проверяем на ошибки HTTP
            data = response.json()

            vacancies_data = data.get("items", [])
            vacancies = [
                Vacancy.from_dict(vacancy_data) for vacancy_data in vacancies_data
            ]

            logging.info(f"Получено {len(vacancies)} вакансий для запроса '{query}'.")
            return vacancies

        except RequestException as e:
            logging.error(f"Ошибка при получении вакансий: {e}")
            return []  # Возвращаем пустой список в случае ошибки
