# Offline NotebookLM on an Intel N100

A minimal, fully local NotebookLM clone: ask natural-language questions about
your own documents (**text, Markdown and PDF**) **without an internet
connection**, using a small language model (**SLM**) accelerated with
**OpenVINO** on an **Intel N100**. Everything is orchestrated with **LangChain**
using a RAG (*Retrieval-Augmented Generation*) pattern.

> After the initial one-time model download, the system runs 100% offline.
> Your documents never leave the machine.

---

## Why these choices?

| Piece | Choice | Reason |
|-------|--------|--------|
| **SLM** | `Qwen2.5-1.5B-Instruct` (INT4) | Recent, multilingual (good Spanish) and ~1 GB in INT4: fits comfortably on the N100. |
| **Acceleration** | **OpenVINO** | Intel's runtime; squeezes the 4 cores (and optionally the iGPU) of the N100. |
| **Embeddings** | `multilingual-e5-small` | Lightweight (~118 M) and multilingual, also via OpenVINO. |
| **Vector store** | **FAISS** | Local, server-less, no external dependencies. |
| **Orchestration** | **LangChain** | Wires document loading, retrieval and generation with little code. |

The **Intel N100** is a 6 W, 4-core CPU with no dedicated GPU. The key to making
an LLM usable is: **small model + INT4 quantization + OpenVINO**.

PDFs are extracted with **PyMuPDF4LLM**, which converts even **tables to
Markdown** (in C++, fast and light on RAM); if it is not installed, the code
falls back to `PyPDFLoader`.

> **Design note.** Unlike the usual approaches (Ollama or llama.cpp with GGUF
> models, where OpenVINO is used only for the *embeddings* or as an optional
> backend), here **the SLM itself runs on OpenVINO** through `optimum-intel` in
> INT4. This uses Intel's runtime end to end, which is exactly the goal on an
> N100.

---

## What runs what? (engine and models)

This is the most common point of confusion if you come from Ollama, so let's be
explicit.

### The engine: OpenVINO (not Ollama, not llama.cpp)

The SLM is **not** run by Ollama or llama.cpp. It is loaded and executed by the
**OpenVINO Runtime**, called from Python. The chain of pieces is:

```
LangChain  →  optimum-intel (OVModelForCausalLM)  →  OpenVINO Runtime  →  N100 CPU/iGPU
(orchestrates)      (loads the model)                   (does the math)
```

Key differences vs. an Ollama / llama.cpp setup:

| | Ollama / llama.cpp | **This project** |
|---|---|---|
| Engine that runs the SLM | Ollama or llama.cpp | **OpenVINO** (via `optimum-intel`) |
| Model format | GGUF (`.gguf`) | **OpenVINO IR** (`.xml` + `.bin`) |
| Separate server process? | Yes (`ollama serve` / `llama-server`) | **No** — the model loads inside the Python process |
| Who prepares it | you `ollama pull` | `download_models.py` exports to IR |

There is **no Ollama and no llama.cpp** anywhere in `requirements.txt`.

### The models: two of them (a RAG always needs two)

They do two different jobs:

| Model | Job | Used here | Size |
|-------|-----|-----------|------|
| **Embeddings** | Turns text into vectors to **search** for the relevant chunk | `multilingual-e5-small` | ~118 M (~120 MB) |
| **SLM (LLM)** | **Writes the answer** from the retrieved chunks | `Qwen2.5-1.5B-Instruct` | ~1 GB in INT4 |

Think of it as a library: the **embeddings** model is the *librarian* that finds
the right page; the **SLM** is the one that reads that page and writes your
answer. That is why `download_models.py` downloads **two** things (you will see
two folders under `models/`: `llm-ov-int4` and `embed-ov`), and **both run on
OpenVINO**.

---

## Architecture (RAG in one picture)

