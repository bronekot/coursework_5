import psycopg2
from psycopg2 import sql
from typing import List, Dict, Any, Optional
from src.abstract_classes.abstract_classes import AbstractDBManager
from src.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
from src.vacancies.vacancy import SalaryRange


class DBManager(AbstractDBManager):
    def __init__(self):
        self.conn = self.connect_to_db()

    @classmethod
    def initialize_database(cls):
        """Инициализирует базу данных и создает необходимые таблицы."""
        cls.create_database()
        instance = cls()
        instance.create_tables()
        return instance

    @staticmethod
    def create_database():
        """Создает базу данных, если она не существует."""
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
            )
            conn.autocommit = True
            cursor = conn.cursor()

            cursor.execute(
                "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_NAME,)
            )
            exists = cursor.fetchone()
            if not exists:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME))
                )
                print(f"База данных {DB_NAME} успешно создана.")
            else:
                print(f"База данных {DB_NAME} уже существует.")
        except psycopg2.Error as e:
            print(f"Ошибка при создании базы данных: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def connect_to_db():
        try:
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
            )
            print("Успешное подключение к базе данных.")
            return conn
        except psycopg2.Error as e:
            print(f"Не удалось подключиться к базе данных. Ошибка: {e}")
            raise

    @staticmethod
    def create_tables(conn):
        """Создает таблицы, если они еще не существуют."""
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS companies (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE
                )
            """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS vacancies (
                    id SERIAL PRIMARY KEY,
                    company_id INTEGER REFERENCES companies(id),
                    name VARCHAR(255) NOT NULL,
                    salary_from INTEGER,
                    salary_to INTEGER,
                    url TEXT NOT NULL,
                    hh_vacancy_id VARCHAR(20) UNIQUE
                )
            """
            )
        conn.commit()
        print("Таблицы успешно созданы или уже существуют.")

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT companies.name, COUNT(vacancies.id) as vacancy_count
                FROM companies
                LEFT JOIN vacancies ON companies.id = vacancies.company_id
                GROUP BY companies.id, companies.name
                ORDER BY companies.name
                """
            )
            return [
                {"company": row[0], "vacancy_count": row[1]} for row in cur.fetchall()
            ]

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT companies.name, vacancies.name, vacancies.salary_from, vacancies.salary_to, vacancies.url
                FROM vacancies
                JOIN companies ON companies.id = vacancies.company_id
            """
            )
            return [
                {
                    "company": row[0],
                    "vacancy": row[1],
                    "salary_from": row[2],
                    "salary_to": row[3],
                    "url": row[4],
                }
                for row in cur.fetchall()
            ]

    def get_avg_salary(self) -> float:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2)
                FROM vacancies
                WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
            """
            )
            result = cur.fetchone()[0]
            return float(result) if result is not None else 0.0

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        avg_salary = self.get_avg_salary()
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT companies.name, vacancies.name, vacancies.salary_from, vacancies.salary_to, vacancies.url
                FROM vacancies
                JOIN companies ON companies.id = vacancies.company_id
                WHERE (COALESCE(vacancies.salary_from, 0) + COALESCE(vacancies.salary_to, 0)) / 2 > %s
            """,
                (avg_salary,),
            )
            return [
                {
                    "company": row[0],
                    "vacancy": row[1],
                    "salary_from": row[2],
                    "salary_to": row[3],
                    "url": row[4],
                }
                for row in cur.fetchall()
            ]

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT companies.name, vacancies.name, vacancies.salary_from, vacancies.salary_to, vacancies.url
                FROM vacancies
                JOIN companies ON companies.id = vacancies.company_id
                WHERE vacancies.name ILIKE %s
            """,
                (f"%{keyword}%",),
            )
            return [
                {
                    "company": row[0],
                    "vacancy": row[1],
                    "salary_from": row[2],
                    "salary_to": row[3],
                    "url": row[4],
                }
                for row in cur.fetchall()
            ]

    def create_tables(self):
        with self.conn.cursor() as cur:
            # Создание таблицы companies
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS companies (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL
                )
            """
            )

            # Создание таблицы vacancies
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS vacancies (
                    id SERIAL PRIMARY KEY,
                    company_id INTEGER REFERENCES companies(id),
                    name VARCHAR(255) NOT NULL,
                    salary_from INTEGER,
                    salary_to INTEGER,
                    url TEXT NOT NULL
                )
            """
            )

            # Проверка наличия столбца hh_vacancy_id и его добавление, если он отсутствует
            cur.execute(
                """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='vacancies' AND column_name='hh_vacancy_id'
                """
            )
            if cur.fetchone() is None:
                cur.execute(
                    """
                    ALTER TABLE vacancies
                    ADD COLUMN hh_vacancy_id VARCHAR(20) UNIQUE
                    """
                )
                print("Столбец hh_vacancy_id добавлен в таблицу vacancies.")

        self.conn.commit()

    def insert_company(self, name: str) -> int:
        with self.conn.cursor() as cur:
            # Проверяем, существует ли уже компания
            cur.execute("SELECT id FROM companies WHERE name = %s", (name,))
            existing_company = cur.fetchone()
            if existing_company:
                return existing_company[0]
            else:
                # Если компании нет, вставляем новую
                cur.execute(
                    "INSERT INTO companies (name) VALUES (%s) RETURNING id", (name,)
                )
                company_id = cur.fetchone()[0]
                self.conn.commit()
                return company_id

    def insert_vacancy(
        self,
        company_id: int,
        hh_vacancy_id: str,
        name: str,
        salary: Optional[SalaryRange],
        url: str,
    ):
        with self.conn.cursor() as cur:
            # Проверяем, существует ли уже вакансия с таким hh_vacancy_id
            cur.execute(
                "SELECT id FROM vacancies WHERE hh_vacancy_id = %s", (hh_vacancy_id,)
            )
            existing_vacancy = cur.fetchone()

            if existing_vacancy:
                # Если вакансия существует, обновляем её
                cur.execute(
                    """
                    UPDATE vacancies 
                    SET company_id = %s, name = %s, salary_from = %s, salary_to = %s, url = %s
                    WHERE hh_vacancy_id = %s
                    """,
                    (
                        company_id,
                        name,
                        salary.salary_from if salary else None,
                        salary.salary_to if salary else None,
                        url,
                        hh_vacancy_id,
                    ),
                )
                print(f"Обновлена существующая вакансия: {name}")
            else:
                # Если вакансии нет, вставляем новую
                cur.execute(
                    """
                    INSERT INTO vacancies (company_id, hh_vacancy_id, name, salary_from, salary_to, url) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        company_id,
                        hh_vacancy_id,
                        name,
                        salary.salary_from if salary else None,
                        salary.salary_to if salary else None,
                        url,
                    ),
                )
                print(f"Добавлена новая вакансия: {name}")
            self.conn.commit()
