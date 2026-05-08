#!/usr/bin/env python3
import time
import logging
from memory_engine.llm.orchestrator import LLMOrchestrator
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

logging.info("Loading Semantic Similarity Model (MiniLM)...")
sim_tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
sim_model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
sim_model.eval()

def calculate_similarity(text1, text2):
    """Calculates semantic similarity using PyTorch and MiniLM embeddings."""
    if not text1 or not text2:
        return 0.0
        
    def get_embedding(text):
        inputs = sim_tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = sim_model(**inputs)
        attention_mask = inputs['attention_mask']
        token_embeddings = outputs[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        embedding = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        return F.normalize(embedding, p=2, dim=1)

    emb1 = get_embedding(text1)
    emb2 = get_embedding(text2)
    return F.cosine_similarity(emb1, emb2).item()

def main():
    try:
        with open("txt.txt", "r") as f:
            queries = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logging.error("txt.txt not found. Please provide a file with test queries.")
        return

    logging.info("Initializing LLM Orchestrator...")
    orchestrator = LLMOrchestrator()
    session_id = "eval_session"

    results = []

    for idx, query in enumerate(queries):
        logging.info(f"Evaluating Query {idx + 1}: {query[:50]}...")

        # --- Method A Evaluation ---
        res_a = orchestrator.generate_method_a(session_id, query)
        output_a = res_a["response"]
        latency_a = res_a["latency_ms"]
        vram_delta_a = res_a["vram_delta"]

        # --- Method B Evaluation ---
        res_b = orchestrator.generate_method_b(session_id, query)
        output_b = res_b["response"]
        latency_b = res_b["latency_ms"]
        vram_delta_b = res_b["vram_delta"]

        # --- Output Similarity ---
        similarity = calculate_similarity(output_a, output_b)

        results.append({
            "Query ID": idx + 1,
            "Latency A (ms)": f"{latency_a:.2f}",
            "Latency B (ms)": f"{latency_b:.2f}",
            "VRAM Delta (GB)": f"{abs(vram_delta_b):.2f}",
            "Similarity": f"{similarity:.2%}"
        })

    # Output formatted Markdown table
    print("\n## Evaluation Metrics\n")
    print("| Query ID | Latency A (ms) | Latency B (ms) | VRAM Delta (GB) | Output Similarity |")
    print("|----------|----------------|----------------|-----------------|-------------------|")
    for r in results:
        print(f"| {r['Query ID']} | {r['Latency A (ms)']} | {r['Latency B (ms)']} | {r['VRAM Delta (GB)']} | {r['Similarity']} |")

if __name__ == "__main__":
    main()
