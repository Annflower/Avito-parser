"""
ПРОСТОЙ ПАРСЕР ЧЕРЕЗ REQUESTS
Для сайтов без защиты (новости, блоги, погода и т.д.)
"""

import requests
from bs4 import BeautifulSoup
import csv
import re
import time
import random

print("🚀 Простой парсер (Requests + BeautifulSoup)")
print("=" * 50)

# ========== НАСТРОЙКИ ==========
URL = "https://habr.com/ru/articles/"  # Замените на нужный сайт
MIN_PRICE = 0  # Для фильтрации (если есть цены)

# Список User-Agent для маскировки
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

def get_random_headers():
    """Возвращает случайные заголовки для маскировки"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

def get_page(url):
    """Загружает страницу с повторными попытками"""
    for attempt in range(3):
        try:
            print(f"🌐 Загружаем: {url} (попытка {attempt+1}/3)")
            headers = get_random_headers()
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                print("✅ Страница загружена!")
                return response.text
            elif response.status_code == 429:
                wait_time = 10 * (attempt + 1)
                print(f"⚠️ Слишком много запросов (429). Ждём {wait_time} сек...")
                time.sleep(wait_time)
            else:
                print(f"❌ Код ответа: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(5)
    return None

def parse_page(html):
    """Парсит страницу и извлекает данные"""
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    
    # Пример: парсим статьи с Habr
    articles = soup.find_all('article', class_=re.compile('article'))
    
    if not articles:
        # Если статьи не найдены, пробуем другой селектор
        articles = soup.find_all('div', class_=re.compile('post'))
    
    print(f"🔍 Найдено элементов: {len(articles)}")
    
    for article in articles:
        try:
            # Заголовок
            title_tag = article.find('a', class_=re.compile('title'))
            if not title_tag:
                title_tag = article.find('h2')
            title = title_tag.text.strip() if title_tag else "Нет заголовка"
            
            # Ссылка
            link = "#"
            if title_tag and title_tag.get('href'):
                link = title_tag.get('href')
                if not link.startswith('http'):
                    link = 'https://habr.com' + link
            
            # Дата (если есть)
            date_tag = article.find('time')
            date = date_tag.text.strip() if date_tag else "Дата не указана"
            
            items.append({
                'title': title,
                'date': date,
                'link': link
            })
            
        except Exception as e:
            continue
    
    return items

def save_to_csv(data, filename='data.csv'):
    """Сохраняет данные в CSV"""
    if not data:
        print("❌ Нет данных для сохранения")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✅ Сохранено {len(data)} записей в файл '{filename}'")

# ========== ОСНОВНАЯ ЧАСТЬ ==========
html = get_page(URL)

if html:
    items = parse_page(html)
    if items:
        save_to_csv(items, 'parsed_data.csv')
        print("\n📊 Первые 3 записи:")
        for i, item in enumerate(items[:3], 1):
            print(f"{i}. {item['title']}")
            print(f"   {item.get('date', '')}")
            print(f"   {item['link']}")
            print()
    else:
        print("❌ Данные не найдены")
else:
    print("❌ Не удалось загрузить страницу")

print("\n🏁 Готово!")
input("Нажмите Enter для выхода...")