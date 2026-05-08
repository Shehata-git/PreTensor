= Methodology

== Preprocessing Pipeline

The preprocessing stage leverages the `spaCy` natural language processing library to execute deterministic token contraction. The pipeline implements aggressive lemmatization, stop-word removal, and punctuation stripping. Crucially, this deterministic approach is engineered to preserve named entities and domain-specific terminology, ensuring that the semantic core of the RAG payload remains intact while eliminating superfluous syntactic elements @jiang2023llmlingua.

== Dual-Pipeline Workflow

To empirically measure the efficacy of the token contraction, a "Dual-Pipeline" A/B testing environment was engineered. This environment is orchestrated via a Wayland-native GTK3 graphical interface. 
- *Method A (Baseline):* Passes raw, uncompressed retrieval chunks directly from the Qdrant vector database to the LLM.
- *Method B (Optimized):* Intercepts the Qdrant retrieval chunks and routes them through the NLP-optimized token contraction pipeline before passing the condensed payload to the LLM.

== Telemetry and Measurement

Accurate evaluation requires precise measurement of computational overhead. Custom Delta-measurement telemetry was developed to isolate and quantify the Key-Value (KV) cache costs. This telemetry directly interfaces with `nvidia-smi` to capture pure VRAM utilization. Furthermore, the `torch.cuda` cache is explicitly flushed between experimental runs to prevent memory state contamination and ensure isolated, reproducible measurements.
