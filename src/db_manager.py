from typing import Any

import psycopg2


class DBManager:
    """Класс для получения данных о вакансиях из базы данных"""

    def __init__(self, db_name: str, params: dict) -> None:
        """Инициализируем базу данных"""

        self.__db_name = db_name
        self.__params = params

    def __query_execute(self, query: str) -> list[dict | Any]:
        """Метод для выполнения запроса"""

        with psycopg2.connect(dbname=self.__db_name, **self.__params) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                columns = [column[0] for column in cur.description]
                result = cur.fetchall()
                result_in_dict = [dict(zip(columns, i)) for i in result]

        conn.close()

        return result_in_dict

    def get_employers(self) -> Any:
        """Получить данные о работодателях из БД"""

        return self.__query_execute("SELECT * FROM employers")

    def get_companies_and_vacancies_count(self) -> Any:
        """Получает список всех компаний и количество вакансий у каждой компании"""

        query = """
            SELECT employers.company_name, COUNT(*) AS vacancies_count
            FROM vacancies
            JOIN employers USING(employer_id)
            GROUP BY employers.company_name
            """

        return self.__query_execute(query)

    def get_all_vacancies(self) -> Any:
        """Получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию
        """

        query = """
            SELECT employers.company_name, vacancy_name, salary_from, salary_to, url
            FROM vacancies
            JOIN employers USING(employer_id)
            """

        return self.__query_execute(query)

    def get_avg_salary(self) -> Any:
        """Получает среднюю зарплату по вакансиям"""

        query = """
            SELECT AVG (salary_from)
            FROM vacancies
            WHERE salary_to > 0
            """

        return round(self.__query_execute(query)[0]["avg"], 2)

    def get_vacancies_with_higher_salary(self) -> Any:
        """Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям"""

        query = """
            SELECT employers.company_name, vacancy_name, salary_from, salary_to, url
            FROM vacancies
            JOIN employers USING(employer_id)
            WHERE salary_from > (
            SELECT AVG (salary_from)
            FROM vacancies
            WHERE salary_to > 0
            )
            """

        return self.__query_execute(query)

    def get_vacancies_with_keyword(self, text: str) -> Any:
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова, например python"""

        query = f"""
            SELECT employers.company_name, vacancy_name, salary_from, salary_to, url
            FROM vacancies
            JOIN employers USING(employer_id)
            WHERE vacancy_name LIKE '%{text}%'
            """

        return self.__query_execute(query)
