import os
from dotenv import load_dotenv
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import gc
import time
import re
from typing import List, Dict, Any
from memory_engine.db.sqlite_client import SQLiteClient
from memory_engine.pipeline import SemanticPipeline

# Load environment variables for gated repo access
load_dotenv()

class LLMOrchestrator:
    def __init__(self, model_id: str = "google/gemma-3-4b-it", db_path: str = "memory.db"):
        self.sqlite = SQLiteClient(db_path)
        self.pipeline = SemanticPipeline()
        hf_token = os.getenv("HF_TOKEN")
        
        # 1. 4-Bit Quantization Config
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True
        )

        # 2. Native Model & Tokenizer Load
        print(f"// LOADING_NATIVE_ENGINE: {model_id}")
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_id, 
            token=hf_token
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
            token=hf_token
        )
        print("// ENGINE_ONLINE: READY")

    def warm_up_ollama(self) -> bool:
        """Compatibility shim for GUI"""
        return True

    def get_vram_usage(self) -> float:
        """Query physical VRAM usage in GB"""
        try:
            import subprocess
            res = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,nounits,noheader"],
                encoding="utf-8"
            )
            return float(res.strip()) / 1024.0
        except Exception:
            return 0.0

    def _generate_native(self, prompt: str) -> Dict[str, Any]:
        """
        Internal generation logic with Cache Clearing and VRAM Delta Capture.
        """
        # A. Clear Cache to isolate this specific generation
        torch.cuda.empty_cache()
        gc.collect()
        vram_before = self.get_vram_usage()
        
        # B. Tokenize and Generate
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        start_time = time.time()
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=256,
                do_sample=True,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        end_time = time.time()
        vram_after = self.get_vram_usage()
        
        # C. Decode and calculate metrics
        response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        tokens_gen = outputs.shape[1] - inputs.input_ids.shape[1]
        
        return {
            "response": response,
            "latency_ms": (end_time - start_time) * 1000,
            "vram_gb": vram_after, # We report the absolute peak for the telemetry
            "vram_delta": vram_after - vram_before,
            "tokens": tokens_gen
        }

    def _assemble_prompt(self, session_id: str, prompt: str, relevant_chunks: List[str], optimized: bool = False) -> str:
        all_history = self.sqlite.get_messages(session_id)
        history_str = ""
        total_msg = len(all_history)
        
        for i, m in enumerate(all_history):
            role = "User" if m['role'] == 'user' else "Assistant"
            content = m['content']
            if optimized and i < total_msg - 1:
                cleaned = self.pipeline.cleaner.clean_text(content)
                history_str += f"{role} (MIN): {cleaned}\n"
            else:
                history_str += f"{role}: {content}\n"

        chunks_str = "\n".join([f"- {c}" for c in relevant_chunks]) if relevant_chunks else "None"

        # Note: Using standard Gemma-style format
        final_prompt = (
            f"<start_of_turn>user\n"
            f"RELEVANT_MEMORY:\n{chunks_str}\n\n"
            f"HISTORY:\n{history_str}\n"
            f"QUERY: {prompt}<end_of_turn>\n"
            f"<start_of_turn>model\n"
        )
        return final_prompt

    def generate_method_a(self, session_id: str, prompt: str) -> Dict[str, Any]:
        all_history = self.sqlite.get_messages(session_id)
        relevant_chunks = self.pipeline.retrieve_relevant(prompt, limit=5)
        full_prompt = self._assemble_prompt(session_id, prompt, relevant_chunks, optimized=False)
        return self._generate_native(full_prompt)

    def generate_method_b(self, session_id: str, prompt: str) -> Dict[str, Any]:
        all_history = self.sqlite.get_messages(session_id)
        relevant_chunks = self.pipeline.retrieve_relevant(prompt, limit=5)
        full_prompt = self._assemble_prompt(session_id, prompt, relevant_chunks, optimized=True)
        return self._generate_native(full_prompt)

    def store_interaction(self, session_id: str, prompt: str, response: str):
        self.sqlite.add_message(session_id, "user", prompt)
        self.sqlite.add_message(session_id, "assistant", response)
        self.pipeline.process_and_store(session_id, prompt)
        self.pipeline.process_and_store(session_id, response)

    def summarize_session(self, prompt: str) -> str:
        """
        Generate a short title for the session based on the first prompt.
        """
        summary_prompt = (
            f"<start_of_turn>user\n"
            f"Summarize the following user query into a concise 3-5 word title. "
            f"Output ONLY the title text, no quotes, no prefix.\n\n"
            f"QUERY: {prompt}<end_of_turn>\n"
            f"<start_of_turn>model\n"
        )
        
        # We use a direct call here to bypass _generate_native, ensuring
        # summary tokens are not counted in the chat telemetry.
        inputs = self.tokenizer(summary_prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=32,
                do_sample=False, # Deterministic for titles
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        title = response.strip()
        
        # Post-processing: remove quotes, trailing dots, and "Title: " prefix if present
        title = re.sub(r'^["\']|["\']$', '', title)
        title = re.sub(r'(?i)^title:\s*', '', title)
        title = title.rstrip('.')
        
        # If the model fails or returns empty, fallback to a timestamped title
        if not title:
            title = f"SESSION_{time.strftime('%H%M%S')}"
            
        return title.upper()
