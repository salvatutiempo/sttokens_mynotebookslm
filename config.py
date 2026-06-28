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
def llm_dir(model_id: str) -> Path:
    """Folder where a given LLM is exported (one folder per model)."""
    return MODELS_DIR / f"llm-{model_id.split('/')[-1].lower()}-int4"


# Models selectable from the Streamlit UI (label -> HuggingFace id). Export them
# with `python download_models.py` (default) or pass ids as arguments, e.g.
#   python download_models.py "Qwen/Qwen2.5-1.5B-Instruct"
AVAILABLE_LLMS = {
    "Qwen2.5-0.5B · fast": "Qwen/Qwen2.5-0.5B-Instruct",
    "Qwen2.5-1.5B · quality": "Qwen/Qwen2.5-1.5B-Instruct",
}

# Speed-first default. Changing it requires `python download_models.py`.
LLM_MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
LLM_OV_DIR = llm_dir(LLM_MODEL_ID)

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
MAX_NEW_TOKENS = 256      # hard cap (safety); also drives the word budget below
NO_REPEAT_NGRAM = 3       # block repeated n-grams (small models loop otherwise)
# Guardrail: instruct the model to give a COMPLETE answer within a word budget
# derived from MAX_NEW_TOKENS, so it self-limits instead of being truncated.
# Spanish needs ~1.5-2 tokens/word, so ~0.5 words per token leaves headroom.
ANSWER_WORD_RATIO = 0.5
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
