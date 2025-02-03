# Multilingual Insurance RAG System (Quark Hackathon 2025)

## Authors
- Amogh Malagi, Naitik Verma, Ronan Coutinho, Vidit Jain
- Date: 3/10/2025

## Introduction
This project presents a fully open-source, cloud-agnostic multilingual Retrieval-Augmented Generation (RAG) system for insurance documentation. Designed to support multiple Indian languages, the system enables both text and voice-based interactions while ensuring privacy-friendly, cost-effective deployment without reliance on proprietary cloud platforms.
By integrating open-source LLMs (LLaMA) and leveraging FastAPI, FastText, Deep Translate, the system delivers context-aware responses with enhanced accuracy.
This chatbot not only facilitates real-time translation and multilingual conversations, but also supports essential transactional services such as policy inquiries and service requests, making it a practical and scalable solution for the insurance sector.

### Key Features
- Multilingual support for 9 Indian languages
- Voice and text input processing
- PDF document processing and embedding generation
- Context-aware responses using RAG
- Real-time translation

### Tech Stack
- FastAPI for backend
- FastText for embeddings
- Deep Translate for language translation
- LLaMA 3.1 (via Ollama) for response generation
- React for frontend

## Installation & Setup

### Prerequisites
- Python 3.13+
- FastText pre-trained model (cc.en.300.bin)
- Node.js and npm for frontend
- Ollama installed and running

### Installation Steps
1. Clone the repository:
```bash
git clone https://github.com/[username]/quarkhackathon25.git
cd quarkhackathon25
```

2. Create and activate virtual environment:
```bash
python -m venv rag_env
source rag_env/bin/activate  # On Windows: rag_env\Scripts\activate
```

3. Install dependencies:
```bash
pip install fastapi uvicorn pydantic-settings pydantic==2.5.2 deep-translator langdetect PyPDF2 numpy pandas tqdm nltk scikit-learn
```

### Configuration
Create a `.env` file in the root directory:
```env
APP_NAME="Insurance RAG API"
APP_VERSION="1.0.0"
LOG_LEVEL=INFO
LOG_FILE=app.log
```

## Usage Guide

### Running the Project
1. Start the FastAPI server:
```bash
cd backend
uvicorn app.main:app --reload
```

2. Generate embeddings (first time setup):
```bash
python app/services/embedding_service.py
```

### Testing
Test the RAG service:
```bash
python test_rag.py
```

## Architecture Overview

### Directory Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── embedding_service.py
│   │   ├── translation_service.py
│   │   ├── rag_service.py
│   │   ├── llm_service.py
│   │   └── speech_service.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── embeddings_output/
└── models/
```

### Core Components
1. **Embedding Service**: Processes PDFs and generates FastText embeddings
2. **RAG Service**: Handles context retrieval and query processing
3. **Translation Service**: Manages language detection and translation
4. **Speech Service**: Handles voice input/output processing
5. **LLM Service**: Interfaces with LLaMA for response generation

## API Documentation

### Endpoints

#### POST /api/upload
Handles voice input processing
```json
Request:
- FormData with 'file' field (audio/mpeg)

Response:
{
    "audio_content": bytes,
    "detected_language": string
}
```

#### POST /api/query
Handles text input processing
```json
Request:
{
    "prompt": string
}

Response:
{
    "response": string,
    "detected_language": string
}
```

### References
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastText Documentation](https://fasttext.cc/)
- [Google Cloud Translation API](https://cloud.google.com/translate)
- [LLaMA Documentation](https://github.com/facebookresearch/llama)
