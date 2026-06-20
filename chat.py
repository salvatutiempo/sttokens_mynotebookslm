"""Chat interactivo tipo NotebookLM: pregunta sobre tus documentos, offline.

    python chat.py

Requiere haber ejecutado antes:  python download_models.py  y  python ingest.py
"""

import sys

import config
import core


def main() -> int:
    if not config.INDEX_DIR.exists():
        print("[!] No hay índice. Ejecuta primero: python ingest.py")
        return 1

    print("[>] Cargando modelos (puede tardar unos segundos en la N100)...")
    embeddings = core.get_embeddings()
    vectorstore = core.load_index(embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": config.RETRIEVER_K})
    llm = core.get_llm()
    chain = core.build_rag_chain(retriever, llm)

    print("\nNotebookLM offline listo. Escribe tu pregunta (o 'salir').\n")
    while True:
        try:
            question = input("Tú > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"salir", "exit", "quit"}:
            break

        result = chain.invoke({"input": question})
        print("\nIA  >", result["answer"].strip())

        sources = {doc.metadata.get("source", "?") for doc in result.get("context", [])}
        if sources:
            print("Fuentes:", ", ".join(sorted(sources)))
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
