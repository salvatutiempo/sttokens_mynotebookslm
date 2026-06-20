"""Core pieces of the offline NotebookLM: document loading, embeddings,
language model and RAG chain. Everything runs locally with OpenVINO.
"""

from __future__ import annotations

from pathlib import Path

import config


# --- 1. Document loading -----------------------------------------------------
def _load_pdf(path: Path) -> list:
    """Extract a PDF to Markdown with PyMuPDF4LLM (it converts tables to
    Markdown, is C++ and runs very light on the N100). Falls back to
    PyPDFLoader if it is not installed.
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
    """Recursively read .txt, .md and .pdf files from the documents folder."""
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
    """Multilingual embeddings accelerated with OpenVINO."""
    from langchain_community.embeddings import OpenVINOEmbeddings

    return OpenVINOEmbeddings(
        model_name_or_path=str(config.EMBED_OV_DIR),
        model_kwargs={"device": config.DEVICE},
        encode_kwargs={"normalize_embeddings": True, "mean_pooling": True},
    )


# --- 3. Language model (OpenVINO) --------------------------------------------
def get_llm():
    """Load the SLM exported to OpenVINO and wrap it as a LangChain chat model."""
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
    # ChatHuggingFace applies the model's chat template (system/user roles).
    return ChatHuggingFace(llm=HuggingFacePipeline(pipeline=text_pipe))


# --- 4. Vector index (FAISS) -------------------------------------------------
def build_index(chunks: list, embeddings) -> None:
    """Build the FAISS index from the chunks and save it to disk."""
    from langchain_community.vectorstores import FAISS

    config.INDEX_DIR.parent.mkdir(parents=True, exist_ok=True)
    store = FAISS.from_documents(chunks, embeddings)
    store.save_local(str(config.INDEX_DIR))


def load_index(embeddings):
    """Load a previously persisted FAISS index."""
    from langchain_community.vectorstores import FAISS

    return FAISS.load_local(
        str(config.INDEX_DIR),
        embeddings,
        allow_dangerous_deserialization=True,  # index generated locally by you
    )


# --- 5. RAG chain ------------------------------------------------------------
SYSTEM_PROMPT = (
    "You are an assistant that answers EXCLUSIVELY using the information in the "
    "provided context. If the answer is not in the context, clearly say that "
    "you do not have that information. Answer in the same language as the "
    "question and be concise.\n\n"
    "Context:\n{context}"
)


def build_rag_chain(retriever, llm):
    """Build the retrieval + generation (RAG) chain."""
    from langchain.chains import create_retrieval_chain
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain_core.prompts import ChatPromptTemplate

    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), ("human", "{input}")]
    )
    combine = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, combine)
