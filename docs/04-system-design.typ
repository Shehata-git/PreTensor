= System Design and Interface Explanation

== Backend Architecture

The backend infrastructure is built upon a Python-based orchestrator that manages the flow of data between the retrieval systems and the inference engine. Qdrant is employed as the vector database for managing high-dimensional embeddings and executing rapid similarity searches. An SQLite registry is integrated into the architecture to provide robust session archiving and historical data persistence. The language model inference is powered by an Ollama and `llama.cpp` backend, optimized for local execution.

== Frontend Interface

The user interface is a Wayland-native GTK3 application, developed utilizing `PyGObject`. It provides real-time control and monitoring of the A/B testing environment. The interface design employs a custom CSS-injected "Brutalist" aesthetic, featuring a dark mode color palette that emphasizes functional data visualization and telemetry readouts over ornamental design.
