import os
import re
import pymorphy2
import shutil

from collections import defaultdict
from bs4 import BeautifulSoup

class Tokenizer:
    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()
        
        # Список русских стоп-слов
        self.stop_words = {
            'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'она', 'так', 
            'его', 'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было', 
            'вот', 'от', 'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда', 'даже', 'ну', 'вдруг', 
            'ли', 'если', 'уже', 'или', 'ни', 'быть', 'был', 'него', 'до', 'вас', 'нибудь', 'опять', 'уж', 
            'вам', 'ведь', 'там', 'потом', 'себя', 'ничего', 'ей', 'может', 'они', 'тут', 'где', 'есть', 
            'надо', 'ней', 'для', 'мы', 'тебя', 'их', 'чем', 'была', 'сам', 'чтоб', 'без', 'будто', 'чего', 
            'раз', 'тоже', 'себе', 'под', 'будет', 'ж', 'тогда', 'кто', 'этот', 'того', 'потому', 'этого', 
            'какой', 'совсем', 'этом', 'об', 'им', 'здесь', 'при', 'куда', 'зачем', 'всех', 'можно', 'над', 
            'про', 'тут', 'нам', 'нас', 'ими', 'или', 'мой', 'свой', 'твой', 'нам', 'чтобы', 'были', 'кому', 
            'больше', 'после', 'через',
        }

    def extract_tokens(self, file_path: str) -> set[str]:
        """Извлекает токены из HTML файла"""
        with open(file_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # Извлекаем текст из HTML
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator=' ')

        # Находим только русские слова
        tokens_raw = re.findall(r'\b[а-яё]+\b', text, flags=re.IGNORECASE)
        tokens = set()

        # Фильтруем токены
        for token in tokens_raw:
            token_lower = token.lower()
            # Проверяем, что токен - это слово и не стоп-слово
            if token_lower.isalpha() and token_lower not in self.stop_words and len(token_lower) > 2:
                tokens.add(token_lower)
        
        return tokens

    def group_by_lemma(self, tokens: set[str]) -> dict[str, set[str]]:
        """Группирует токены по леммам"""
        lemmas = defaultdict(set)

        for token in tokens:
            parsed = self.morph.parse(token)
            if parsed:
                lemma = parsed[0].normal_form
                lemmas[lemma].add(token)

        return lemmas

    def process_file(self, file_path: str, file_number: str) -> None:
        """Обрабатывает HTML файл и создает файлы токенов и лемм"""
        tokens = self.extract_tokens(file_path)
        lemmas = self.group_by_lemma(tokens)

        # Создаем директории для результатов
        tokens_dir = os.path.join('lab2results', 'tokens')
        lemmas_dir = os.path.join('lab2results', 'lemmas')
        
        os.makedirs(tokens_dir, exist_ok=True)
        os.makedirs(lemmas_dir, exist_ok=True)

        # Записываем токены в файл
        tokens_file = os.path.join(tokens_dir, f"{file_number}.txt")
        with open(tokens_file, 'w', encoding='utf-8') as f:
            for token in sorted(tokens):
                f.write(token + '\n')

        # Записываем леммы в файл
        lemmas_file = os.path.join(lemmas_dir, f"{file_number}.txt")
        with open(lemmas_file, 'w', encoding='utf-8') as f:
            for lemma in sorted(lemmas):
                f.write(lemma + ' ' + ' '.join(sorted(lemmas[lemma])) + '\n')
        
        return len(tokens), len(lemmas)


def main():
    # Создаем директорию для результатов
    output_dir = 'lab2results'
    os.makedirs(output_dir, exist_ok=True)
    
    # Удаляем предыдущие результаты, если они есть
    tokens_dir = os.path.join(output_dir, 'tokens')
    lemmas_dir = os.path.join(output_dir, 'lemmas')
    
    if os.path.exists(tokens_dir):
        shutil.rmtree(tokens_dir)
    if os.path.exists(lemmas_dir):
        shutil.rmtree(lemmas_dir)
    
    # Создаем новые директории
    os.makedirs(tokens_dir, exist_ok=True)
    os.makedirs(lemmas_dir, exist_ok=True)

    tokenizer = Tokenizer()
    processed_files = 0
    total_tokens = 0
    total_lemmas = 0

    # Обрабатываем все HTML файлы
    input_dir = 'pages'
    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith('.html'):
            file_path = os.path.join(input_dir, filename)
            file_number = os.path.splitext(filename)[0]
            
            print(f"Обработка файла: {filename}")
            tokens_count, lemmas_count = tokenizer.process_file(file_path, file_number)
            
            total_tokens += tokens_count
            total_lemmas += lemmas_count
            processed_files += 1

    print(f"\nОбработка завершена.")
    print(f"Обработано файлов: {processed_files}")
    print(f"Всего уникальных токенов: {total_tokens}")
    print(f"Всего уникальных лемм: {total_lemmas}")
    print(f"Токены и леммы сохранены в директориях:")
    print(f"- {tokens_dir}")
    print(f"- {lemmas_dir}")

    # Создаем архив с результатами
    shutil.make_archive('lab2results', 'zip', output_dir)
    print(f"Архив с результатами: lab2results.zip")


if __name__ == "__main__":
    main()