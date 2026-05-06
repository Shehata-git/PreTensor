import os
import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer
from huggingface_hub import hf_hub_download
from typing import List

class ONNXEmbedder:
    def __init__(self, model_repo: str = "nomic-ai/nomic-embed-text-v1.5", cache_dir: str = "model_cache"):
        self.model_repo = model_repo
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.tokenizer = AutoTokenizer.from_pretrained("nomic-ai/nomic-embed-text-v1.5")
        self.model_path = self._ensure_model()
        
        # Force CPU execution as per specification
        self.session = ort.InferenceSession(
            self.model_path, 
            providers=['CPUExecutionProvider']
        )

    def _ensure_model(self) -> str:
        # nomic-embed-text-v1.5 usually has an onnx subfolder or specific filename
        # We'll pull the standard model.onnx (or equivalent)
        # Note: nomic-embed-text-v1.5 on HF often has 'onnx/model.onnx'
        try:
            return hf_hub_download(
                repo_id=self.model_repo,
                filename="onnx/model.onnx",
                cache_dir=self.cache_dir
            )
        except Exception:
            # Fallback for different repo structures if necessary
            return hf_hub_download(
                repo_id=self.model_repo,
                filename="model.onnx",
                cache_dir=self.cache_dir
            )

    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]
        input_mask_expanded = np.expand_dims(attention_mask, -1).astype(float)
        return np.sum(token_embeddings * input_mask_expanded, 1) / np.clip(input_mask_expanded.sum(1), a_min=1e-9, a_max=None)

    def embed(self, text: str) -> List[float]:
        # Prefix required by nomic-embed-text for specific tasks
        # For clustering/retrieval: "search_document: "
        # For queries: "search_query: "
        # We'll use document prefix for storage
        prefix = "search_document: "
        full_text = prefix + text
        
        encoded_input = self.tokenizer(
            [full_text], 
            padding=True, 
            truncation=True, 
            return_tensors='np'
        )
        
        inputs_onnx = {
            "input_ids": encoded_input["input_ids"].astype(np.int64),
            "attention_mask": encoded_input["attention_mask"].astype(np.int64)
        }
        
        # Token type ids might be required depending on the specific model export
        if "token_type_ids" in encoded_input:
            inputs_onnx["token_type_ids"] = encoded_input["token_type_ids"].astype(np.int64)

        outputs = self.session.run(None, inputs_onnx)
        
        # Perform mean pooling
        embeddings = self.mean_pooling(outputs, encoded_input["attention_mask"])
        
        # Normalize embeddings
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / norms
        
        return embeddings[0].tolist()
