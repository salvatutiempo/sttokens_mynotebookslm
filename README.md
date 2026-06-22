## Offline NotebookLM in a Cheap Intel device

A minimal, fully local NotebookLM clone: ask natural-language questions about  
your own documents (**text, Markdown and PDF**) **without an internet**  
**connection**, using a small language model (**SLM**) accelerated with  
**OpenVINO** on an **Intel N100**. Everything is orchestrated with **LangChain**  
using a RAG (_Retrieval-Augmented Generation_) pattern.

\> After the initial one-time model download, the system runs 100% offline.  
\> Your documents never leave the machine.

## Why these choices?

| Piece | Choice | Reason |
| --- | --- | --- |
| **SLM** | `Qwen2.5-0.5B-Instruct` (INT4) | Speed-first default: flies on an N100 (~0.4 GB). Switch to 1.5B/3B for more quality. |
| **Acceleration** | **OpenVINO** | Intel's runtime; squeezes the 4-8 cores (and optionally the iGPU) of the N-series. |
| **Embeddings** | `multilingual-e5-small` | Lightweight (~118 M) and multilingual, also via OpenVINO. |
| **Vector store** | **FAISS** | Local, server-less, no external dependencies; indexed incrementally. |
| **Orchestration** | **LangChain** | Wires document loading, retrieval and embeddings with little code. |

The **Intel N series** are usually low power CPs with no dedicated GPU. The key to making  
an LLM usable is: **small model + INT4 quantization + OpenVINO**.

PDFs are extracted with **PyMuPDF4LLM**, which converts even **tables to**  
**Markdown** (in C++, fast and light on RAM); if it is not installed, the code  
falls back to `PyPDFLoader`.

\> **Design note.** Unlike the usual approaches (Ollama or llama.cpp with GGUF  
\> models, where OpenVINO is used only for the _embeddings_ or as an optional  
\> backend), here **the SLM itself runs on OpenVINO** through `optimum-intel` in  
\> INT4. This uses Intel's runtime end to end, which is exactly the goal on an  
\> N100.

## What runs what? (engine and models)

This is the most common point of confusion if you come from Ollama, so let's be  
explicit.

### The engine: OpenVINO (not Ollama, not llama.cpp)

The SLM is **not** run by Ollama or llama.cpp. It is loaded and executed by the  
**OpenVINO Runtime**, called from Python. The chain of pieces is:

```plaintext
LangChain  →  optimum-intel (OVModelForCausalLM)  →  OpenVINO Runtime  →  N100 CPU/iGPU
(orchestrates)      (loads the model)                   (does the math)
```

Key differences vs. an Ollama / llama.cpp setup:

|   | Ollama / llama.cpp | **This project** |
| --- | --- | --- |
| Engine that runs the SLM | Ollama or llama.cpp | **OpenVINO** (via `optimum-intel`) |
| Model format | GGUF (`.gguf`) | **OpenVINO IR** (`.xml` + `.bin`) |
| Separate server process? | Yes (`ollama serve` / `llama-server`) | **No** — the model loads inside the Python process |
| Who prepares it | you `ollama pull` | `download_models.py` exports to IR |

There is **no Ollama and no llama.cpp** anywhere in `requirements.txt`.

### The models: two of them (a RAG always needs two)

They do two different jobs:

| Model | Job | Used here | Size |
| --- | --- | --- | --- |
| **Embeddings** | Turns text into vectors to **search** for the relevant chunk | `multilingual-e5-small` | ~118 M (~120 MB) |
| **SLM (LLM)** | **Writes the answer** from the retrieved chunks | `Qwen2.5-1.5B-Instruct` | ~1 GB in INT4 |

Think of it as a library: the **embeddings** model is the _librarian_ that finds  
the right page; the **SLM** is the one that reads that page and writes your  
answer. That is why `download_models.py` downloads **two** things (you will see  
two folders under `models/`: `llm-ov-int4` and `embed-ov`), and **both run on**  
**OpenVINO**.

## Architecture (RAG in one picture)

```plaintext
documents (.txt/.md/.pdf)
        │  ingest.py
        ▼
  chunks ──► embeddings (OpenVINO) ──► FAISS index  (on disk)
                                            │
question ──► embedding ──► retrieve top-K relevant chunks
                                            │
                    ┌───────────────────────┘
                    ▼
        SLM (Qwen2.5 INT4, OpenVINO) ──► answer + sources
```

## Installation (isolated environment)

Requirements: Python 3.10+ and an internet connection **only** the first time.

```plaintext
bash setup.sh                  # creates .venv and installs everything in isolation
source .venv/bin/activate
python download_models.py      # downloads and exports the models to OpenVINO (once)
```

\> The `.venv` virtual environment keeps the dependencies separate from the  
\> system, as required by the isolation goal.

\> **About INT4 quantization.** The SLM is exported with _data-free_ weight-only  
\> INT4 (no calibration dataset), so `download_models.py` does not need the  
\> `datasets` library. If you prefer data-aware INT4 (slightly better accuracy),  
\> run `pip install datasets` and drop the `--group-size/--ratio` flags in  
\> `download_models.py`.

## Usage

Drop your documents into `documents/` (`.txt`, `.md`, `.pdf`).

