import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

class AvitoParse:
    def __init__(self, url: str, items: list, count: int = 100, version_main=None):
        self.url = url
        self.items = items
        self.count = count
        self.version_main = version_main
        self.data = []

    def __set_up(self):
        options = Options()
        options.add_argument('--headless')
        self.driver = uc.Chrome(version_main=self.version_main, options=options)

    def __get_url(self):
        self.driver.get(self.url)

    def __paginator(self):
        while self.driver.find_element(By.CSS_SELECTOR, "[data-marker='pagination-button/nextPage']") and self.count > 0:
            self.__parse_page()
            self.driver.find_element(By.CSS_SELECTOR, "[class*='item-descriptionStep']").click()
            self.count -= 1

    def __parse_page(self):
        titles = self.driver.find_elements(By.CSS_SELECTOR, "[data-marker='item']")
            for title in titles:
            name = title.find_element(By.CSS_SELECTOR, "[itemprop='name']").text
            description = title.find_element(By.CSS_SELECTOR, "[itemprop='name']").text
            url = title.find_element(By.CSS_SELECTOR, "[data-marker='item-title']").get_attribute("href")
            # Используйте селектор для извлечения текста "Бесплатно"
            price_element = title.find_element(By.CSS_SELECTOR, "strong.styles-module-root-LIAav span")
            # Получите текст внутри элемента span
            price = price_element.text if price_element else "Цена не указана"
            print(name, description, url, price)
            data = {
                'name':name,
                'description':description,
                'url':url,
                'price':price
            }
            if any([item.lower() in description for item in self.items]):
                self.data.append(data)
            #   print(name, description, url, price)
        self.__save_data()

    def __save_data(self):
        with open("items.json",'w',encoding='utf-8') as f:
            json.dump(self.data,f,ensure_ascii=False,indent=4)

    def parse(self):
        self.__set_up()
        self.__get_url()
        self.__paginator()


if __name__ == "__main__":
  AvitoParse(url='https://www.avito.ru/rostov-na-donu/sobaki?cd=1&q=%D0%BE%D1%82%D0%B4%D0%B0%D0%BC+%D0%B1%D0%B5%D1%81%D0%BF%D0%BB%D0%B0%D1%82%D0%BD%D0%BE', count=1, items=["собака"], version_main=119).parse()

