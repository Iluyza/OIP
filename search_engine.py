import os
import numpy as np
from flask import Flask, render_template, request, jsonify
from collections import defaultdict
import math
from typing import List, Dict, Tuple
import json

app = Flask(__name__)

class VectorSearchEngine:
    def __init__(self):
        self.doc_vectors = {}  # Векторы документов
        self.term_to_id = {}  # Словарь термин -> id
        self.id_to_term = {}  # Словарь id -> термин
        self.doc_ids = []     # Список id документов
        self.vector_dim = 0   # Размерность векторов
        
    def load_tfidf_data(self, tfidf_dir: str):
        """Загружает TF-IDF данные из директории"""
        # Сначала собираем все уникальные термины
        all_terms = set()
        for filename in os.listdir(tfidf_dir):
            if filename.endswith('.txt'):
                with open(os.path.join(tfidf_dir, filename), 'r', encoding='utf-8') as f:
                    for line in f:
                        term = line.split()[0]
                        all_terms.add(term)
        
        # Создаем словари для маппинга терминов
        self.term_to_id = {term: idx for idx, term in enumerate(sorted(all_terms))}
        self.id_to_term = {idx: term for term, idx in self.term_to_id.items()}
        self.vector_dim = len(self.term_to_id)
        
        # Загружаем векторы документов
        for filename in os.listdir(tfidf_dir):
            if filename.endswith('.txt'):
                doc_id = filename[:-4]  # Убираем расширение .txt
                self.doc_ids.append(doc_id)
                
                # Создаем вектор документа
                doc_vector = np.zeros(self.vector_dim)
                with open(os.path.join(tfidf_dir, filename), 'r', encoding='utf-8') as f:
                    for line in f:
                        term, _, tfidf = line.strip().split()
                        term_id = self.term_to_id[term]
                        doc_vector[term_id] = float(tfidf)
                
                # Нормализуем вектор
                norm = np.linalg.norm(doc_vector)
                if norm > 0:
                    doc_vector = doc_vector / norm
                
                self.doc_vectors[doc_id] = doc_vector
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Выполняет векторный поиск по запросу"""
        # Создаем вектор запроса
        query_vector = np.zeros(self.vector_dim)
        query_terms = query.lower().split()
        
        # Заполняем вектор запроса
        for term in query_terms:
            if term in self.term_to_id:
                term_id = self.term_to_id[term]
                query_vector[term_id] = 1.0
        
        # Нормализуем вектор запроса
        norm = np.linalg.norm(query_vector)
        if norm > 0:
            query_vector = query_vector / norm
        
        # Вычисляем косинусное сходство для каждого документа
        similarities = []
        for doc_id, doc_vector in self.doc_vectors.items():
            similarity = np.dot(query_vector, doc_vector)
            similarities.append((doc_id, float(similarity)))
        
        # Сортируем по убыванию сходства и возвращаем top_k результатов
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

# Создаем экземпляр поисковой системы
search_engine = VectorSearchEngine()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'results': []})
    
    results = search_engine.search(query)
    return jsonify({'results': results})

def main():
    # Загружаем данные TF-IDF
    search_engine.load_tfidf_data('lab4results/tf-idf-lemmas')
    
    # Запускаем веб-сервер
    app.run(debug=True)

if __name__ == '__main__':
    main()