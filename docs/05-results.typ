= Results and Evaluation

== Latency (Time-to-First-Token)

Empirical testing with massive RAG payloads demonstrated a substantial performance advantage for Method B (the NLP-contracted pipeline). By drastically reducing the total token payload prior to inference, the time required for prefill computation was significantly diminished. This resulted in an accelerated Time-to-First-Token (TTFT) and an overall reduction in inference latency compared to the baseline Method A. While Ollama provides a highly performant backend for this showcase, its memory allocation strategies required careful analysis to fully contextualize these latency gains.

== The Pre-Allocation Paradox

Despite the significant reductions in compute time and token velocity, profiling revealed a constraint within the memory management architecture. It was discovered that `llama.cpp` (and by extension, Ollama) statically pre-allocates the KV cache in large pages upon initialization. Consequently, the physical VRAM footprint remained entirely static at 3.80 GB, regardless of the token contraction applied to the input payload. Because Ollama precaches these large pages for the KV cache, it does not allow the architectural savings in token volume to manifest as dynamic VRAM reduction. Achieving actual memory reclamation requires dynamic cache allocators, such as the `DynamicCache` implemented in Hugging Face `transformers` or PagedAttention mechanisms @kwon2023efficient.

== Architectural Comparison: PreTensor vs. Agentic Caveman Skills

The PreTensor architecture presents a complementary approach to contemporary optimization paradigms, most notably the trend of "Caveman" agentic prompting (e.g., Caveman Claude). 
- *Agentic Caveman Skills* aggressively compress the LLM's *output* and tool-use syntax to minimize operational burn and token velocity during generation.
- *Project PreTensor* operates inversely. It compresses the *input* RAG payload before inference begins, directly optimizing the prefill phase and reducing the semantic payload that the model must initially process.

Both methodologies address opposite ends of the inference pipeline, forming necessary halves of a highly optimized, end-to-end local AI workflow.
