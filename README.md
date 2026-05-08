# Project PreTensor

## Overview

Project PreTensor is an optimization pipeline designed to reduce inference latency and mitigate context overflow in local Large Language Model (LLM) Retrieval-Augmented Generation (RAG). By applying a deterministic, pre-tensor token contraction algorithm, the system aggressively reduces the semantic payload before it hits the LLM context window, lowering Time-to-First-Token (TTFT) without degrading output quality.

## Prerequisites & Environment
>
> **IMPORTANT NOTICE**
> The graphical interface for this project is built using a native Wayland/GTK3 environment via `PyGObject` on Void Linux.
> **This project is NOT designed to compile or run natively on Windows or macOS.**

### Distro Generalization & VM Recommendation

If you are evaluating this project on a non-Linux machine or require distro generalization, it is strongly recommended that you provision a **Ubuntu Linux Virtual Machine** using VirtualBox or VMware to execute the codebase.

## Setup & Installation

This project strictly utilizes `uv` for lightning-fast Python dependency management. Do not use legacy `pip` or bare Python commands.

1. **Install `uv` (if not already installed on Ubuntu VM):**

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Sync dependencies from pyproject.toml:**

   ```bash
   uv sync
   ```

3. **Prepare the Evaluation Data:**
   Edit the `txt.txt` file in the root directory. Ensure that each line in the file represents a single turn or query to be evaluated by the headless script.

4. **Run the headless evaluation script:**

   ```bash
   uv run scripts/headless_eval.py
   ```

5. **Run the Graphical Interface:**

   Note: Requires a Wayland/GTK3 environment

   ```bash
   uv run main.py
   ```
