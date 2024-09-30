from typing import Any

import requests


class HH:
    """Класс для работы с API HeadHunter"""

    @staticmethod
    def __connection_to_api(api_method: str, api_params: dict) -> Any:
        """Приватный метод для подключения к API"""

        url = f"https://api.hh.ru/{api_method}"
        headers = {"User-Agent": "HH-User-Agent"}

        response = requests.get(url, headers=headers, params=api_params)

        if response.status_code != 200:
            print()
            print(f"---{api_method} --- {api_params} --- не выполнен")
            print(response.status_code)
        return response

    @classmethod
    def load_vacancies(cls, employer_id: str) -> list:
        """Метод для получения вакансий по ID работодателя"""

        params = {"employer_id": employer_id, "page": 0, "per_page": 100, "area": 2}
        vacancies = []

        print("Загрузка данных ... ", end="")
        while params.get("page") != 20:
            print("#", end="")

            try:
                vacancies_page = cls.__connection_to_api("vacancies", params).json()["items"]
                if not vacancies_page:
                    break
                vacancies.extend(vacancies_page)
                # print(type(vacancies), len(vacancies))
            except KeyError:
                pass

            params["page"] += 1

        print()
        return vacancies

    @classmethod
    def load_employer_data(cls, employer_id: str) -> Any:
        """Метод для получения данных о работодателях"""

        params: dict = {}

        employer_data = cls.__connection_to_api(f"employers/{employer_id}", params).json()

        return employer_data
