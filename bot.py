#6634413708:AAGC1Q_qIE0AKwSKCCqDMcgOOj02IV7ueGg id:752219662
import telebot
from selenium import webdriver
from time import sleep


options = webdriver.ChromeOptions()
options.add_argument("--remote-debugging-port=0")

driver = webdriver.Chrome()

bot = telebot.TeleBot("6634413708:AAGC1Q_qIE0AKwSKCCqDMcgOOj02IV7ueGg")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет")

@bot.message_handler(commands=['search_videos'])
def search_videos(message):
    msg = bot.send_message(message.chat.id, "Введите текст, который вы хотите найти на YouTube")
    bot.register_next_step_handler(msg, search)

@bot.message_handler(content_types=['text'])
def text(message):
    bot.send_message(message.chat.id, "Ты что-то хотел?")
def search(message):
    bot.send_message(message.chat.id, "Начинаю поиск")
    video_href = "https://matchtv.ru/search?q=" + message.text
    driver.get(video_href)
    sleep(2)
    videos = driver.find_elements_by_id("video-title")
    for i in range(len(videos)):
        bot.send_message(message.chat.id, videos[i].get_attribute('href'))
        if i == 10:
            break


# Запуск бота
bot.polling()
