import requests
import os
from urllib.parse import urlparse
import time

def create_directory(directory):
    """Создает директорию, если она не существует"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def download_page(url, output_dir, file_number):
    """Загружает страницу и сохраняет её в файл"""
    try:
        # Добавляем задержку между запросами
        time.sleep(1)
        
        # Отправляем GET запрос
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        # Проверяем успешность запроса
        if response.status_code == 200:
            # Создаем имя файла
            filename = f"{file_number}.html"
            filepath = os.path.join(output_dir, filename)
            
            # Сохраняем содержимое в файл
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
                
            return True
        return False
    except Exception as e:
        print(f"Ошибка при загрузке {url}: {str(e)}")
        return False

def main():
    # Список URL-адресов для загрузки (замените на свой список)
    urls = [
        "https://habr.com/ru/articles/1/",
        "https://habr.com/ru/articles/2/",
        "https://habr.com/ru/articles/4/",
        "https://habr.com/ru/articles/6/",
        "https://habr.com/ru/articles/7/",
        "https://habr.com/ru/articles/8/",  
        "https://habr.com/ru/articles/9/",
        "https://habr.com/ru/articles/10/",
        "https://habr.com/ru/articles/11/",
        "https://habr.com/ru/articles/12/",
        "https://habr.com/ru/articles/13/",
        "https://habr.com/ru/articles/14/",
        "https://habr.com/ru/articles/17/",
        "https://habr.com/ru/articles/18/",
        "https://habr.com/ru/articles/19/",
        "https://habr.com/ru/articles/20/",
        "https://habr.com/ru/articles/21/",
        "https://habr.com/ru/articles/22/",
        "https://habr.com/ru/articles/24/",
        "https://habr.com/ru/articles/26/",
        "https://habr.com/ru/articles/27/",
        "https://habr.com/ru/articles/28/",
        "https://habr.com/ru/articles/29/",
        "https://habr.com/ru/articles/30/",
        "https://habr.com/ru/articles/32/", 
        "https://habr.com/ru/articles/33/",
        "https://habr.com/ru/articles/34/",
        "https://habr.com/ru/articles/35/",
        "https://habr.com/ru/articles/36/",
        "https://habr.com/ru/articles/37/",
        "https://habr.com/ru/articles/39/",
        "https://habr.com/ru/articles/40/",
        "https://habr.com/ru/articles/42/",
        "https://habr.com/ru/articles/43/",
        "https://habr.com/ru/articles/45/",
        "https://habr.com/ru/articles/46/",
        "https://habr.com/ru/articles/47/",
        "https://habr.com/ru/articles/48/",
        "https://habr.com/ru/articles/49/",
        "https://habr.com/ru/articles/51/",
        "https://habr.com/ru/articles/52/",
        "https://habr.com/ru/articles/53/",
        "https://habr.com/ru/articles/54/",
        "https://habr.com/ru/articles/55/",
        "https://habr.com/ru/articles/56/",     
        "https://habr.com/ru/articles/57/",
        "https://habr.com/ru/articles/58/",
        "https://habr.com/ru/articles/59/",
        "https://habr.com/ru/articles/63/",
        "https://habr.com/ru/articles/64/",
        "https://habr.com/ru/articles/65/",
        "https://habr.com/ru/articles/66/",
        "https://habr.com/ru/articles/67/",
        "https://habr.com/ru/articles/71/",
        "https://habr.com/ru/articles/72/",
        "https://habr.com/ru/articles/73/",
        "https://habr.com/ru/articles/74/",
        "https://habr.com/ru/articles/75/",
        "https://habr.com/ru/articles/76/",
        "https://habr.com/ru/articles/77/",
        "https://habr.com/ru/articles/78/",
        "https://habr.com/ru/articles/79/",
        "https://habr.com/ru/articles/80/",
        "https://habr.com/ru/articles/81/",         
        "https://habr.com/ru/articles/82/", 
        "https://habr.com/ru/articles/84/",
        "https://habr.com/ru/articles/85/",
        "https://habr.com/ru/articles/86/",
        "https://habr.com/ru/articles/87/", 
        "https://habr.com/ru/articles/89/",
        "https://habr.com/ru/articles/90/",
        "https://habr.com/ru/articles/91/",
        "https://habr.com/ru/articles/92/",
        "https://habr.com/ru/articles/93/",
        "https://habr.com/ru/articles/94/",
        "https://habr.com/ru/articles/95/",
        "https://habr.com/ru/articles/96/",
        "https://habr.com/ru/articles/97/",
        "https://habr.com/ru/articles/98/",
        "https://habr.com/ru/articles/100/",
        "https://habr.com/ru/articles/102/",
        "https://habr.com/ru/articles/104/",
        "https://habr.com/ru/articles/105/",    
        "https://habr.com/ru/articles/106/",
        "https://habr.com/ru/articles/108/",
        "https://habr.com/ru/articles/109/",
        "https://habr.com/ru/articles/110/",
        "https://habr.com/ru/articles/112/",
        "https://habr.com/ru/articles/113/",
        "https://habr.com/ru/articles/114/",
        "https://habr.com/ru/articles/115/",
        "https://habr.com/ru/articles/116/",
        "https://habr.com/ru/articles/117/",
        "https://habr.com/ru/articles/118/",
        "https://habr.com/ru/articles/119/",
        "https://habr.com/ru/articles/121/",
        "https://habr.com/ru/articles/122/",
        "https://habr.com/ru/articles/124/",
        "https://habr.com/ru/articles/125/",
        "https://habr.com/ru/articles/127/",
    ]
    
    # Создаем директорию для сохранения страниц
    output_dir = "pages"
    create_directory(output_dir)
    
    # Создаем или очищаем index.txt
    with open("index.txt", 'w', encoding='utf-8') as index_file:
        index_file.write("Номер файла\tURL\n")
    
    # Загружаем страницы
    successful_downloads = 0
    file_number = 1
    
    for url in urls:
        if download_page(url, output_dir, file_number):
            # Записываем информацию в index.txt
            with open("index.txt", 'a', encoding='utf-8') as index_file:
                index_file.write(f"{file_number}\t{url}\n")
            
            successful_downloads += 1
            file_number += 1
            print(f"Успешно загружена страница: {url}")
        else:
            print(f"Не удалось загрузить страницу: {url}")
            
        if successful_downloads >= 100:
            break
    
    print(f"\nЗагрузка завершена. Успешно загружено страниц: {successful_downloads}")

if __name__ == "__main__":
    main()
