import psycopg2


class DBCreater:
    """Класс для создания базы данных"""

    def __init__(self, db_name: str, params: dict) -> None:
        """Инициализируем базу данных"""

        self.__db_name = db_name
        self.__params = params

    def create_database(self) -> None:
        """Создать базу данных"""

        conn = psycopg2.connect(dbname="postgres", **self.__params)
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(
            f"""SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{self.__db_name}' AND pid <> pg_backend_pid()"""
        )
        cur.execute(f"DROP DATABASE IF EXISTS {self.__db_name}")
        cur.execute(f"CREATE DATABASE {self.__db_name}")
        conn.close()

    def create_tables(self) -> None:
        """Создание таблиц для работодателей и вакансий"""

        conn = psycopg2.connect(dbname=self.__db_name, **self.__params)
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE employers(
            employer_id INT PRIMARY KEY,
            company_name VARCHAR,
            open_vacancies INT,
            accredited_it_employer BOOL,
            site_url VARCHAR,
            description TEXT
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE vacancies(
            vacancy_id INT PRIMARY KEY,
            employer_id INT,
            vacancy_name VARCHAR,
            salary_from INT,
            salary_to INT,
            url VARCHAR,
            CONSTRAINT fk_vacancies_employer FOREIGN KEY (employer_id) REFERENCES employers(employer_id)
            )
            """
        )

        conn.close()