"""Minimal web interface (Streamlit) for the offline NotebookLM.

    streamlit run app_web.py

Reuses the same logic as the terminal version (core.py): document loading,
embeddings and FAISS index with OpenVINO, retrieval and streaming generation.
"""

import streamlit as st

import config
import core


# --- Lazy, cached loading (done once per session) ----------------------------
@st.cache_resource(show_spinner="Loading embeddings...")
def get_embeddings():
    return core.get_embeddings()


@st.cache_resource(show_spinner="Loading the language model (OpenVINO)...")
def get_llm():
    return core.get_llm()


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


# --- Interface ---------------------------------------------------------------
st.set_page_config(page_title="Offline NotebookLM", page_icon="📓")
st.title("📓 Offline NotebookLM · Intel N100")
st.caption("100% local RAG with LangChain + OpenVINO. Your documents never leave the machine.")

with st.sidebar:
    st.header("Documents")
    st.write(f"Folder: `{config.DOCUMENTS_DIR.name}/`")
    if st.button("🔄 Index documents", use_container_width=True):
        reindex()
    st.caption(f"SLM: {config.LLM_MODEL_ID}")

if not core.index_exists():
    st.info("No index yet. Add documents to `documents/` and click "
            "**Index documents** in the sidebar.")
    st.stop()

retriever = get_retriever()
llm = get_llm()

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
