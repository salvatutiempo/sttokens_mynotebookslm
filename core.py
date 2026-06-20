"""Piezas centrales del NotebookLM offline: carga de documentos, embeddings,
modelo de lenguaje y cadena RAG. Todo se ejecuta en local con OpenVINO.
"""

from __future__ import annotations

from pathlib import Path

import config


# --- 1. Carga de documentos --------------------------------------------------
def _load_pdf(path: Path) -> list:
    """Extrae un PDF a Markdown con PyMuPDF4LLM (convierte tablas a Markdown,
    es C++ y va muy ligero en la N100). Si no está instalado, usa PyPDFLoader.
    """
    from langchain_core.documents import Document

    try:
        import pymupdf4llm

        text = pymupdf4llm.to_markdown(str(path))
        return [Document(page_content=text, metadata={"source": str(path)})]
    except ImportError:
        from langchain_community.document_loaders import PyPDFLoader

        return PyPDFLoader(str(path)).load()


def load_documents(documents_dir: Path = config.DOCUMENTS_DIR) -> list:
    """Lee .txt, .md y .pdf de forma recursiva desde la carpeta de documentos."""
    from langchain_community.document_loaders import TextLoader

    docs = []
    for path in sorted(documents_dir.rglob("*")):
        suffix = path.suffix.lower()
        if suffix in {".txt", ".md"}:
            docs.extend(TextLoader(str(path), encoding="utf-8").load())
        elif suffix == ".pdf":
            docs.extend(_load_pdf(path))
    return docs


def split_documents(docs: list) -> list:
    """Divide los documentos en fragmentos manejables para el RAG."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        add_start_index=True,
    )
    return splitter.split_documents(docs)


# --- 2. Embeddings (OpenVINO) ------------------------------------------------
def get_embeddings():
    """Embeddings multilingües acelerados con OpenVINO."""
    from langchain_community.embeddings import OpenVINOEmbeddings

    return OpenVINOEmbeddings(
        model_name_or_path=str(config.EMBED_OV_DIR),
        model_kwargs={"device": config.DEVICE},
        encode_kwargs={"normalize_embeddings": True, "mean_pooling": True},
    )


# --- 3. Modelo de lenguaje (OpenVINO) ----------------------------------------
def get_llm():
    """Carga el SLM exportado a OpenVINO y lo envuelve como chat de LangChain."""
    from optimum.intel import OVModelForCausalLM
    from transformers import AutoTokenizer, pipeline
    from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline

    tokenizer = AutoTokenizer.from_pretrained(str(config.LLM_OV_DIR))
    model = OVModelForCausalLM.from_pretrained(str(config.LLM_OV_DIR), device=config.DEVICE)

    text_pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=config.MAX_NEW_TOKENS,
        do_sample=False,
        repetition_penalty=1.1,
        return_full_text=False,
    )
    # ChatHuggingFace aplica la plantilla de chat del modelo (rol system/user).
    return ChatHuggingFace(llm=HuggingFacePipeline(pipeline=text_pipe))


# --- 4. Índice vectorial (FAISS) ---------------------------------------------
def build_index(chunks: list, embeddings) -> None:
    """Crea el índice FAISS a partir de los fragmentos y lo guarda en disco."""
    from langchain_community.vectorstores import FAISS

    config.INDEX_DIR.parent.mkdir(parents=True, exist_ok=True)
    store = FAISS.from_documents(chunks, embeddings)
    store.save_local(str(config.INDEX_DIR))


def load_index(embeddings):
    """Carga un índice FAISS previamente persistido."""
    from langchain_community.vectorstores import FAISS

    return FAISS.load_local(
        str(config.INDEX_DIR),
        embeddings,
        allow_dangerous_deserialization=True,  # índice generado localmente por ti
    )


# --- 5. Cadena RAG -----------------------------------------------------------
SYSTEM_PROMPT = (
    "Eres un asistente que responde EXCLUSIVAMENTE usando la información del "
    "contexto proporcionado. Si la respuesta no está en el contexto, di "
    "claramente que no dispones de esa información. Responde en el mismo "
    "idioma de la pregunta y de forma concisa.\n\n"
    "Contexto:\n{context}"
)


def build_rag_chain(retriever, llm):
    """Construye la cadena de recuperación + generación (RAG)."""
    from langchain.chains import create_retrieval_chain
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain_core.prompts import ChatPromptTemplate

    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), ("human", "{input}")]
    )
    combine = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, combine)
