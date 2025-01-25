import telebot
import os
import json
from bs4 import BeautifulSoup
import requests
import threading


BOT_TOKEN = os.environ.get('BOT_TOKEN')
NEWS_DATA_PATH = "data/news.json"
CHATS = [{"chat_id": "@united_nations_news", "language": "en"}]

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t  

def get_news(language):
    url = f"https://news.un.org/feed/subscribe/{language}/news/all/rss.xml"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")
    items = soup.find_all("item")
    news = []
    
    for item in items:
        title = item.find("title").text
        link = item.find("guid").text
        description = item.find("description").text
        image = item.find("enclosure")["url"]
        news.append({"title": title, "link": link, "description": description, "image": image})
    return news

def is_news_new(newsData, news):
    for n in newsData:
        if n["link"] == news["link"]:
            return False
    return True

def send_news():
    newsData = get_data(NEWS_DATA_PATH)
    for chat in CHATS:
        language = chat["language"]
        news = get_news(language)
        for n in news:
            if is_news_new(newsData, n):
                newsData.append(n)
                save_data(newsData, NEWS_DATA_PATH)
                print(n['link'])
                bot.send_photo(chat["chat_id"], n["image"], caption=f"*{n['title']}*\n\n{n['description']}\n\n[Read more]({n['link']})", parse_mode="Markdown")


def get_data(path):
    with open(path, "r") as f:
        return json.load(f)


def save_data(data, path):
    with open(path, "w") as f:
        json.dump(data, f)


if __name__ == "__main__":

    bot = telebot.TeleBot(BOT_TOKEN)


    
    set_interval(send_news, 300)
    bot.infinity_polling()
        