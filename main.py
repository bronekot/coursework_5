from src.api.hh_api import HeadHunterAPI
from src.database.db_manager import DBManager
from src.vacancies.vacancy import Vacancy
import logging

logging.basicConfig(level=logging.INFO)


def main():
    # Инициализация API и БД
    hh_api = HeadHunterAPI()

    try:
        # Инициализация базы данных и DBManager
        db_manager = DBManager.initialize_database()
    except Exception as e:
        print(f"Не удалось инициализировать базу данных: {e}")
        return

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
        print(f"Обработка вакансий компании {company}...")
        vacancies = hh_api.get_vacancies(company, per_page=100, page=0)
        company_id = db_manager.insert_company(company)
        for vacancy in vacancies:
            db_manager.insert_vacancy(
                company_id=company_id,
                hh_vacancy_id=vacancy.hh_vacancy_id,
                name=vacancy.name,
                salary=vacancy.salary,
                url=vacancy.url,
            )
        print(f"Обработано {len(vacancies)} вакансий для компании {company}")

    # Запуск пользовательского интерфейса
    user_interface(db_manager)


def user_interface(db_manager: DBManager):
    while True:
        print("\nВыберите действие:")
        print(
            "1. Получить список всех компаний и количество вакансий у каждой компании"
        )
        print("2. Получить список всех вакансий")
        print("3. Получить среднюю зарплату по вакансиям")
        print("4. Получить список вакансий с зарплатой выше средней")
        print("5. Поиск вакансий по ключевому слову")
        print("0. Выход")

        choice = input("Введите номер действия: ")

        if choice == "1":
            companies = db_manager.get_companies_and_vacancies_count()
            for company in companies:
                print(f"{company['company']}: {company['vacancy_count']} вакансий")
        elif choice == "2":
            vacancies = db_manager.get_all_vacancies()
            for vacancy in vacancies[:10]:  # Показываем только первые 10 для краткости
                print(f"{vacancy['company']} - {vacancy['vacancy']}")
                print(
                    f"Зарплата: от {vacancy['salary_from']} до {vacancy['salary_to']}"
                )
                print(f"URL: {vacancy['url']}\n")
            print(f"Показано 10 из {len(vacancies)} вакансий")
        elif choice == "3":
            avg_salary = db_manager.get_avg_salary()
            print(f"Средняя зарплата: {avg_salary:.2f}")
        elif choice == "4":
            vacancies = db_manager.get_vacancies_with_higher_salary()
            for vacancy in vacancies[:10]:  # Показываем только первые 10 для краткости
                print(f"{vacancy['company']} - {vacancy['vacancy']}")
                print(
                    f"Зарплата: от {vacancy['salary_from']} до {vacancy['salary_to']}"
                )
                print(f"URL: {vacancy['url']}\n")
            print(f"Показано 10 из {len(vacancies)} вакансий с зарплатой выше средней")
        elif choice == "5":
            keyword = input("Введите ключевое слово для поиска: ")
            vacancies = db_manager.get_vacancies_with_keyword(keyword)
            for vacancy in vacancies:
                print(f"{vacancy['company']} - {vacancy['vacancy']}")
                print(
                    f"Зарплата: от {vacancy['salary_from']} до {vacancy['salary_to']}"
                )
                print(f"URL: {vacancy['url']}\n")
            print(f"Найдено {len(vacancies)} вакансий с ключевым словом '{keyword}'")
        elif choice == "0":
            print("Спасибо за использование программы. До свидания!")
            break
        else:
            print("Неверный выбор. Пожалуйста, выберите число от 0 до 5.")


if __name__ == "__main__":
    main()
