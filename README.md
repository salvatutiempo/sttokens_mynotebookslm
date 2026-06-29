# Offline NotebookLM on an Intel low power device

A minimal, fully local NotebookLM clone: ask natural-language questions about
your own documents (**text, Markdown and PDF**) **without an internet
connection**, using a small language model (**SLM**) accelerated with
**OpenVINO** on an **Intel N100**. Everything is orchestrated with **LangChain**
using a RAG (*Retrieval-Augmented Generation*) pattern.

> After the initial one-time model download, the system runs 100% offline.
> Your documents never leave the machine.

## What's new in v2.0.0

### Model picker in the web UI
- A sidebar selector lets you switch between any models listed in `AVAILABLE_LLMS` (`config.py`) without restarting the app.
- - The previous model is **unloaded from RAM** before the new one is loaded (`get_llm.clear()` + `gc.collect()`), keeping memory usage predictable on a device with limited RAM like the N100.
  - - `download_models.py` now accepts model IDs as arguments so you can export multiple models in one command:
    -   ```
          python download_models.py "Qwen/Qwen2.5-0.5B-Instruct" "Qwen/Qwen2.5-1.5B-Instruct"
          ```

        ### Drag-and-drop document uploads
        - A file uploader widget in the sidebar lets you add `.txt`, `.md` and `.pdf` files directly from the browser — no need to SSH into the machine to drop files in the `documents/` folder.
        - - Uploaded files are saved to `documents/` and indexed immediately in one click ("➕ Add & index").
          -
          ### Load-on-demand with model readiness check
          - `core.llm_is_ready(model_dir)` checks whether a given model has been exported before trying to load it. If the model is not yet exported, the UI shows a clear warning with the exact command to run.
          - - Each model is stored in its own folder (`llm-<model-name>-int4/`), managed by the new `config.llm_dir()` helper.
            -
            ### Cleaner `core.py` API
            - `get_llm()` now accepts an explicit `model_dir` parameter, allowing the web UI to load whichever model the user selected rather than always loading the default.
            -
            ---

## Why these choices?

| Piece | Choice | Reason |
|-------|--------|--------|
| **SLM** | `Qwen2.5-0.5B-Instruct` (INT4) | Speed-first default: flies on an N100 (~0.4 GB). Switch to 1.5B/3B for more quality. |
| **Acceleration** | **OpenVINO** | Intel's runtime; squeezes the 4-8 cores (and optionally the iGPU) of the N-series. |
| **Embeddings** | `multilingual-e5-small` | Lightweight (~118 M) and multilingual, also via OpenVINO. |
| **Vector store** | **FAISS** | Local, server-less, no external dependencies; indexed incrementally. |
| **Orchestration** | **LangChain** | Wires document loading, retrieval and embeddings with little code. |

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
                    ┌─────────────────────────┘
                    ▼
        SLM (Qwen2.5 INT4, OpenVINO) ──► answer + sources
```

---

## Installation (isolated environment)

**Requirements:**

- **Python 3.10 or newer must be installed** (with `pip` and the `venv` module).
  Check with `python3 --version`. On Debian/Ubuntu, if needed:
  `sudo apt install python3 python3-venv python3-pip`.
- An internet connection **only** the first time (to download the models).

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

   Open `http://localhost:8501` in your browser: a chat, plus an **uploader**
   to add documents (`.txt`/`.md`/`.pdf`) and index them from the interface.

Whenever you add or change documents, run `python ingest.py` again (or click
**Index documents** in the web interface).

---

## Project layout

```
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

---

## Quick customization (`config.py`)

- **Switch model from the web UI**: a sidebar selector lets you pick between the
  models in `AVAILABLE_LLMS` (0.5B fast / 1.5B quality). Export both once so they
  are selectable:
  ```bash
  python download_models.py "Qwen/Qwen2.5-0.5B-Instruct" "Qwen/Qwen2.5-1.5B-Instruct"
  ```
  (`download_models.py` with no arguments exports the default from `config.py`.)
- **Try the iGPU**: `DEVICE = "GPU"` (or `"AUTO"`).
- **Longer/shorter answers**: tune `MAX_NEW_TOKENS`.
- **Retrieve more context**: raise `RETRIEVER_K` (at the cost of speed).

---

## Performance (making it usable on an N100)

This is a CPU SLM, so latency is dominated by the language model. The defaults
are tuned for responsiveness:

- **Small model by default** (`Qwen2.5-0.5B-Instruct`) — the biggest speed lever.
- **Short answers** (`MAX_NEW_TOKENS = 256`) — generation time scales with the
  number of tokens produced.
- **Token streaming** — both the web and terminal UIs show the answer as it is
  generated, so it never feels frozen.
- **OpenVINO CPU tuning** (`LLM_OV_CONFIG`): `LATENCY` hint, `u8` KV-cache and
  dynamic quantization. If model loading fails, it falls back automatically.
- **Faster ingestion**: embeddings run in batches (`EMBED_BATCH_SIZE`), the index
  is **incremental** (only new/changed files are re-embedded), and `PDF_FAST =
  True` skips table detection for big PDFs.

Optional, experimental:

- **`PROMPT_LOOKUP`** (default `0`): set to e.g. `10` to enable prompt-lookup
  decoding, which can speed up RAG generation by reusing n-grams from the
  context. It is experimental on stateful OpenVINO models — if generation
  errors, set it back to `0`.

> **Quality vs speed.** Retrieval quality comes from the embeddings model, not
> the SLM, so a smaller SLM mostly affects *wording*, not which facts are found.
> Step up to 1.5B/3B (and raise `MAX_NEW_TOKENS`) when you want richer answers.

---

## Troubleshooting

- **`RuntimeError: basic_ios::clear: iostream error` while exporting.** A write
  failed. The export writes a temporary model (~3 GB) under `/tmp`, and on many
  NAS/Proxmox systems **`/tmp` is a RAM-backed `tmpfs`** (check with `df -hT`):
  it overflows and, since it lives in RAM, it also worsens out-of-memory. Point
  `TMPDIR` to a real disk that has space:
  ```bash
  rm -rf models/llm-ov-int4
  mkdir -p /root/tmp && export TMPDIR=/root/tmp
  python download_models.py
  ```
  If instead the **system disk itself** is small, move the cache and models to a
  big volume: `export HF_HOME=/big/hf-cache` and
  `export NOTEBOOKLM_MODELS_DIR=/big/models`.

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
