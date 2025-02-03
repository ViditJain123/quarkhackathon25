# app/services/rag_service.py
from .embedding_service import EmbeddingSearcher
from typing import List

class RAGService:
    def __init__(self):
        self.searcher = EmbeddingSearcher('embeddings_output')
    
    def get_relevant_context(self, query: str, top_k: int = 3) -> str:
        results = self.searcher.search(query, top_k=top_k)
        context = "\n".join([r['text'] for r in results])
        return context