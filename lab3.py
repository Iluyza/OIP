import os
import re
import pymorphy2
from typing import Dict, List, Set, Union, Tuple
from collections import defaultdict

class InvertedIndex:
    """Класс для создания и работы с инвертированным индексом"""
    
    def __init__(self):
        self.index = defaultdict(set)
        self.documents = set()
        self.morph_analyzer = pymorphy2.MorphAnalyzer()
        
    def add_document(self, document_id: str, terms: Dict[str, Set[str]]) -> None:
        """Добавляет документ в индекс"""
        # Сохраняем идентификатор документа
        self.documents.add(document_id)
        
        # Добавляем каждую лемму в индекс
        for lemma in terms:
            self.index[lemma].add(document_id)
    
    def create_from_directory(self, lemmas_directory: str) -> None:
        """Создает индекс из файлов с леммами в указанной директории"""
        file_count = 0
        
        # Проходим по всем файлам в директории
        for filename in sorted(os.listdir(lemmas_directory)):
            if filename.endswith('.txt'):
                file_path = os.path.join(lemmas_directory, filename)
                
                # Получаем идентификатор документа (убираем расширение)
                document_id = os.path.splitext(filename)[0]
                
                # Считываем леммы из файла
                terms = {}
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        parts = line.strip().split()
                        if parts:
                            # Формат строки: <лемма> <токен1> <токен2> ... <токенN>
                            lemma = parts[0]
                            tokens = set(parts[1:]) if len(parts) > 1 else set()
                            terms[lemma] = tokens
                
                # Добавляем документ в индекс
                self.add_document(document_id, terms)
                file_count += 1
                
                if file_count % 10 == 0:
                    print(f"Обработано {file_count} файлов...")
        
        print(f"Индекс создан. Всего документов: {len(self.documents)}")
        print(f"Размер словаря индекса: {len(self.index)} терминов")
    
    def save_index(self, file_path: str) -> None:
        """Сохраняет индекс в текстовый файл"""
        with open(file_path, 'w', encoding='utf-8') as file:
            for term in sorted(self.index.keys()):
                doc_list = sorted(self.index[term])
                # Записываем в формате: "термин: документ1, документ2, ..., документN"
                file.write(f"{term}: {', '.join(doc_list)}\n")
                
        print(f"Индекс сохранен в файл: {file_path}")
    
    def load_index(self, file_path: str) -> None:
        """Загружает индекс из текстового файла"""
        self.index.clear()
        self.documents.clear()
        
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                # Пропускаем пустые строки
                if not line.strip():
                    continue
                
                # Разделяем строку на термин и список документов
                parts = line.strip().split(': ', 1)
                if len(parts) != 2:
                    continue
                
                term, doc_list_str = parts
                # Разбиваем список документов по запятой и удаляем пробелы
                doc_list = [doc.strip() for doc in doc_list_str.split(',')]
                
                # Добавляем документы в индекс для данного термина
                self.index[term] = set(doc_list)
                # Обновляем список всех документов
                self.documents.update(doc_list)
        
        print(f"Индекс загружен из файла: {file_path}")
        print(f"Всего документов: {len(self.documents)}")
        print(f"Размер словаря индекса: {len(self.index)} терминов")
    
    def get_lemma(self, word: str) -> str:
        """Приводит слово к лемме"""
        parsed = self.morph_analyzer.parse(word.lower())
        if parsed:
            return parsed[0].normal_form
        return word.lower()
    
    def find_documents(self, term: str) -> Set[str]:
        """Находит документы, содержащие указанный термин"""
        # Приводим поисковый термин к лемме
        lemma = self.get_lemma(term)
        
        return self.index.get(lemma, set())
    
    def _parse_expression(self, expression: str) -> List[str]:
        """Разбирает поисковое выражение на токены"""
        # Заменяем скобки пробелами вокруг них для упрощения токенизации
        expression = re.sub(r'\(', ' ( ', expression)
        expression = re.sub(r'\)', ' ) ', expression)
        
        # Токенизируем выражение
        tokens = expression.split()
        return tokens
    
    def _execute_search(self, tokens: List[str]) -> Set[str]:
        """Выполняет поиск по токенам с учетом операторов AND, OR, NOT и скобок"""
        operand_stack = []
        operator_stack = []
        priorities = {
            'AND': 2,
            'OR': 1,
            'NOT': 3,
            '(': 0
        }
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # Если это открывающая скобка, помещаем её в стек операторов
            if token == '(':
                operator_stack.append(token)
            
            # Если это закрывающая скобка, вычисляем выражение в скобках
            elif token == ')':
                # Выполняем все операции до открывающей скобки
                while operator_stack and operator_stack[-1] != '(':
                    self._execute_operation(operand_stack, operator_stack)
                
                # Удаляем открывающую скобку из стека
                if operator_stack and operator_stack[-1] == '(':
                    operator_stack.pop()
            
            # Если это оператор
            elif token in ('AND', 'OR', 'NOT'):
                # Если это NOT, то он унарный и следующий токен должен быть операндом
                if token == 'NOT':
                    # Пропускаем токен NOT и берем следующий токен
                    i += 1
                    if i < len(tokens):
                        next_token = tokens[i]
                        
                        # Если следующий токен - скобка, обрабатываем выражение в скобках
                        if next_token == '(':
                            # Ищем соответствующую закрывающую скобку
                            depth = 1
                            j = i + 1
                            while j < len(tokens) and depth > 0:
                                if tokens[j] == '(':
                                    depth += 1
                                elif tokens[j] == ')':
                                    depth -= 1
                                j += 1
                            
                            # Рекурсивно обрабатываем выражение в скобках
                            subresult = self._execute_search(tokens[i+1:j])
                            
                            # Применяем оператор NOT к результату
                            result = self.documents - subresult
                            operand_stack.append(result)
                            
                            # Переходим к следующему токену после закрывающей скобки
                            i = j - 1
                        else:
                            # Получаем результат для операнда
                            operand_result = self.find_documents(next_token)
                            
                            # Применяем оператор NOT
                            result = self.documents - operand_result
                            operand_stack.append(result)
                    
                else:
                    # Выполняем все операции с более высоким или равным приоритетом
                    while (operator_stack and operator_stack[-1] != '(' and
                           priorities.get(operator_stack[-1], 0) >= priorities.get(token, 0)):
                        self._execute_operation(operand_stack, operator_stack)
                    
                    # Добавляем текущий оператор в стек
                    operator_stack.append(token)
            
            # Если это операнд
            else:
                result = self.find_documents(token)
                operand_stack.append(result)
            
            i += 1
        
        # Выполняем все оставшиеся операции
        while operator_stack:
            self._execute_operation(operand_stack, operator_stack)
        
        # Результат находится в вершине стека операндов
        return operand_stack[0] if operand_stack else set()
    
    def _execute_operation(self, operand_stack: List[Set[str]], operator_stack: List[str]) -> None:
        """Выполняет операцию из вершины стека операторов над операндами из стека операндов"""
        operator = operator_stack.pop()
        
        if operator == 'AND':
            right_operand = operand_stack.pop()
            left_operand = operand_stack.pop()
            result = left_operand & right_operand
            operand_stack.append(result)
        
        elif operator == 'OR':
            right_operand = operand_stack.pop()
            left_operand = operand_stack.pop()
            result = left_operand | right_operand
            operand_stack.append(result)
    
    def search(self, query: str) -> List[str]:
        """Выполняет булев поиск по запросу"""
        # Если запрос пустой, возвращаем пустой список
        if not query.strip():
            return []
        
        # Разбираем запрос на токены
        tokens = self._parse_expression(query)
        
        # Выполняем поиск
        result = self._execute_search(tokens)
        
        # Возвращаем отсортированный список документов
        return sorted(result)


