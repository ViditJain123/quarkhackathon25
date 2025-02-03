# app/services/llm_service.py
import requests

class LlamaService:
    def __init__(self):
        self.api_url = "http://localhost:11434/api/generate"
        
    async def generate_response(self, prompt: str, context: str) -> str:
        full_prompt = f"""Context: {context}\n\nQuestion: {prompt}\n\nAnswer:"""
        
        response = requests.post(
            self.api_url,
            json={
                "model": "llama2",
                "prompt": full_prompt,
                "stream": False
            }
        )
        return response.json()['response']