"""Minimal web interface (Streamlit) for the offline NotebookLM.

    streamlit run app_web.py

Reuses the same logic as the terminal version (core.py): document loading,
embeddings and FAISS index with OpenVINO, retrieval and streaming generation.
"""

import streamlit as st

from pathlib import Path

import config
import core


# --- Lazy, cached loading (done once per session) ----------------------------
@st.cache_resource(show_spinner="Loading embeddings...")
def get_embeddings():
    return core.get_embeddings()


# max_entries=1: keep only the model currently in use cached (frees RAM).
@st.cache_resource(max_entries=1, show_spinner="Loading the language model (OpenVINO)...")
def get_llm(model_dir: str):
    return core.get_llm(model_dir)


def load_llm(model_dir: str):
    """Load the selected model, freeing the previous one from RAM on a switch."""
    import gc

    if st.session_state.get("model_dir") != model_dir:
        get_llm.clear()          # drop the previously loaded model...
        gc.collect()             # ...and release its memory before loading the new one
        st.session_state["model_dir"] = model_dir
    return get_llm(model_dir)


def get_retriever():
    return core.get_retriever(get_embeddings())


def reindex():
    """Index documents/ incrementally (only new/changed files are embedded)."""
    with st.spinner("Indexing documents..."):
        summary = core.build_or_update_index(get_embeddings())
    if summary["action"] == "empty":
        st.sidebar.error("No .txt, .md or .pdf files in documents/")
    elif summary["action"] == "uptodate":
        st.sidebar.info("Index already up to date.")
    else:
        st.sidebar.success(
            f"{summary['action']}: {summary['files']} file(s), "
            f"{summary['chunks']} new chunk(s)"
        )


def save_uploads(files) -> int:
    """Save uploaded files into the documents folder. Returns how many."""
    config.DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    for f in files:
        # Path(...).name strips any directory components (no path traversal).
        (config.DOCUMENTS_DIR / Path(f.name).name).write_bytes(f.getbuffer())
    return len(files)


# --- Interface ---------------------------------------------------------------
st.set_page_config(page_title="Offline NotebookLM", page_icon="📓")
st.title("📓 Offline NotebookLM")
st.caption("100% local RAG with LangChain + OpenVINO. Your documents never leave the machine.")

with st.sidebar:
    st.header("Documents")
    st.write(f"Folder: `{config.DOCUMENTS_DIR.name}/`")

    uploaded = st.file_uploader(
        "Upload documents",
        type=["txt", "md", "pdf"],
        accept_multiple_files=True,
    )
    if uploaded and st.button("➕ Add & index", use_container_width=True):
        n = save_uploads(uploaded)
        st.sidebar.success(f"Saved {n} file(s)")
        reindex()

    if st.button("🔄 Re-index folder", use_container_width=True):
        reindex()

    st.header("Model")
    labels = list(config.AVAILABLE_LLMS)
    default_label = next(
        (l for l, i in config.AVAILABLE_LLMS.items() if i == config.LLM_MODEL_ID),
        labels[0],
    )
    choice = st.selectbox("Language model", labels, index=labels.index(default_label))
    selected_id = config.AVAILABLE_LLMS[choice]
    selected_dir = config.llm_dir(selected_id)

if not core.index_exists():
    st.info("No index yet. Upload documents in the sidebar (or drop them into "
            "`documents/`) and click **Add & index**.")
    st.stop()

if not core.llm_is_ready(selected_dir):
    st.warning(
        f"**{choice}** is not downloaded yet. Export it once with:\n\n"
        f"```\npython download_models.py \"{selected_id}\"\n```"
    )
    st.stop()

retriever = get_retriever()
llm = load_llm(str(selected_dir))

# Conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if question := st.chat_input("Ask about your documents..."):
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user").write(question)

    with st.chat_message("assistant"):
        docs = retriever.invoke(question)
        context = core.format_context(docs)
        # Stream the answer token by token as it is generated.
        answer = st.write_stream(llm.stream(question, context))
        sources = core.sources_of(docs)
        if sources:
            st.caption("Sources: " + ", ".join(sources))
    st.session_state.messages.append({"role": "assistant", "content": answer})
