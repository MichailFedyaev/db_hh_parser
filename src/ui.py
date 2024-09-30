import psycopg2

from src.api import HH
from src.config import config
from src.db_creater import DBCreater
from src.db_manager import DBManager
from src.db_updater import DBUpdater
from src.utils import read_json


def main_ui() -> None:
    """Основная структура взаимодействия с пользователем"""

    print("Здравствуйте! Это программа для парсинга вакансий с сайта hh.ru")
    params = config()
    db_name = "hh_parser"
    print(f"Параметры сервера базы данных загружены. Имя БД: {db_name}, хост: {params["host"]}")

    if check_db(db_name, params):
        print("База данных существует и содержит информацию о вакансиях в следующих компаниях:")
        print_db_data(db_name, params)
        print("Хотите пересоздать базу и загрузить актуальные данные о компаниях и вакансиях с сайта hh.ru?")
        answer = input("Введите Да или ничего не вводите: ")
        if answer.lower() == "да":
            create_db(db_name, params)
            print_db_data(db_name, params)

    else:
        input("Нажмите Enter для начала загрузки данных о компаниях и вакансиях с сайта hh.ru и сохранения их в БД ")
        create_db(db_name, params)
        print_db_data(db_name, params)

    print()
    db = DBManager(db_name, params)
    while True:
        print("Вам доступны следующие возможности:")
        print("1. Получить список всех вакансий")
        print("2. Получить среднюю зарплату по вакансиям")
        print("3. Получить список всех вакансий, у которых зарплата выше средней по всем вакансиям")
        print("4. Получить список всех вакансий, в названии которых содержатся определенное слово")
        choice = input("Введите номер требуемого действия от 1 до 4: ")
        match choice:
            case "1":
                vacancies = db.get_all_vacancies()
                print_vacancies(vacancies)

            case "2":
                print(db.get_avg_salary())
                print()

            case "3":
                vacancies = db.get_vacancies_with_higher_salary()
                print_vacancies(vacancies)

            case "4":
                keyword = input("Введите слово для поиска: ")
                vacancies = db.get_vacancies_with_keyword(keyword)
                print_vacancies(vacancies)

            case _:
                continue

        stop_word = input(
            "Введите слово СТОП, чтобы завершить работу с программой или ничего не вводите, чтобы продолжить: "
        )
        if stop_word.lower() == "стоп":
            break


def check_db(db_name: str, params: dict) -> bool:
    """Проверка наличия базы данных"""

    try:
        db = DBManager(db_name, params)
        db.get_employers()
        return True
    except psycopg2.OperationalError:
        return False


def create_db(db_name: str, params: dict) -> None:
    """Создать или пересоздать БД и наполнить данными"""

    db = DBCreater(db_name, params)
    db.create_database()
    db.create_tables()
    print("БД создана")

    file_with_companies = "data/companies_settings.json"
    companies = read_json(file_with_companies)
    print(f"Получен перечень компаний для загрузки вакансий из файла {file_with_companies}")

    employers = []
    vacancies = []

    for company in companies:
        print(f"Загрузка данных о вакансиях для компании: {company["name"]}")
        employers.append(HH.load_employer_data(company["id"]))
        vacancies.extend(HH.load_vacancies(company["id"]))

    print()
    print("Данные успешно загружены")

    db_updater = DBUpdater(db_name, params)
    db_updater.insert_data(employers, vacancies)

    print("Данные успешно внесены в БД")


def print_db_data(db_name: str, params: dict) -> None:
    """Вывод данных о содержимом БД"""

    db = DBManager(db_name, params)
    companies = db.get_companies_and_vacancies_count()
    print()
    print("Название компании       Количество вакансий в БД")
    for company in companies:
        print(f"{company["company_name"]:<23}", company["vacancies_count"])
    print()


def print_vacancies(vacancies: list) -> None:
    """Вывод данных о вакансиях"""

    print("Название компании  Название вакансии", " " * 35, "Зарплата ОТ   Зарплата ДО   Ссылка на вакансию")
    for i in range(len(vacancies)):
        vacancy = vacancies[i]
        company = vacancy["company_name"]
        name = vacancy["vacancy_name"]
        salary_from = "Не указана" if vacancy["salary_from"] == 0 else vacancy["salary_from"]
        salary_to = "Не указана" if vacancy["salary_to"] == 0 else vacancy["salary_to"]
        url = vacancy["url"]
        print(
            f"{company:<15}", "  ", f"{name[0:50]:<50}", "  ", f"{str(salary_from):<13}", f"{str(salary_to):<13}", url
        )
        if (i + 1) % 10 == 0:
            print()
            print("Название компании  Название вакансии", " " * 35, "Зарплата ОТ   Зарплата ДО   Ссылка на вакансию")
            print()
    print()