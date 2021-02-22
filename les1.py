"""
Задача организовать сбор данных, необходимо иметь метод сохранения данных в .json файлы результат:
Данные скачиваются с источника, при вызове метода/функции сохранения в файл скачанные данные сохраняются
в Json файлы, для каждой категории товаров должен быть создан отдельный файл и содержать
товары исключительно соответсвующие данной категории.
пример структуры данных для файла:

{
"name": "имя категории",
"code": "Код соответсвующий категории (используется в запросах)",
"products": [{PRODUCT},  {PRODUCT}........] # список словарей товаров соответсвующих данной категории
}
"""

import time
import json
from pathlib import Path
import requests

class Parse5Ka:
    headers = {

        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 "
                      "(X11; Ubuntu; Linux x86_64; rv:85.0) "
                      "Gecko/20100101 Firefox/85.0",
    }

    def __init__(self, start_url: str, products_path: Path):
        self.start_url = start_url
        self.products_path = products_path

    def _get_response(self, url):
        """
            Функция делает запрос по определенному url.
        """
        time_sleep_counts = 0
        while True:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response
            elif response.status_code != 200:
                time_sleep_counts += 1
                print(response.status_code)
                if time_sleep_counts == 3:
                    break
                else:
                    time.sleep(0.5)

    def run(self):
        """
            Функция иницирует старт и запускает методы класса в цикле.
        """
        for product in self._parse(self.start_url):
            product_path = self.products_path.joinpath(f"{product['id']}.json")
            self._save(product, product_path)

    def _parse(self, url):
        """
            Функция разбирает по полученному url ответ используя генератор, когда страница заканчивается
            иницирует переход на следующую страницу и так пока url не станет none.
        """
        while url:
            response = self._get_response(url)
            data = response.json()
            url = data["next"]
            for product in data["results"]:
                yield product

    @staticmethod
    def _save(data: dict, file_path):
        """
            Функция сохраняет словарь по определенному пути.
        """
        jdata = json.dumps(data, ensure_ascii=False)
        file_path.write_text(jdata, encoding="UTF-8")


class CategoriesParser(Parse5Ka):
    def __init__(self, categories_url: str, *args, **kwargs):
        self.categories_url = categories_url
        super().__init__(*args, **kwargs)

    def _get_categories(self) -> list:
        """
            Функция делает запрос категории по определенному url.
        """
        response = self._get_response(self.categories_url)
        data = response.json()
        return data

    def run(self):
        """
            Функция получает из категории код родительской группы и её наименование
            перебирает пауком в категории все продукты и передает всё на сохранение.
        """
        for category in self._get_categories():
            category["products"] = []
            url = f"{self.start_url}?categories={category['parent_group_code']}"
            file_path = self.products_path.joinpath(f"{category['parent_group_code']}.json")
            for product in self._parse(url):
                category["products"].append(product)
            self._save(category, file_path)


def get_dir_path(dirname: str) -> Path:
    """
        Функция создает каталог если его ранее не было и возварщает путь.
    """
    dir_path = Path(__file__).parent.joinpath(dirname)
    if not dir_path.exists():
        dir_path.mkdir()
    return dir_path

if __name__ == "__main__":
    url = "https://5ka.ru/api/v2/special_offers/"
    product_path = ""
    cat_path = get_dir_path("categories")
    cat_url = "https://5ka.ru/api/v2/categories/"
    parser = Parse5Ka(url, product_path)
    cat_parser = CategoriesParser(cat_url, url, cat_path)
    cat_parser.run()