import numpy as np
import pandas as pd
from pathlib import Path
import fasttext
from sklearn.metrics.pairwise import cosine_similarity

class EmbeddingSearcher:
    def __init__(self, embeddings_dir):
        self.embeddings_dir = Path(embeddings_dir)
        # Load embeddings and metadata
        self.embeddings = np.load(self.embeddings_dir / 'embeddings.npy')
        self.metadata = pd.read_csv(self.embeddings_dir / 'metadata.csv')
        # Load FastText model
        self.model = fasttext.load_model('cc.en.300.bin')
        
    def search(self, query, top_k=5):
        """
        Search for most similar chunks to the query
        Args:
            query (str): Search query
            top_k (int): Number of results to return
        Returns:
            list: Top k results with their metadata and similarity scores
        """
        # Generate embedding for the query
        query_embedding = self.model.get_sentence_vector(query)
        
        # Reshape for sklearn
        query_embedding = query_embedding.reshape(1, -1)
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Get top k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Prepare results
        results = []
        for idx in top_indices:
            result = {
                'similarity': similarities[idx],
                'text': self.metadata.iloc[idx]['text'],
                'company': self.metadata.iloc[idx]['company'],
                'category': self.metadata.iloc[idx]['category'],
                'file_name': self.metadata.iloc[idx]['file_name']
            }
            results.append(result)
        
        return results

def main():
    # Initialize searcher
    embeddings_dir = Path('embeddings_output')  # Change this to your embeddings directory
    searcher = EmbeddingSearcher(embeddings_dir)
    
    # Test queries
    test_queries = [
        "What is the premium payment process?"
    ]
    
    # Run test searches
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        
        results = searcher.search(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            print(f"\nResult {i} (Similarity: {result['similarity']:.3f})")
            print(f"Company: {result['company']}")
            print(f"Category: {result['category']}")
            print(f"File: {result['file_name']}")
            print(f"Text snippet: {result['text'][:200]}...")

if __name__ == "__main__":
    main()

# Example usage:
"""
# For interactive use:
searcher = EmbeddingSearcher('embeddings_output')
results = searcher.search("What are the health insurance benefits?", top_k=3)

# Print detailed results
for i, result in enumerate(results, 1):
    print(f"\nResult {i}")
    print(f"Similarity Score: {result['similarity']:.3f}")
    print(f"Company: {result['company']}")
    print(f"Category: {result['category']}")
    print(f"Text: {result['text'][:200]}...")
"""