```
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

---

## Installation (isolated environment)

Requirements: Python 3.10+ and an internet connection **only** the first time.

```bash
bash setup.sh                  # creates .venv and installs everything in isolation
source .venv/bin/activate
python download_models.py      # downloads and exports the models to OpenVINO (once)
```

> The `.venv` virtual environment keeps the dependencies separate from the
> system, as required by the isolation goal.

> **About INT4 quantization.** The SLM is exported with *data-free* weight-only
> INT4 (no calibration dataset), so `download_models.py` does not need the
> `datasets` library. If you prefer data-aware INT4 (slightly better accuracy),
> run `pip install datasets` and drop the `--group-size/--ratio` flags in
> `download_models.py`.

---

## Usage

1. Drop your documents into `documents/` (`.txt`, `.md`, `.pdf`).
2. Index them:

   ```bash
   python ingest.py
   ```

3. Ask. There are two interfaces:

   **Terminal:**

   ```bash
   python chat.py
   ```

   ```
   You > In what year was Vinotopia founded?
   AI  > According to the document, in the year 2026.
   Sources: documents/example.md
   ```

   **Web (Streamlit):**

   ```bash
   streamlit run app_web.py
   ```

   Open `http://localhost:8501` in your browser: a chat plus a button to
   re-index documents from the interface itself.

Whenever you add or change documents, run `python ingest.py` again (or click
**Index documents** in the web interface).

---

## Project layout

```
config.py           Parameters: models, paths, chunking, device.
core.py             RAG logic: loading, embeddings, SLM, FAISS and chain.
download_models.py  Exports the SLM (INT4) and embeddings to OpenVINO. Once.
ingest.py           Indexes documents/ into the FAISS index.
chat.py             Interactive terminal chat.
app_web.py          Web interface (Streamlit) with chat and re-indexing.
requirements.txt    Dependencies for the isolated environment.
setup.sh            Creates the venv and installs everything.
documents/          Your sources (includes a sample example.md).
```

---

## Quick customization (`config.py`)

- **Higher quality**: `LLM_MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"` (recommended on
  a 16 GB N100; slower but more accurate, less hallucination).
- **Lighter / faster**: `LLM_MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"`.
- **Try the iGPU**: `DEVICE = "GPU"` (or `"AUTO"`).
- **Longer/shorter answers**: tune `MAX_NEW_TOKENS`.
- **Retrieve more context**: raise `RETRIEVER_K` (at the cost of speed).

> **Which SLM should I pick?** On an **8 GB** N100, stick with the default
> `Qwen2.5-1.5B-Instruct` (snappy, ~8-14 tok/s). On a **16 GB** N100, prefer
> `Qwen2.5-3B-Instruct`: it follows "answer only from the context" more
> reliably and hallucinates less, at ~3-6 tok/s. Changing the embeddings model
> is independent and only affects search quality, not the wording of answers.

---

## Troubleshooting

- **`RuntimeError: basic_ios::clear: iostream error` while exporting.** A write
  failed — almost always **out of disk space** (or a full `/tmp` tmpfs). The
  export writes ~3 GB (FP16) + ~1 GB (INT4), plus the HuggingFace cache (~3 GB).
  On a NAS where the system disk is small, point everything to a big volume:
  ```bash
  rm -rf models/llm-ov-int4
  export HF_HOME=/mnt/pool/hf-cache          # HuggingFace download cache
  export NOTEBOOKLM_MODELS_DIR=/mnt/pool/models
  export TMPDIR=/mnt/pool/tmp                 # if /tmp is a small tmpfs
  python download_models.py
  ```

- **`download_models.py` is killed (`SIGKILL` / signal 9) during "Applying
  Weight Compression".** This is the OOM killer: exporting/quantizing the model
  briefly needs several GB of RAM (much more than *running* it). Options:
  - Add temporary swap on the device and retry:
    ```bash
    rm -rf models/llm-ov-int4
    fallocate -l 8G /swapfile && chmod 600 /swapfile
    mkswap /swapfile && swapon /swapfile
    python download_models.py
    ```
  - Or export on a machine with more RAM and copy the `models/` folder over
    (the N100 only needs the final IR to *run*).
  - Or use a smaller SLM in `config.py` (e.g. `Qwen/Qwen2.5-0.5B-Instruct`).
  - Always delete a partial `models/llm-ov-int4` before retrying.

## Notes and limitations

- The **first answer** is slower because the model is loaded into memory.
- In INT4 on the N100, expect a few *tokens/second*: great for Q&A, not for
  generating long essays.
- This is a deliberately **simple** RAG (no conversational memory, no reranking):
  the goal is to keep it minimal, clean and easy to follow for the blog.
- Scanned PDFs (images) are not read: they would need OCR.

---

## License

Free-to-use example code. Downloaded models keep their respective licenses
(Qwen, e5).
