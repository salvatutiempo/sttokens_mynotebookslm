"""Configuración central del NotebookLM offline.

Un único lugar para ajustar modelos, rutas y parámetros del RAG.
Pensado para un Intel N100 (4 núcleos, sin GPU dedicada, 8-16 GB de RAM).
"""

from pathlib import Path

# --- Rutas -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "documents"          # tus .txt, .md y .pdf
MODELS_DIR = BASE_DIR / "models"                # modelos exportados a OpenVINO
INDEX_DIR = BASE_DIR / "storage" / "faiss_index"  # índice vectorial persistente

# --- Modelo de lenguaje (SLM) ------------------------------------------------
# Qwen2.5-1.5B-Instruct: equilibrio calidad/peso ideal para la N100.
# Es reciente, multilingüe (responde bien en español) y en INT4 ocupa ~1 GB.
# Alternativas:
#   - "Qwen/Qwen2.5-0.5B-Instruct"  -> más ligero/rápido, menor calidad.
#   - "meta-llama/Llama-3.2-3B-Instruct" -> mejor calidad, más lento/pesado.
LLM_MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"
LLM_OV_DIR = MODELS_DIR / "llm-ov-int4"

# --- Modelo de embeddings ----------------------------------------------------
# multilingual-e5-small: ligero (~118M) y multilingüe (incluye español).
EMBED_MODEL_ID = "intfloat/multilingual-e5-small"
EMBED_OV_DIR = MODELS_DIR / "embed-ov"

# --- Hardware ----------------------------------------------------------------
# "CPU" es lo más estable en la N100. Puedes probar "GPU" (iGPU UHD) o "AUTO".
DEVICE = "CPU"

# --- Parámetros del RAG ------------------------------------------------------
CHUNK_SIZE = 800          # caracteres por fragmento
CHUNK_OVERLAP = 120       # solapamiento entre fragmentos
RETRIEVER_K = 4           # nº de fragmentos recuperados por pregunta
MAX_NEW_TOKENS = 512      # longitud máxima de la respuesta
