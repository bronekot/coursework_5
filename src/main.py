from src.api.hh_api import HeadHunterAPI
from src.database.db_manager import DBManager
from src.vacancies.vacancy import Vacancy
import logging

logging.basicConfig(level=logging.INFO)


def main():
    # Инициализация API и БД
    hh_api = HeadHunterAPI()
    db_manager = DBManager()

    # Создание таблиц в БД
    db_manager.create_tables()

    # Список интересующих компаний
    companies = [
        "Яндекс",
        "Google",
        "Mail.ru Group",
        "Сбербанк-Технологии",
        "Тинькофф",
        "VK",
        "Ozon",
        "Авито",
        "Касперский",
        "EPAM",
    ]

    # Получение и сохранение данных о вакансиях
    for company in companies:
        vacancies = hh_api.get_vacancies(company, per_page=100, page=0)
        company_id = db_manager.insert_company(company)
        for vacancy in vacancies:
            salary_from = vacancy.salary.salary_from if vacancy.salary else None
            salary_to = vacancy.salary.salary_to if vacancy.salary else None
            db_manager.insert_vacancy(
                company_id, vacancy.name, salary_from, salary_to, vacancy.url
            )

    # Демонстрация работы методов DBManager
    print("Компании и количество вакансий:")
    print(db_manager.get_companies_and_vacancies_count())

    print("\nВсе вакансии:")
    print(db_manager.get_all_vacancies())

    print(f"\nСредняя зарплата: {db_manager.get_avg_salary()}")

    print("\nВакансии с зарплатой выше средней:")
    print(db_manager.get_vacancies_with_higher_salary())

    print("\nВакансии с ключевым словом 'Python':")
    print(db_manager.get_vacancies_with_keyword("Python"))


if __name__ == "__main__":
    main()
