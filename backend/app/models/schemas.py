# app/models/schemas.py
from pydantic import BaseModel
from typing import Optional
from fastapi import UploadFile

class QueryRequest(BaseModel):
    prompt: Optional[str] = None
    
    class Config:
        from_attributes = True

class AudioResponse(BaseModel):
    audio_content: bytes
    detected_language: str
