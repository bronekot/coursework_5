import psycopg2
from psycopg2 import sql
from typing import List, Dict, Any, Optional
from src.abstract_classes.abstract_classes import AbstractDBManager
from src.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


class DBManager(AbstractDBManager):
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT companies.name, COUNT(vacancies.id) as vacancy_count
                FROM companies
                LEFT JOIN vacancies ON companies.id = vacancies.company_id
                GROUP BY companies.id
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
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS companies (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL
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
                    url TEXT NOT NULL
                )
            """
            )
        self.conn.commit()

    def insert_company(self, name: str) -> int:
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO companies (name) VALUES (%s) RETURNING id", (name,)
            )
            company_id = cur.fetchone()[0]
        self.conn.commit()
        return company_id

    def insert_vacancy(
        self,
        company_id: int,
        name: str,
        salary_from: Optional[int],
        salary_to: Optional[int],
        url: str,
    ):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO vacancies (company_id, name, salary_from, salary_to, url) VALUES (%s, %s, %s, %s, %s)",
                (company_id, name, salary_from, salary_to, url),
            )
        self.conn.commit()

    def __del__(self):
        if hasattr(self, "conn"):
            self.conn.close()
