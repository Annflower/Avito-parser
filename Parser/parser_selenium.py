import time
import csv
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

print("🚀 Парсер Авито (простой и надёжный)")
print("=" * 50)

# ========== НАСТРОЙКИ ==========
CITY = "novosibirsk"
MIN_PRICE = 0
URL = f"https://www.avito.ru/{CITY}/kvartiry/prodam-ASgBAgICAUSSA8YQ?f=ASgBAgICAkSSA8YQ5gmgBg"

# ========== НАСТРОЙКА БРАУЗЕРА ==========
options = Options()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--window-size=1920,1080')
options.add_argument('--remote-allow-origins=*')

print("🔄 Запускаем браузер...")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# Маскировка под человека
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

try:
    print(f"🌐 Загружаем: {URL}")
    driver.get(URL)
    time.sleep(5)
    
    # ========== КАПЧА ==========
    if "капч" in driver.page_source.lower() or "captcha" in driver.page_source.lower():
        print("⚠️ Обнаружена капча! Решите её вручную в окне браузера.")
        input("⏳ Нажмите Enter, когда решите капчу и увидите страницу...")
        print("✅ Продолжаем...")
        driver.refresh()
        time.sleep(5)
    
    # ========== ПАРСИНГ ==========
    print("🔍 Парсим страницу...")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Ищем все карточки
    cards = soup.find_all('div', {'data-marker': 'item'})
    print(f"🔍 Найдено карточек: {len(cards)}")
    
    items = []
    
    for card in cards:
        try:
            # === ЦЕНА (ПРОСТОЙ СПОСОБ) ===
            # Ищем элемент с ценой
            price_element = card.find('span', {'data-marker': 'item-price'})
            if not price_element:
                price_element = card.find('span', class_=re.compile('price|rub', re.I))
            
            price = 0
            if price_element:
                # Берём ТОЛЬКО цифры из текста
                price_text = price_element.text
                # Убираем всё, кроме цифр
                digits = re.sub(r'\D', '', price_text)
                if digits:
                    price = int(digits)
            
            if price < MIN_PRICE:
                continue
            
            # === ЗАГОЛОВОК ===
            title_tag = card.find('h3', {'data-marker': 'item-title'})
            title = title_tag.text.strip() if title_tag else "Без названия"
            
            # === ССЫЛКА ===
            link_tag = card.find('a', {'data-marker': 'item-title'})
            link = "#"
            if link_tag:
                link = link_tag.get('href')
                if link and not link.startswith('http'):
                    link = 'https://www.avito.ru' + link
            
            # === АДРЕС ===
            address_tag = card.find('div', {'data-marker': 'item-address'})
            address = address_tag.text.strip() if address_tag else "Адрес не указан"
            
            # Добавляем только если цена не 0
            if price > 0:
                items.append({
                    'title': title,
                    'price': price,
                    'address': address,
                    'link': link
                })
            
        except Exception as e:
            # Пропускаем ошибочные карточки
            continue
    
    # ========== СОХРАНЕНИЕ ==========
    if items:
        items.sort(key=lambda x: x['price'])
        filename = 'avito_flats.csv'
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['title', 'price', 'address', 'link'])
            writer.writeheader()
            writer.writerows(items)
        
        print(f"\n✅ СОХРАНЕНО {len(items)} ОБЪЯВЛЕНИЙ в файл '{filename}'")
        print(f"💰 Самая дешёвая: {items[0]['price']:,} руб.")
        print(f"💰 Самая дорогая: {items[-1]['price']:,} руб.")
        print("\n🔗 Первые 3 объявления:")
        for item in items[:3]:
            print(f"   {item['title']} — {item['price']:,} руб.")
            print(f"   {item['link']}")
            print()
    else:
        print("❌ Объявлений с ценой не найдено")
        print("💡 Попробуйте изменить MIN_PRICE = 1000000")

except Exception as e:
    print(f"❌ Ошибка: {e}")

finally:
    driver.quit()
    print("🏁 Браузер закрыт")

input("\nНажмите Enter для выхода...")