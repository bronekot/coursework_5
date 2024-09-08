from abc import ABC, abstractmethod
from typing import List, Dict, Any


class AbstractDBManager(ABC):
    @abstractmethod
    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """Получает список всех компаний и количество вакансий у каждой компании."""

    @abstractmethod
    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """Получает список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию."""

    @abstractmethod
    def get_avg_salary(self) -> float:
        """Получает среднюю зарплату по вакансиям."""

    @abstractmethod
    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям."""

    @abstractmethod
    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова, например python."""


class AbstractAPI(ABC):
    @abstractmethod
    def get_vacancies(self, query: str, per_page: int, page: int) -> List[Any]:
        """Получает список вакансий от API."""
