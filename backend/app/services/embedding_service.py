# app/services/embedding_service.py
import os
from pathlib import Path
import PyPDF2
import fasttext
import numpy as np
import pandas as pd
from tqdm import tqdm
import re
import nltk
from nltk.tokenize import sent_tokenize
from sklearn.metrics.pairwise import cosine_similarity
import logging
nltk.download('punkt')
nltk.download('punkt_tab')

class PDFEmbeddingGenerator:
    def __init__(self, base_dir, chunk_size=512):
        self.base_dir = Path(base_dir)
        self.chunk_size = chunk_size
        self.companies = ['LIC', 'Maxlife']
        self.categories = ['Health Plans', 'Insurance Plans', 'Pension Plans']
        
        # Update model path to match EmbeddingSearcher
        base_dir = Path(__file__).resolve().parent.parent  # This gets us to 'app' directory
        model_path = base_dir / 'models' / 'cc.en.300.bin'
        self.model = fasttext.load_model(str(model_path))
        
    def preprocess_text(self, text):
        """Clean and preprocess text"""
        # Remove special characters and extra whitespace
        text = re.sub(r'[^\w\s.]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ''
                for page in reader.pages:
                    text += page.extract_text() + ' '
                return self.preprocess_text(text)
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            return ''
    
    def chunk_text(self, text):
        """Split text into chunks using sentence boundaries"""
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = ''
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence + ' '
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ' '
        
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks
    
    def generate_embedding(self, text):
        """Generate FastText embedding for a text chunk"""
        return self.model.get_sentence_vector(text)
    
    def process_all_pdfs(self):
        """Process all PDFs and generate embeddings"""
        data = []
        
        for company in self.companies:
            for category in self.categories:
                folder_path = self.base_dir / company / category
                if not folder_path.exists():
                    continue
                
                pdf_files = list(folder_path.glob('*.pdf'))
                for pdf_file in tqdm(pdf_files, desc=f"Processing {company}/{category}"):
                    # Extract text from PDF
                    text = self.extract_text_from_pdf(pdf_file)
                    if not text:
                        continue
                    
                    # Split into chunks
                    chunks = self.chunk_text(text)
                    
                    # Generate embeddings for each chunk
                    for chunk_idx, chunk in enumerate(chunks):
                        embedding = self.generate_embedding(chunk)
                        data.append({
                            'company': company,
                            'category': category,
                            'file_name': pdf_file.name,
                            'chunk_idx': chunk_idx,
                            'text': chunk,
                            'embedding': embedding
                        })
        
        return pd.DataFrame(data)
    
    def save_embeddings(self, df, output_dir):
        """Save embeddings and metadata"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save embeddings as numpy array
        embeddings = np.stack(df['embedding'].values)
        np.save(output_dir / 'embeddings.npy', embeddings)
        
        # Save metadata without embeddings column
        metadata = df.drop('embedding', axis=1)
        metadata.to_csv(output_dir / 'metadata.csv', index=False)

class EmbeddingSearcher:
    def __init__(self, embeddings_dir):
        self.embeddings_dir = Path(embeddings_dir)
        self.logger = logging.getLogger(__name__)
        
        try:
            # Load embeddings and metadata
            self.embeddings = np.load(self.embeddings_dir / 'embeddings.npy')
            self.metadata = pd.read_csv(self.embeddings_dir / 'metadata.csv')
            
            # Update model path to point to app/models
            base_dir = Path(__file__).resolve().parent.parent  # This gets us to 'app' directory
            model_path = base_dir / 'models' / 'cc.en.300.bin'
            
            if not model_path.exists():
                self.logger.error(f"FastText model not found at {model_path}")
                raise FileNotFoundError(f"FastText model not found at {model_path}")
                
            self.model = fasttext.load_model(str(model_path))
            
        except Exception as e:
            self.logger.error(f"Error initializing EmbeddingSearcher: {str(e)}")
            raise


    def search(self, query: str, top_k: int = 3) -> list:
        """
        Search for most similar chunks to the query
        Args:
            query (str): Search query
            top_k (int): Number of results to return
        Returns:
            list: Top k results with their metadata and similarity scores
        """
        try:
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
                    'similarity': float(similarities[idx]),
                    'text': self.metadata.iloc[idx]['text'],
                    'company': self.metadata.iloc[idx]['company'],
                    'category': self.metadata.iloc[idx]['category'],
                    'file_name': self.metadata.iloc[idx]['file_name']
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in similarity search: {str(e)}")
            return []

def main():
    # Set up paths
    base_dir = Path('Hackathon')
    output_dir = Path('../../embeddings_output')
    
    # Initialize generator
    generator = PDFEmbeddingGenerator(base_dir)
    
    # Process PDFs and generate embeddings
    df = generator.process_all_pdfs()
    
    # Save results
    generator.save_embeddings(df, output_dir)
    
    print(f"Processed {len(df)} chunks from {df['file_name'].nunique()} PDFs")
    print(f"Results saved to {output_dir}")

if __name__ == "__main__":
    main()