def main():
    # Путь к директории из задания 2
    lemmas_directory = 'lab2results/lemmas'
    
    # Путь к файлу для сохранения индекса
    index_file = 'inverted_index.txt'
    
    index = InvertedIndex()
    
    # Проверяем, существует ли уже индекс
    if os.path.exists(index_file):
        choice = input(f"Файл индекса {index_file} уже существует. Загрузить его? (y/n): ")
        if choice.lower() == 'y':
            index.load_index(index_file)
        else:
            print("Создание нового индекса...")
            index.create_from_directory(lemmas_directory)
            index.save_index(index_file)
    else:
        print("Создание нового индекса...")
        index.create_from_directory(lemmas_directory)
        index.save_index(index_file)
    
    # Интерактивный поиск
    print("\nНачинаем поиск...")
    print("Поддерживаемые операторы: AND, OR, NOT, скобки () для группировки.")
    print("Пример запроса: (слово1 AND слово2) OR NOT слово3")
    print("Для выхода введите 'exit'.")
    
    while True:
        query = input("\nВведите поисковый запрос: ")
        
        if query.lower() == 'exit':
            break
        
        results = index.search(query)
        
        if results:
            print(f"Найдено документов: {len(results)}")
            print("Результаты (номера страниц):")
            for number in results:
                print(f"- {number}")
        else:
            print("По вашему запросу ничего не найдено.")


if __name__ == "__main__":
    main() 