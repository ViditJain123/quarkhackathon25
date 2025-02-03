# app/services/llm_service.py
import requests

class LlamaService:
    
        
        
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
    
import os
import json
from typing import List
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.memory import ConversationBufferMemory
import nest_asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
import pickle
import atexit
from ollama import chat
from ollama import ChatResponse


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Apply nest_asyncio if needed
nest_asyncio.apply()   

app = FastAPI()


user_memories = {}
memory_file_path = 'user_memories.pkl'
file_path = 'user_prompts.json'  # Ensure this is defined before usage


def load_user_memories():
    global user_memories
    if os.path.exists(memory_file_path):
        with open(memory_file_path, 'rb') as f:
            user_memories = pickle.load(f)
            logging.info("User memories loaded from disk.")
    else:
        user_memories = {}
        logging.info("No existing user memories found. Starting fresh.")

def save_user_memories():
    with open(memory_file_path, 'wb') as f:
        pickle.dump(user_memories, f)
        logging.info("User memories saved to disk.")

# Load user memories at startup
load_user_memories()

# Save user memories on shutdown
atexit.register(save_user_memories)

def generate_response(user_id, question):
    """
    Generate a response using Gemini's GenerativeModel with the relevant context and user memory.
    """
    # Retrieve or initialize user memory
    if user_id not in user_memories:
        user_memories[user_id] = ConversationBufferMemory(memory_key='chat_history', k=5, return_messages=True)
    
    memory = user_memories[user_id]
    
    # Retrieve conversation history
    chat_history = memory.load_memory_variables({"input": question})
    messages = chat_history.get('chat_history', [])
    
    # Format the conversation history
    history_text = ""
    for msg in messages:
        if msg.type == "human":
            history_text += f"User: {msg.content}\n"
        elif msg.type == "ai":
            history_text += f"Assistant: {msg.content}\n"
    
    # Retrieve relevant context from vector store 
    # context = get_relevant_context(question)
    context = "Ronan is a good boy"
    logging.info(f"Retrieved context for user {user_id}: {context}")
    
    # Construct the prompt with user history and current question
    prompt = f"""
    You are an assistant for answering questions based on the context provided.
    Answer concisely and only based on the context provided.

    Context:
    {context}

    Conversation History:
    {history_text}

    User: {question}

    Assistant:
    """
    print(prompt)
    
    
    try:
        # Generate the response
        # response = model.generate_content(prompt)
        response: ChatResponse = chat(model='llama3.2', messages=[
        {
            'role': 'user',
            'content': question,
        },
        ])
        # r = response.message.content
        answer = response['message']['content']
        # answer = r.text.strip()
    except Exception as e:
        logging.error(f"Error generating response with Gemini: {e}")
        raise e
    
    # Update conversation memory
    memory.save_context({"input": question}, {"output": answer})
    
    return answer

def load_data():
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            for user_id in data:
                date_str, count = data[user_id]
                data[user_id] = (datetime.strptime(date_str, '%Y-%m-%d').date(), count)
            return data
    except FileNotFoundError:
        return {}  # Return an empty dictionary if file doesn't exist

def save_data(data):
    # Convert the date object to a string for JSON serialization
    data_to_save = {user_id: (date.strftime('%Y-%m-%d'), count) for user_id, (date, count) in data.items()}
    with open(file_path, 'w') as f:
        json.dump(data_to_save, f)

user_prompts = load_data()