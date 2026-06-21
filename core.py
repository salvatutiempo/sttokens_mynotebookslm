"""Core pieces of the offline NotebookLM: document loading, embeddings,
language model and RAG helpers. Everything runs locally with OpenVINO.

LangChain orchestrates loading, splitting, embeddings and FAISS retrieval.
Generation runs directly on the OpenVINO model (optimum-intel) with token
streaming, which is what keeps it responsive on an Intel N100/N300.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

import config


# --- 1. Document loading -----------------------------------------------------
def _doc_paths(documents_dir: Path = config.DOCUMENTS_DIR) -> list[Path]:
    """All supported document paths under the documents folder."""
    return [
        p for p in sorted(documents_dir.rglob("*"))
        if p.suffix.lower() in {".txt", ".md", ".pdf"}
    ]


def _load_pdf(path: Path) -> list:
    """Extract a PDF. By default PyMuPDF4LLM (tables -> Markdown). With
    config.PDF_FAST, use plain PyMuPDF text extraction (much faster on big
    PDFs, but no table reconstruction). Falls back to PyPDFLoader.
    """
    from langchain_core.documents import Document

    try:
        if config.PDF_FAST:
            import pymupdf  # fitz, ships with pymupdf4llm

            with pymupdf.open(str(path)) as doc:
                text = "\n".join(page.get_text() for page in doc)
        else:
            import pymupdf4llm

            text = pymupdf4llm.to_markdown(str(path))
        return [Document(page_content=text, metadata={"source": str(path)})]
    except ImportError:
        from langchain_community.document_loaders import PyPDFLoader

        return PyPDFLoader(str(path)).load()


def load_documents(paths: list[Path] | None = None) -> list:
    """Read .txt, .md and .pdf documents (all of them, or a given subset)."""
    from langchain_community.document_loaders import TextLoader

    docs = []
    for path in (paths if paths is not None else _doc_paths()):
        suffix = path.suffix.lower()
        if suffix in {".txt", ".md"}:
            docs.extend(TextLoader(str(path), encoding="utf-8").load())
        elif suffix == ".pdf":
            docs.extend(_load_pdf(path))
    return docs


def split_documents(docs: list) -> list:
    """Split the documents into manageable chunks for the RAG."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        add_start_index=True,
    )
    return splitter.split_documents(docs)


# --- 2. Embeddings (OpenVINO) ------------------------------------------------
def get_embeddings():
    """Multilingual embeddings accelerated with OpenVINO (batched for speed)."""
    from langchain_community.embeddings import OpenVINOEmbeddings

    return OpenVINOEmbeddings(
        model_name_or_path=str(config.EMBED_OV_DIR),
        model_kwargs={"device": config.DEVICE},
        encode_kwargs={
            "normalize_embeddings": True,
            "mean_pooling": True,
            "batch_size": config.EMBED_BATCH_SIZE,
        },
    )


# --- 3. Language model (OpenVINO, streaming) ---------------------------------
SYSTEM_PROMPT = (
    "You are an assistant that answers EXCLUSIVELY using the information in the "
    "provided context. If the answer is not in the context, clearly say that "
    "you do not have that information. Answer in the same language as the "
    "question. Give a COMPLETE, self-contained answer in at most {max_words} "
    "words: prioritise the most important points and ALWAYS finish your "
    "sentences — never stop mid-sentence.\n\n"
    "Context:\n{context}"
)


def _word_budget() -> int:
    """Word budget for the answer, derived from the token cap (see config)."""
    return max(40, int(config.MAX_NEW_TOKENS * config.ANSWER_WORD_RATIO))


