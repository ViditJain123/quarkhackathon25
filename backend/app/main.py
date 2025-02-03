# app/main.py
from fastapi import FastAPI
from .models.schemas import QueryRequest, QueryResponse
from .services.translation_service import TranslationService
from .services.rag_service import RAGService
from .services.llm_service import LlamaService

app = FastAPI()

translation_service = TranslationService()
rag_service = RAGService()
llm_service = LlamaService()

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    # Detect language
    source_lang = translation_service.detect_language(request.prompt)
    
    # Translate to English if needed
    english_prompt = translation_service.translate_to_english(
        request.prompt, source_lang
    )
    
    # Get relevant context using RAG
    context = rag_service.get_relevant_context(english_prompt)
    
    # Generate response using Llama
    english_response = await llm_service.generate_response(
        english_prompt, context
    )
    
    # Translate response back if needed
    final_response = translation_service.translate_from_english(
        english_response, source_lang
    )
    
    return QueryResponse(
        response=final_response,
        detected_language=source_lang
    )