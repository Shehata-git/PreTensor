import requests
import json
import time
import re
from typing import List, Dict, Any
from memory_engine.db.sqlite_client import SQLiteClient
from memory_engine.pipeline import SemanticPipeline

class LLMOrchestrator:
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "gemma3:4b", db_path: str = "memory.db"):
        self.ollama_url = ollama_url
        self.model = model
        self.sqlite = SQLiteClient(db_path)
        self.pipeline = SemanticPipeline()

    def clean_llm_text(self, raw_text: str) -> str:
        """
        Quadruple-stage decoding chain to fix literal escapes and mojibake simultaneously.
        """
        if not raw_text:
            return ""
            
        try:
            # Combined chain: UTF-8 Encode -> Unicode Escape Decode -> Latin1 Encode -> UTF-8 Decode
            # This handles cases with literal \uXXXX AND UTF-8 misinterpretation.
            return raw_text.encode('utf-8').decode('unicode_escape').encode('latin1').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            try:
                # Fallback 1: Just unicode_escape
                return raw_text.encode('utf-8').decode('unicode_escape')
            except Exception:
                try:
                    # Fallback 2: Just mojibake fix
                    return raw_text.encode('latin1').decode('utf-8')
                except Exception:
                    # Final resort: Return as is
                    return raw_text

    def _call_ollama(self, prompt: str) -> str:
        url = f"{self.ollama_url}/api/generate"
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.encoding = 'utf-8'
            response.raise_for_status()
            
            data = response.json()
            raw_response = data.get("response", "")
            
            return self.clean_llm_text(raw_response)
        except Exception as e:
            return f"Error calling Ollama: {str(e)}"

    def summarize_session(self, first_msg: str) -> str:
        prompt = f"Summarize this query into exactly 3 words to use as a title. Query: {first_msg}\nTitle:"
        title = self._call_ollama(prompt).strip().replace('"', '')
        words = title.split()[:3]
        return " ".join(words) if words else "New Session"

    def _assemble_prompt(self, session_id: str, prompt: str, relevant_chunks: List[str]) -> str:
        history = self.sqlite.get_messages(session_id, limit=3)
        history_str = ""
        for m in history:
            role = "User" if m['role'] == 'user' else "Assistant"
            history_str += f"{role}: {m['content']}\n"

        chunks_str = "\n".join([f"- {c}" for c in relevant_chunks]) if relevant_chunks else "No relevant background memory found."

        final_prompt = (
            "SYSTEM: You are a helpful, precise AI assistant. Use the background memory to inform your answers, "
            "but do NOT assume the user just said the things in the background memory.\n\n"
            f"<background_memory>\n{chunks_str}\n</background_memory>\n\n"
            f"<current_conversation>\n{history_str}"
            f"User: {prompt}\n"
            "</current_conversation>\n"
            "Assistant:"
        )
        return final_prompt

    def generate_method_a(self, session_id: str, prompt: str, semantic_limit: int = 5) -> str:
        history = self.sqlite.get_messages(session_id)
        if len(history) < 3:
            relevant_chunks = []
        else:
            relevant_chunks = self.pipeline.retrieve_relevant(prompt, limit=semantic_limit, session_id=None)
        full_prompt = self._assemble_prompt(session_id, prompt, relevant_chunks)
        return self._call_ollama(full_prompt)

    def generate_method_b(self, session_id: str, prompt: str, semantic_limit: int = 5) -> str:
        history = self.sqlite.get_messages(session_id)
        relevant_chunks = []
        if len(history) >= 3:
            cleaned_query = self.pipeline.cleaner.clean_text(prompt)
            query_to_use = cleaned_query if cleaned_query.strip() else prompt
            relevant_chunks = self.pipeline.retrieve_relevant(query_to_use, limit=semantic_limit, session_id=None)
        full_prompt = self._assemble_prompt(session_id, prompt, relevant_chunks)
        return self._call_ollama(full_prompt)

    def store_interaction(self, session_id: str, prompt: str, response: str):
        self.sqlite.add_message(session_id, "user", prompt)
        self.sqlite.add_message(session_id, "assistant", response)
        self.pipeline.process_and_store(session_id, prompt)
        self.pipeline.process_and_store(session_id, response)
