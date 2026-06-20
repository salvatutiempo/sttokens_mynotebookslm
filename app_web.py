"""Minimal web interface (Streamlit) for the offline NotebookLM.

    streamlit run app_web.py

Reuses the same logic as the terminal version (core.py): document loading,
embeddings and FAISS index with OpenVINO, and the RAG chain.
"""

import streamlit as st

import config
import core


# --- Lazy, cached loading (done once per session) ----------------------------
@st.cache_resource(show_spinner="Loading OpenVINO models...")
def get_chain():
    embeddings = core.get_embeddings()
    vectorstore = core.load_index(embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": config.RETRIEVER_K})
    return core.build_rag_chain(retriever, core.get_llm())


def reindex():
    """Rebuild the FAISS index from documents/."""
    docs = core.load_documents()
    if not docs:
        st.sidebar.error("No .txt, .md or .pdf files in documents/")
        return
    chunks = core.split_documents(docs)
    core.build_index(chunks, core.get_embeddings())
    get_chain.clear()  # force reloading the new index
    st.sidebar.success(f"Indexed {len(docs)} document(s) -> {len(chunks)} chunks")


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

if not config.INDEX_DIR.exists():
    st.info("No index yet. Add documents to `documents/` and click "
            "**Index documents** in the sidebar.")
    st.stop()

chain = get_chain()

# Conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if question := st.chat_input("Ask about your documents..."):
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user").write(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking on the N100..."):
            result = chain.invoke({"input": question})
        answer = result["answer"].strip()
        st.write(answer)

        sources = sorted({d.metadata.get("source", "?") for d in result.get("context", [])})
        if sources:
            st.caption("Sources: " + ", ".join(sources))
    st.session_state.messages.append({"role": "assistant", "content": answer})
