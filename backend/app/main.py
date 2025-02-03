# app/main.py
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from app.models.schemas import AudioResponse, TextResponse, QueryRequest  
from app.services.rag_service import RAGService
from app.services.llm_service import LlamaService
from app.services.speech_service import SpeechService
from app.services.translation_service import TranslationService
from app.utils.helpers import handle_error, timer_decorator, validate_language_code
from app.config import settings
import logging

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
translation_service = TranslationService()
rag_service = RAGService()
llm_service = LlamaService()
speech_service = SpeechService()

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

@app.post("/api/upload", response_model=AudioResponse)
@handle_error
@timer_decorator
async def process_audio_upload(
    file: UploadFile = File(...)
):
    """Process audio upload from frontend"""
    logger.info(f"Received audio upload: {file.filename}")
    
    # Validate file type
    if file.content_type != 'video/mp4':
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only MP4 files are accepted."
        )
    
    try:
        # Read audio content
        audio_content = await file.read()
        
        # Convert speech to text
        transcript = await speech_service.speech_to_text(audio_content)
        logger.info(f"Transcribed text: {transcript[:100]}...")
        
        # Detect language
        source_lang = translation_service.detect_language(transcript)
        if not validate_language_code(source_lang):
            raise HTTPException(
                status_code=400,
                detail=f"Language {source_lang} is not supported"
            )
        
        # Process query
        english_prompt = translation_service.translate_to_english(
            transcript, source_lang
        )
        context = rag_service.get_relevant_context(english_prompt)
        english_response = await llm_service.generate_response(english_prompt, context)
        final_response = translation_service.translate_from_english(
            english_response, source_lang
        )
        
        # Convert response to speech
        audio_response = await speech_service.text_to_speech(
            final_response, source_lang
        )
        
        return AudioResponse(
            audio_content=audio_response,
            detected_language=source_lang
        )
        
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing audio: {str(e)}"
        )

@app.post("/api/query", response_model=TextResponse)
@handle_error
@timer_decorator
async def process_text_query(request: QueryRequest):
    """Process text query"""
    if not request.prompt:
        raise HTTPException(
            status_code=400,
            detail="Text prompt is required"
        )
    
    logger.info(f"Received text query: {request.prompt[:100]}...")
    
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
    
    return TextResponse(
        response=final_response,
        detected_language=source_lang
    )

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }