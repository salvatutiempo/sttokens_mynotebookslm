"""Central configuration for the offline NotebookLM.

A single place to tune models, paths and RAG parameters.
Targeted at an Intel N100/N300 (4-8 cores, no dedicated GPU, ~16 GB of RAM).
"""

from os import environ
from pathlib import Path

# --- Paths -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "documents"            # your .txt, .md and .pdf files
# Models can be large; on a NAS (small system disk) point this to a big volume
# with:  export NOTEBOOKLM_MODELS_DIR=/mnt/pool/models
MODELS_DIR = Path(environ.get("NOTEBOOKLM_MODELS_DIR", BASE_DIR / "models"))
INDEX_DIR = BASE_DIR / "storage" / "faiss_index"  # persistent vector index

# --- Language model (SLM) ----------------------------------------------------
# Speed-first default: Qwen2.5-0.5B-Instruct flies on an N100 (INT4 ~0.4 GB).
# For better answers (slower) switch to "Qwen/Qwen2.5-1.5B-Instruct" or 3B.
# NOTE: changing this requires re-running `python download_models.py` (each
# model is exported into its own folder, derived from the name below).
LLM_MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
LLM_OV_DIR = MODELS_DIR / f"llm-{LLM_MODEL_ID.split('/')[-1].lower()}-int4"

# --- Embeddings model --------------------------------------------------------
# multilingual-e5-small: lightweight (~118M) and multilingual (includes Spanish).
EMBED_MODEL_ID = "intfloat/multilingual-e5-small"
EMBED_OV_DIR = MODELS_DIR / "embed-ov"

# --- Hardware ----------------------------------------------------------------
# "CPU" is the most stable. You may try "GPU" (iGPU UHD) or "AUTO".
DEVICE = "CPU"
# OpenVINO runtime tuning for the LLM (single-stream latency on CPU).
# If model loading ever fails, get_llm() falls back to simpler configs.
LLM_OV_CONFIG = {
    "PERFORMANCE_HINT": "LATENCY",
    "KV_CACHE_PRECISION": "u8",            # smaller KV cache -> less bandwidth
    "DYNAMIC_QUANTIZATION_GROUP_SIZE": "32",
}

# --- Generation --------------------------------------------------------------
MAX_NEW_TOKENS = 256      # keep answers short -> much lower latency on CPU
# Prompt-lookup decoding can speed up RAG generation (it reuses n-grams from the
# context). It is experimental on stateful OpenVINO models, so it is OFF by
# default. Set to e.g. 10 to try it; if generation errors, set back to 0.
PROMPT_LOOKUP = 0

# --- Embeddings / ingestion --------------------------------------------------
EMBED_BATCH_SIZE = 16     # bigger batches = faster ingestion (more RAM)
PDF_FAST = False          # True: skip table detection -> much faster big PDFs

# --- RAG parameters ----------------------------------------------------------
CHUNK_SIZE = 1000         # characters per chunk (fewer chunks = faster ingest)
CHUNK_OVERLAP = 120       # overlap between chunks
RETRIEVER_K = 3           # number of chunks retrieved per question