class ChatLLM:
    """Thin wrapper around an OpenVINO causal LM with token streaming."""

    def __init__(self):
        from optimum.intel import OVModelForCausalLM
        from transformers import AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(str(config.LLM_OV_DIR))

        # Load with runtime tuning; fall back to simpler configs if a property
        # is not accepted, so the app always starts.
        last_error = None
        for ov_config in (config.LLM_OV_CONFIG, {"PERFORMANCE_HINT": "LATENCY"}, {}):
            try:
                self.model = OVModelForCausalLM.from_pretrained(
                    str(config.LLM_OV_DIR), device=config.DEVICE, ov_config=ov_config
                )
                break
            except Exception as exc:  # noqa: BLE001 - try the next, simpler config
                last_error = exc
        else:
            raise last_error

        self._warmup()

    def _build_inputs(self, question: str, context: str):
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT.format(
                    context=context, max_words=_word_budget()
                ),
            },
            {"role": "user", "content": question},
        ]
        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        return self.tokenizer(text, return_tensors="pt")

    def _generate_kwargs(self, inputs, streamer=None) -> dict:
        kwargs = dict(
            **inputs,
            max_new_tokens=config.MAX_NEW_TOKENS,
            do_sample=False,
            repetition_penalty=1.1,
            no_repeat_ngram_size=config.NO_REPEAT_NGRAM,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        if streamer is not None:
            kwargs["streamer"] = streamer
        if config.PROMPT_LOOKUP > 0:
            kwargs["prompt_lookup_num_tokens"] = config.PROMPT_LOOKUP
        return kwargs

    def _warmup(self) -> None:
        """First inference compiles the model; do it once at load time."""
        try:
            inputs = self.tokenizer("Hello", return_tensors="pt")
            self.model.generate(**inputs, max_new_tokens=1,
                                 pad_token_id=self.tokenizer.eos_token_id)
        except Exception:  # noqa: BLE001 - warmup is best effort
            pass

    def stream(self, question: str, context: str) -> Iterator[str]:
        """Yield the answer token by token (keeps the UI responsive)."""
        from threading import Thread
        from transformers import TextIteratorStreamer

        inputs = self._build_inputs(question, context)
        streamer = TextIteratorStreamer(
            self.tokenizer, skip_prompt=True, skip_special_tokens=True
        )
        thread = Thread(target=self.model.generate,
                        kwargs=self._generate_kwargs(inputs, streamer))
        thread.start()
        for token in streamer:
            yield token
        thread.join()


def get_llm() -> ChatLLM:
    return ChatLLM()


# --- 4. Vector index (FAISS, incremental) ------------------------------------
def load_index(embeddings):
    """Load a previously persisted FAISS index."""
    from langchain_community.vectorstores import FAISS

    return FAISS.load_local(
        str(config.INDEX_DIR),
        embeddings,
        allow_dangerous_deserialization=True,  # index generated locally by you
    )


def get_retriever(embeddings):
    """LangChain retriever over the persisted FAISS index."""
    return load_index(embeddings).as_retriever(search_kwargs={"k": config.RETRIEVER_K})


def _manifest_path() -> Path:
    return config.INDEX_DIR.parent / "manifest.json"


def _load_manifest() -> dict:
    p = _manifest_path()
    return json.loads(p.read_text()) if p.exists() else {}


def _save_manifest(manifest: dict) -> None:
    p = _manifest_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(manifest, indent=2))


def index_exists() -> bool:
    return (config.INDEX_DIR / "index.faiss").exists()


def build_or_update_index(embeddings) -> dict:
    """Index the documents incrementally.

    - New files are embedded and *added* to the existing index (fast).
    - If a previously indexed file changed or was removed, the index is rebuilt
      (simplest correct behaviour).
    Returns a small summary: {action, files, chunks}.
    """
    from langchain_community.vectorstores import FAISS

    current = {str(p): p.stat().st_mtime for p in _doc_paths()}
    if not current:
        return {"action": "empty", "files": 0, "chunks": 0}

    manifest = _load_manifest()
    new_files = [f for f in current if f not in manifest]
    changed_or_removed = any(manifest.get(f) != current.get(f) for f in manifest)

    if not index_exists() or changed_or_removed:
        docs = load_documents([Path(f) for f in current])
        chunks = split_documents(docs)
        config.INDEX_DIR.parent.mkdir(parents=True, exist_ok=True)
        FAISS.from_documents(chunks, embeddings).save_local(str(config.INDEX_DIR))
        _save_manifest(current)
        return {"action": "rebuild", "files": len(current), "chunks": len(chunks)}

    if new_files:
        docs = load_documents([Path(f) for f in new_files])
        chunks = split_documents(docs)
        store = load_index(embeddings)
        store.add_documents(chunks)
        store.save_local(str(config.INDEX_DIR))
        _save_manifest(current)
        return {"action": "add", "files": len(new_files), "chunks": len(chunks)}

    return {"action": "uptodate", "files": len(current), "chunks": 0}


# --- 5. RAG helpers ----------------------------------------------------------
def format_context(docs: list) -> str:
    """Join retrieved chunks into the context block for the prompt."""
    return "\n\n".join(doc.page_content for doc in docs)


def sources_of(docs: list) -> list[str]:
    """Unique source paths of the retrieved chunks."""
    return sorted({doc.metadata.get("source", "?") for doc in docs})
