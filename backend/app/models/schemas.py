# app/models/schemas.py
from pydantic import BaseModel

class QueryRequest(BaseModel):
    prompt: str

class QueryResponse(BaseModel):
    response: str
    detected_language: str