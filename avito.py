import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class AvitoParse:
    def __init__(self, url: str, count: int = 100, version_main=None):
        self.url = url
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
        while self.count > 0:
            self.__parse_page()
            try:
                next_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-marker='pagination-button/nextPage']"))
                )
                next_button.click()
            except Exception as e:
                print(f"Error clicking next button: {e}")
                break
            self.count -= 1

    def __parse_page(self):
        titles = self.driver.find_elements(By.CSS_SELECTOR, "[data-marker='item']")
        for title in titles:
            # Проверяем наличие элемента с CSS-классом "SnippetBadgeV2-root-hYQxp" и пропускаем его, если он присутствует
            if title.find_elements(By.CSS_SELECTOR, ".SnippetBadgeV2-root-hYQxp"):
                continue

            name = title.find_element(By.CSS_SELECTOR, "[itemprop='name']").text

            # Проверяем наличие элемента .iva-item-descriptionStep-C0ty1 перед его поиском
            description_element = title.find_elements(By.CSS_SELECTOR, ".iva-item-descriptionStep-C0ty1")
            description = description_element[0].text if description_element else "Описание отсутствует"

            # Limit description to 100 characters
            description = description[:100]

            url = title.find_element(By.CSS_SELECTOR, "[data-marker='item-title']").get_attribute("href")
            price_element = title.find_element(By.CSS_SELECTOR, "strong.styles-module-root-LIAav span")
            price = price_element.text if price_element else "Цена не указана"

            data = {
                'name': name,
                'description': description,
                'url': url,
                'price': price
            }
            self.data.append(data)

    def search_items(self, query):
        filtered_data = [item for item in self.data if query.lower() in item['description'].lower()]
        return filtered_data[:10]

    def __save_data(self):
        with open("items.json", 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def parse(self):
        self.__set_up()
        self.__get_url()
        self.__paginator()
        self.__save_data()
        self.driver.quit()

class AvitoBot:
    def __init__(self, token: str, avito_parser: AvitoParse):
        self.token = token
        self.avito_parser = avito_parser
        self.updater = Updater(self.token, use_context=True)
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.text_input))

    def start(self, update: Update, context: CallbackContext):
        update.message.reply_text("Что ты хочешь на халяву?")

    def text_input(self, update: Update, context: CallbackContext):
        text = update.message.text

        if context.user_data.get('waiting_for_confirmation', False):
            # Handle user confirmation
            context.user_data['waiting_for_confirmation'] = False
            self.handle_confirmation(update, context)
            return

        if 'query' in context.user_data and context.user_data['query']:
            # Если есть сохраненный запрос, используем его
            query = context.user_data['query']
            context.user_data['query'] = None  # Сбрасываем сохраненный запрос
        else:
            # Если нет сохраненного запроса, задаем новый вопрос
            context.user_data['query'] = text
            update.message.reply_text(f"Ищу '{text}'...\nМного хочешь, не могу найти ничего подходящего. Может, что-то другое?")
            return

        avito_items = self.avito_parser.search_items(query)
        if avito_items:
            for item in avito_items:
                message = f"Название: {item['name']}\nОписание: {item['description']}\nЦена: {item['price']}\nURL: {item['url']}"
                update.message.reply_text(message)

            # После успешного поиска спрашиваем, хочет ли пользователь продолжить
            update.message.reply_text("Хочешь продолжить поиск? (Да/Нет)")

            # Переключаем состояние бота на ожидание ответа пользователя
            context.user_data['waiting_for_confirmation'] = True
        else:
            update.message.reply_text("Много хочешь, не могу найти ничего подходящего. Может, что-то другое?")

    def handle_confirmation(self, update: Update, context: CallbackContext):
        # Обработка ответа пользователя на вопрос о продолжении поиска
        answer = update.message.text.lower()
        if answer == 'да':
            # Пользователь хочет продолжить, спрашиваем, что он хочет на халяву
            context.user_data['waiting_for_confirmation'] = False
            update.message.reply_text("Скажи, что ты хочешь на халяву?")
        elif answer == 'нет':
            # Пользователь не хочет продолжать, заканчиваем разговор
            context.user_data['waiting_for_confirmation'] = False
            update.message.reply_text("До свидания! Если захочешь что-то еще, напиши /start.")
        else:
            # Некорректный ответ, спрашиваем снова
            update.message.reply_text("Пожалуйста, ответьте 'Да' или 'Нет'")

    def run(self):
        self.updater.start_polling()
        self.updater.idle()
if __name__ == "__main__":
    avito_parser = AvitoParse(url='https://www.avito.ru/rostov-na-donu/posuda_i_tovary_dlya_kuhni?cd=1&q=%D0%BE%D1%82%D0%B4%D0%B0%D0%BC+%D0%B1%D0%B5%D1%81%D0%BF%D0%BB%D0%B0%D1%82%D0%BD%D0%BE&s=104', count=1, version_main=119)
    avito_parser.parse()

    bot_token = "6634413708:AAGC1Q_qIE0AKwSKCCqDMcgOOj02IV7ueGg"
    avito_bot = AvitoBot(token=bot_token, avito_parser=avito_parser)
    avito_bot.run()
