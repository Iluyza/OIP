import os
import re
import math
from collections import Counter, defaultdict
import pymorphy2

TOKENS_DIR_INPUT = 'lab2results/tokens'
LEMMAS_DIR_INPUT = 'lab2results/lemmas'
OUTPUT_DIR = 'lab4results'
OUTPUT_TOKENS_DIR = os.path.join(OUTPUT_DIR, 'tf-idf-tokens')
OUTPUT_LEMMAS_DIR = os.path.join(OUTPUT_DIR, 'tf-idf-lemmas')
TOTAL_DOCS = 100

def calculate_global_df(doc_ids):
    """Рассчитывает Document Frequency (DF) для токенов и лемм по всем документам"""
    token_df_counts = defaultdict(int)
    lemma_df_counts = defaultdict(int)
    actual_doc_count = 0

    for doc_id in doc_ids:
        token_file_path = os.path.join(TOKENS_DIR_INPUT, f"{doc_id}.txt")
        lemma_file_path = os.path.join(LEMMAS_DIR_INPUT, f"{doc_id}.txt")

        doc_processed = False
        # Обработка токенов для DF
        try:
            with open(token_file_path, 'r', encoding='utf-8') as f:
                tokens = f.read().splitlines()
            unique_tokens_in_doc = set(tokens)
            for token in unique_tokens_in_doc:
                token_df_counts[token] += 1
            doc_processed = True # Хотя бы один файл обработан
        except FileNotFoundError:
            print(f"Предупреждение: Файл токенов {token_file_path} не найден. Пропуск для DF.")
        except Exception as e:
            print(f"Ошибка чтения файла токенов {token_file_path}: {e}. Пропуск для DF.")

        # Обработка лемм для DF
        try:
            unique_lemmas_in_doc = set()
            with open(lemma_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split()
                    if parts:
                        unique_lemmas_in_doc.add(parts[0])
            for lemma in unique_lemmas_in_doc:
                lemma_df_counts[lemma] += 1
            doc_processed = True # Хотя бы один файл обработан
        except FileNotFoundError:
            print(f"Предупреждение: Файл лемм {lemma_file_path} не найден. Пропуск для DF.")
        except Exception as e:
            print(f"Ошибка чтения файла лемм {lemma_file_path}: {e}. Пропуск для DF.")

        if doc_processed:
            actual_doc_count += 1

    print(f"Расчет DF завершен. Обработано документов: {actual_doc_count}. Найдено уникальных токенов: {len(token_df_counts)}, уникальных лемм: {len(lemma_df_counts)}.")
    return token_df_counts, lemma_df_counts, actual_doc_count

def calculate_idf_from_df(df_counts, total_docs):
    """Рассчитывает IDF на основе DF"""
    if total_docs == 0:
        return {}
    idfs = {term: math.log(total_docs / df) for term, df in df_counts.items() if df > 0}
    return idfs

def process_documents_tf_idf(doc_ids, token_idfs, lemma_idfs):
    """Обрабатывает каждый документ для расчета TF и TF-IDF, читая файлы токенов/лемм"""
    os.makedirs(OUTPUT_TOKENS_DIR, exist_ok=True)
    os.makedirs(OUTPUT_LEMMAS_DIR, exist_ok=True)

    processed_count = 0
    for doc_id in doc_ids:
        token_file_path = os.path.join(TOKENS_DIR_INPUT, f"{doc_id}.txt")
        lemma_file_path = os.path.join(LEMMAS_DIR_INPUT, f"{doc_id}.txt")
        token_output_path = os.path.join(OUTPUT_TOKENS_DIR, f"{doc_id}.txt")
        lemma_output_path = os.path.join(OUTPUT_LEMMAS_DIR, f"{doc_id}.txt")

        # Обработка токенов      
        try:
            with open(token_file_path, 'r', encoding='utf-8') as f:
                all_doc_tokens = f.read().splitlines()
            
            total_tokens_in_doc = len(all_doc_tokens)
            token_tf_idf_results = []

            if total_tokens_in_doc > 0:
                token_counts = Counter(all_doc_tokens)
                for token, count in token_counts.items():
                    tf = count / total_tokens_in_doc
                    idf = token_idfs.get(token, 0) # Используем посчитанный IDF
                    tf_idf = tf * idf
                    token_tf_idf_results.append((token, idf, tf_idf))
            else:
                print(f"Предупреждение: Файл токенов {token_file_path} пуст.")

            token_tf_idf_results.sort()
            with open(token_output_path, 'w', encoding='utf-8') as f:
                for token, idf, tf_idf in token_tf_idf_results:
                    f.write(f"{token} {idf:.6f} {tf_idf:.6f}\n")
        
        except FileNotFoundError:
            print(f"Ошибка: Файл токенов {token_file_path} не найден при расчете TF-IDF. Пропуск.")
            open(token_output_path, 'w').close()
            open(lemma_output_path, 'w').close() 
            continue 
        except Exception as e:
            print(f"Ошибка обработки токенов для TF-IDF в файле {token_file_path}: {e}. Пропуск.")
            open(token_output_path, 'w').close()
            open(lemma_output_path, 'w').close()
            continue
        
        # Обработка лемм    
        try:
            lemma_counts = Counter()
            total_lemma_occurrences = 0
            
            with open(lemma_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split()
                    if parts:
                        lemma = parts[0]
                        # Количество токенов для этой леммы = count
                        count = len(parts) - 1 
                        lemma_counts[lemma] += count
                        total_lemma_occurrences += count
            
            lemma_tf_idf_results = []
            if total_lemma_occurrences > 0:
                for lemma, count in lemma_counts.items():
                    tf = count / total_lemma_occurrences
                    idf = lemma_idfs.get(lemma, 0)
                    tf_idf = tf * idf
                    lemma_tf_idf_results.append((lemma, idf, tf_idf))
            else:
                 print(f"Предупреждение: Файл лемм {lemma_file_path} не содержит данных для расчета TF.")
            
            # Сортировка и запись
            lemma_tf_idf_results.sort()
            with open(lemma_output_path, 'w', encoding='utf-8') as f:
                for lemma, idf, tf_idf in lemma_tf_idf_results:
                    f.write(f"{lemma} {idf:.6f} {tf_idf:.6f}\n")

        except FileNotFoundError:
            print(f"Ошибка: Файл лемм {lemma_file_path} не найден при расчете TF-IDF. Пропуск.")
            open(lemma_output_path, 'w').close()
        except Exception as e:
            print(f"Ошибка обработки лемм для TF-IDF в файле {lemma_file_path}: {e}. Пропуск.")
            open(lemma_output_path, 'w').close()
            
        processed_count += 1

    print(f"Результаты сохранены в директориях: {OUTPUT_TOKENS_DIR} и {OUTPUT_LEMMAS_DIR}")

def main():    
    # Получаем список ID документов
    try:
        filenames = os.listdir(TOKENS_DIR_INPUT)
        doc_ids_str = []
        for f in filenames:
            if f.endswith('.txt'):
                doc_id_part = os.path.splitext(f)[0]
                if doc_id_part.isdigit():
                    doc_ids_str.append(doc_id_part)

        doc_ids = sorted(doc_ids_str, key=int)
        
        if len(doc_ids) != TOTAL_DOCS:
             print(f"Предупреждение: Найдено {len(doc_ids)} файлов вида N.txt, ожидалось {TOTAL_DOCS}.")
        actual_total_docs = len(doc_ids)

    except FileNotFoundError:
        print(f"Ошибка: Директория {TOKENS_DIR_INPUT} не найдена. Невозможно получить список документов.")
        return
    except Exception as e:
        print(f"Ошибка при чтении директории {TOKENS_DIR_INPUT}: {e}")
        return

    if not doc_ids:
        print(f"Ошибка: В директории {TOKENS_DIR_INPUT} не найдено файлов вида N.txt. Убедитесь, что Задание 2 выполнено корректно.")
        return

    print(f"Найдено {actual_total_docs} документов для обработки.")

    # Рассчитываем DF  
    token_df_counts, lemma_df_counts, processed_docs_for_df = calculate_global_df(doc_ids)

    if processed_docs_for_df == 0:
        print("Ошибка: Не удалось обработать ни одного документа для расчета DF. Завершение работы.")
        return
    
    # Рассчитываем IDF
    token_idfs = calculate_idf_from_df(token_df_counts, processed_docs_for_df) 
    lemma_idfs = calculate_idf_from_df(lemma_df_counts, processed_docs_for_df)
    print(f"Рассчитан IDF для {len(token_idfs)} токенов и {len(lemma_idfs)} лемм.")

    # Рассчитываем TF-IDF для каждого документа 
    process_documents_tf_idf(doc_ids, token_idfs, lemma_idfs)

if __name__ == "__main__":
    main()