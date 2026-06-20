"""Interfaz web mínima (Streamlit) para el NotebookLM offline.

    streamlit run app_web.py

Reutiliza la misma lógica que la versión de terminal (core.py): carga de
documentos, embeddings e índice FAISS con OpenVINO, y la cadena RAG.
"""

import streamlit as st

import config
import core


# --- Carga perezosa y cacheada (se hace una sola vez por sesión) -------------
@st.cache_resource(show_spinner="Cargando modelos OpenVINO...")
def get_chain():
    embeddings = core.get_embeddings()
    vectorstore = core.load_index(embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": config.RETRIEVER_K})
    return core.build_rag_chain(retriever, core.get_llm())


def reindex():
    """Reconstruye el índice FAISS a partir de documents/."""
    docs = core.load_documents()
    if not docs:
        st.sidebar.error("No hay .txt, .md o .pdf en documents/")
        return
    chunks = core.split_documents(docs)
    core.build_index(chunks, core.get_embeddings())
    get_chain.clear()  # fuerza recargar el índice nuevo
    st.sidebar.success(f"Indexados {len(docs)} documento(s) -> {len(chunks)} fragmentos")


# --- Interfaz ----------------------------------------------------------------
st.set_page_config(page_title="NotebookLM offline", page_icon="📓")
st.title("📓 NotebookLM offline · Intel N100")
st.caption("RAG 100% local con LangChain + OpenVINO. Tus documentos no salen del equipo.")

with st.sidebar:
    st.header("Documentos")
    st.write(f"Carpeta: `{config.DOCUMENTS_DIR.name}/`")
    if st.button("🔄 Indexar documentos", use_container_width=True):
        reindex()
    st.caption(f"SLM: {config.LLM_MODEL_ID}")

if not config.INDEX_DIR.exists():
    st.info("No hay índice todavía. Añade documentos a `documents/` y pulsa "
            "**Indexar documentos** en la barra lateral.")
    st.stop()

chain = get_chain()

# Historial de la conversación
if "messages" not in st.session_state:
    st.session_state.messages = []
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if question := st.chat_input("Pregunta sobre tus documentos..."):
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user").write(question)

    with st.chat_message("assistant"):
        with st.spinner("Pensando en la N100..."):
            result = chain.invoke({"input": question})
        answer = result["answer"].strip()
        st.write(answer)

        sources = sorted({d.metadata.get("source", "?") for d in result.get("context", [])})
        if sources:
            st.caption("Fuentes: " + ", ".join(sources))
    st.session_state.messages.append({"role": "assistant", "content": answer})
