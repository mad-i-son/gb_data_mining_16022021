"""
Необходимо собрать структуры товаров по акции и сохранить их в MongoDB
пример структуры и типы обязательно хранить поля даты как объекты datetime

{
    "url": str,
    "promo_name": str,
    "product_name": str,
    "old_price": float,
    "new_price": float,
    "image_url": str,
    "date_from": "DATETIME",
    "date_to": "DATETIME",
}

"""

import requests
from urllib.parse import urljoin
import bs4
import pymongo
import time


class MagnitParse:
    def __init__(self, start_url, db_client):
        self.start_url = start_url
        self.db = db_client["gb_data_mining_16022021"]

    def _get_response(self, url):
        time_sleep_counts = 0
        while True:
            response = requests.get(url)
            if response.status_code == 200:
                return response
            elif response.status_code != 200:
                time_sleep_counts += 1
                print(response.status_code)
                if time_sleep_counts == 3:
                    break
                else:
                    time.sleep(0.5)

    def _get_soup(self, url):
        time_sleep_counts = 0
        while True:
            response = self._get_response(url)
            if response.status_code == 200:
                soup = bs4.BeautifulSoup(response.text, "lxml")
                return soup
            elif response.status_code != 200:
                time_sleep_counts += 1
                print(response.status_code)
                if time_sleep_counts == 3:
                    break
                else:
                    time.sleep(0.5)

    def _template(self):
        return {
            "url": lambda a: urljoin(self.start_url, a.attrs.get("href")),
            "promo_name": lambda a: a.find("div", attrs={"class": "card-sale__header"}).text,
            "title": lambda a: a.find("div", attrs={"class": "card-sale__title"}).text,
        }

    def run(self):
        soup = self._get_soup(self.start_url)
        catalog = soup.find("div", attrs={"class": "сatalogue__main"})
        for product_a in catalog.find_all("a", recursive=False):
            product_data = self._parse(product_a)
            self.save(product_data)

    def _parse(self, product_a: bs4.Tag) -> dict:
        product_data = {}
        for key, funk in self._template().items():
            try:
                product_data[key] = funk(product_a)
            except AttributeError:
                pass

        return product_data

    def save(self, data: dict):
        collection = self.db["magnit"]
        collection.insert_one(data)


if __name__ == "__main__":
    url = "https://magnit.ru/promo/"
    db_client = pymongo.MongoClient("mongodb://localhost:27017")
    parser = MagnitParse(url, db_client)
    parser.run()