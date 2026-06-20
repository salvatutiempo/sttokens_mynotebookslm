"""Central configuration for the offline NotebookLM.

A single place to tune models, paths and RAG parameters.
Targeted at an Intel N100 (4 cores, no dedicated GPU, 8-16 GB of RAM).
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
# Qwen2.5-1.5B-Instruct: ideal quality/size balance for the N100.
# It is recent, multilingual (answers well in Spanish) and ~1 GB in INT4.
# Alternatives:
#   - "Qwen/Qwen2.5-0.5B-Instruct"        -> lighter/faster, lower quality.
#   - "Qwen/Qwen2.5-3B-Instruct"          -> better quality, slower (16 GB N100).
#   - "meta-llama/Llama-3.2-3B-Instruct"  -> good quality, heavier/slower.
LLM_MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"
LLM_OV_DIR = MODELS_DIR / "llm-ov-int4"

# --- Embeddings model --------------------------------------------------------
# multilingual-e5-small: lightweight (~118M) and multilingual (includes Spanish).
EMBED_MODEL_ID = "intfloat/multilingual-e5-small"
EMBED_OV_DIR = MODELS_DIR / "embed-ov"

# --- Hardware ----------------------------------------------------------------
# "CPU" is the most stable on the N100. You may try "GPU" (iGPU UHD) or "AUTO".
DEVICE = "CPU"

# --- RAG parameters ----------------------------------------------------------
CHUNK_SIZE = 800          # characters per chunk
CHUNK_OVERLAP = 120       # overlap between chunks
RETRIEVER_K = 4           # number of chunks retrieved per question
MAX_NEW_TOKENS = 512      # maximum answer length
