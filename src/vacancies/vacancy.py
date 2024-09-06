from typing import Dict, NamedTuple, Optional, Union


class SalaryRange(NamedTuple):
    salary_from: int
    salary_to: int


class Vacancy:
    def __init__(
        self,
        name: str,
        url: str,
        salary: Optional[SalaryRange],  # Делаем salary опциональным
        description: str,
    ):
        self.name = name
        self.url = url
        self.salary = salary
        self.description = description

    def _get_numeric_salary(self) -> Optional[int]:
        """Возвращает числовую зарплату (from) или None."""
        if self.salary:
            if isinstance(self.salary.salary_from, int):
                return self.salary.salary_from
            elif (
                isinstance(self.salary.salary_from, str)
                and self.salary.salary_from.isdigit()
            ):
                return int(self.salary.salary_from)
        return None

    def to_dict(self) -> Dict[str, Union[str, Optional[SalaryRange], Dict[str, int]]]:
        salary_dict = None
        if self.salary:
            salary_dict = {
                "salary_from": self.salary.salary_from,
                "salary_to": self.salary.salary_to,
            }
        return {
            "name": self.name,
            "url": self.url,
            "salary": salary_dict,
            "description": self.description,
        }

    @staticmethod
    def from_dict(data: Dict[str, Union[str, Dict[str, int]]]) -> "Vacancy":
        salary_data = data.get("salary")
        salary = None
        if salary_data:
            salary = SalaryRange(
                salary_from=salary_data["salary_from"],
                salary_to=salary_data["salary_to"],
            )
        return Vacancy(
            name=data.get("name", "Неизвестно"),
            url=data.get("url", ""),
            salary=salary,
            description=data.get("description", "Нет описания"),
        )

    def __repr__(self) -> str:
        return f"Vacancy(name={self.name}, url={self.url}, salary={self.salary}, description={self.description})"