Index them:

Ask. There are two interfaces:

**Terminal:**

**Web (Streamlit):**

Open `http://localhost:8501` in your browser: a chat plus a button to  
re-index documents from the interface itself.

Whenever you add or change documents, run `python ingest.py` again (or click  
**Index documents** in the web interface).

## Project layout

```plaintext
config.py           Parameters: models, paths, chunking, device.
core.py             RAG logic: loading, embeddings, streaming SLM, FAISS.
download_models.py  Exports the SLM (INT4) and embeddings to OpenVINO. Once.
ingest.py           Indexes documents/ into the FAISS index.
chat.py             Interactive terminal chat.
app_web.py          Web interface (Streamlit) with chat and re-indexing.
requirements.txt    Dependencies for the isolated environment.
setup.sh            Creates the venv and installs everything.
documents/          Your sources (includes a sample example.md).
```

## Quick customization (`config.py`)

*   **More quality (slower)**: `LLM_MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"` or  
    `"Qwen/Qwen2.5-3B-Instruct"`. **Re-run** `**python download_models.py**` after  
    changing it (each model is exported into its own folder).
*   **Try the iGPU**: `DEVICE = "GPU"` (or `"AUTO"`).
*   **Longer/shorter answers**: tune `MAX_NEW_TOKENS`.
*   **Retrieve more context**: raise `RETRIEVER_K` (at the cost of speed).

## Performance (making it usable on an N100)

This is a CPU SLM, so latency is dominated by the language model. The defaults  
are tuned for responsiveness:

*   **Small model by default** (`Qwen2.5-0.5B-Instruct`) — the biggest speed lever.
*   **Short answers** (`MAX_NEW_TOKENS = 256`) — generation time scales with the  
    number of tokens produced.
*   **Token streaming** — both the web and terminal UIs show the answer as it is  
    generated, so it never feels frozen.
*   **OpenVINO CPU tuning** (`LLM_OV_CONFIG`): `LATENCY` hint, `u8` KV-cache and  
    dynamic quantization. If model loading fails, it falls back automatically.
*   **Faster ingestion**: embeddings run in batches (`EMBED_BATCH_SIZE`), the index  
    is **incremental** (only new/changed files are re-embedded), and `PDF_FAST = True` skips table detection for big PDFs.

Optional, experimental:

*   `**PROMPT_LOOKUP**` (default `0`): set to e.g. `10` to enable prompt-lookup  
    decoding, which can speed up RAG generation by reusing n-grams from the  
    context. It is experimental on stateful OpenVINO models — if generation  
    errors, set it back to `0`.

\> **Quality vs speed.** Retrieval quality comes from the embeddings model, not  
\> the SLM, so a smaller SLM mostly affects _wording_, not which facts are found.  
\> Step up to 1.5B/3B (and raise `MAX_NEW_TOKENS`) when you want richer answers.

## Troubleshooting

`**RuntimeError: basic_ios::clear: iostream error**` **while exporting.** A write  
failed. The export writes a temporary model (~3 GB) under `/tmp`, and on many  
NAS/Proxmox systems `**/tmp**` **is a RAM-backed** `**tmpfs**` (check with `df -hT`):  
it overflows and, since it lives in RAM, it also worsens out-of-memory. Point  
`TMPDIR` to a real disk that has space:

If instead the **system disk itself** is small, move the cache and models to a  
big volume: `export HF_HOME=/big/hf-cache` and  
`export NOTEBOOKLM_MODELS_DIR=/big/models`.

`**download_models.py**` **is killed (**`**SIGKILL**` **/ signal 9) during "Applying**  
**Weight Compression".** This is the OOM killer: exporting/quantizing the model  
briefly needs several GB of RAM (much more than _running_ it). Options:

*   Add temporary swap on the device and retry:
*   Or export on a machine with more RAM and copy the `models/` folder over  
    (the N100 only needs the final IR to _run_).
*   Or use a smaller SLM in `config.py` (e.g. `Qwen/Qwen2.5-0.5B-Instruct`).
*   Always delete a partial `models/llm-ov-int4` before retrying.

## Notes and limitations

*   The **first answer** is slower because the model is loaded into memory.
*   In INT4 on the N100, expect a few _tokens/second_: great for Q&A, not for  
    generating long essays.
*   This is a deliberately **simple** RAG (no conversational memory, no reranking):  
    the goal is to keep it minimal, clean and easy to follow for the blog.
*   Scanned PDFs (images) are not read: they would need OCR.

## License

Free-to-use example code. Downloaded models keep their respective licenses  
(Qwen, e5).

```plaintext
rm -rf models/llm-ov-int4
fallocate -l 8G /swapfile &amp;&amp; chmod 600 /swapfile
mkswap /swapfile &amp;&amp; swapon /swapfile
python download_models.py
```

```plaintext
rm -rf models/llm-ov-int4
mkdir -p /root/tmp &amp;&amp; export TMPDIR=/root/tmp
python download_models.py
```

```plaintext
streamlit run app_web.py
```

```plaintext
You &gt; In what year was Vinotopia founded?
AI  &gt; According to the document, in the year 2026.
Sources: documents/example.md
```

```plaintext
python chat.py
```

```plaintext
python ingest.py
```