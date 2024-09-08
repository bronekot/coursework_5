from typing import Dict, NamedTuple, Optional, Union, Any


class SalaryRange(NamedTuple):
    salary_from: Optional[int]
    salary_to: Optional[int]


class Vacancy:
    """
    Класс, представляющий вакансию.

    Attributes:
        hh_vacancy_id (str): Уникальный идентификатор вакансии на HeadHunter.
        name (str): Название вакансии.
        url (str): URL вакансии.
        salary (Optional[SalaryRange]): Диапазон зарплаты, если указан.
        description (str): Описание вакансии.
    """

    def __init__(
        self,
        hh_vacancy_id: str,
        name: str,
        url: str,
        salary: Optional[SalaryRange],
        description: str,
    ):
        """
        Инициализирует объект Vacancy.

        Args:
            hh_vacancy_id (str): Уникальный идентификатор вакансии на HeadHunter.
            name (str): Название вакансии.
            url (str): URL вакансии.
            salary (Optional[SalaryRange]): Диапазон зарплаты, если указан.
            description (str): Описание вакансии.
        """
        self.hh_vacancy_id = hh_vacancy_id
        self.name = name
        self.url = url
        self.salary = salary
        self.description = description

    def _get_numeric_salary(self) -> Optional[int]:
        """
        Возвращает числовую зарплату (from) или None.

        Returns:
            Optional[int]: Числовое значение зарплаты или None, если зарплата не указана.
        """
        if self.salary and self.salary.salary_from:
            return int(self.salary.salary_from)
        return None

    def to_dict(self) -> Dict[str, Union[str, Optional[Dict[str, Optional[int]]]]]:
        """
        Преобразует объект Vacancy в словарь.

        Returns:
            Dict[str, Union[str, Optional[Dict[str, Optional[int]]]]]: Словарь с данными вакансии.
        """
        salary_dict = None
        if self.salary:
            salary_dict = {
                "salary_from": self.salary.salary_from,
                "salary_to": self.salary.salary_to,
            }
        return {
            "hh_vacancy_id": self.hh_vacancy_id,
            "name": self.name,
            "url": self.url,
            "salary": salary_dict,
            "description": self.description,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Vacancy":
        """
        Создает объект Vacancy из словаря.

        Args:
            data (Dict[str, Any]): Словарь с данными вакансии.

        Returns:
            Vacancy: Объект вакансии.
        """
        salary_data = data.get("salary")
        salary = None
        if salary_data:
            salary = SalaryRange(
                salary_from=salary_data.get("from"), salary_to=salary_data.get("to")
            )
        return Vacancy(
            hh_vacancy_id=str(data.get("id")),
            name=data.get("name", "Неизвестно"),
            url=data.get("alternate_url", ""),
            salary=salary,
            description=data.get("snippet", {}).get("requirement", "Нет описания"),
        )

    def __repr__(self) -> str:
        """
        Возвращает строковое представление объекта Vacancy.

        Returns:
            str: Строковое представление вакансии.
        """
        return f"Vacancy(name={self.name}, url={self.url}, salary={self.salary}, description={self.description})"
