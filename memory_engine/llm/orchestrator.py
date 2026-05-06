import requests
import json
from typing import List, Dict, Any
from memory_engine.db.sqlite_client import SQLiteClient
from memory_engine.pipeline import SemanticPipeline

class LLMOrchestrator:
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "gemma3:4b", db_path: str = "memory.db"):
        self.ollama_url = ollama_url
        self.model = model
        self.sqlite = SQLiteClient(db_path)
        self.pipeline = SemanticPipeline()

    def _call_ollama(self, prompt: str) -> str:
        url = f"{self.ollama_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            return f"Error calling Ollama: {str(e)}"

    def generate_method_a(self, session_id: str, prompt: str, history_limit: int = 10) -> str:
        """
        Method A: Standard (pulls last N raw messages from SQLite).
        """
        history = self.sqlite.get_messages(session_id, limit=history_limit)
        
        context_str = "\n".join([f"{m['role']}: {m['content']}" for m in history])
        
        full_prompt = f"Context history:\n{context_str}\n\nUser: {prompt}\nAssistant:"
        
        return self._call_ollama(full_prompt)

    def generate_method_b(self, session_id: str, prompt: str, semantic_limit: int = 5) -> str:
        """
        Method B: Semantic (pulls top K relevant chunks from Qdrant).
        """
        relevant_chunks = self.pipeline.retrieve_relevant(prompt, limit=semantic_limit, session_id=None) # Global search or session? Spec says "pulls top K relevant chunks from Qdrant based on the current prompt".
        
        context_str = "\n".join([f"Past interaction: {chunk}" for chunk in relevant_chunks])
        
        full_prompt = f"Semantic Context:\n{context_str}\n\nUser: {prompt}\nAssistant:"
        
        return self._call_ollama(full_prompt)

    def store_interaction(self, session_id: str, prompt: str, response: str):
        """
        Stores the interaction in both SQLite and Qdrant.
        """
        # Store in SQLite
        self.sqlite.add_message(session_id, "user", prompt)
        self.sqlite.add_message(session_id, "assistant", response)
        
        # Store in Qdrant (via pipeline)
        self.pipeline.process_and_store(session_id, prompt)
        self.pipeline.process_and_store(session_id, response)
