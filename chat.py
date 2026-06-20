"""Interactive NotebookLM-style chat: ask about your documents, offline.

    python chat.py

Requires running first:  python download_models.py  and  python ingest.py
"""

import sys

import config
import core


def main() -> int:
    if not config.INDEX_DIR.exists():
        print("[!] No index found. Run first: python ingest.py")
        return 1

    print("[>] Loading models (this may take a few seconds on the N100)...")
    embeddings = core.get_embeddings()
    vectorstore = core.load_index(embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": config.RETRIEVER_K})
    llm = core.get_llm()
    chain = core.build_rag_chain(retriever, llm)

    print("\nOffline NotebookLM ready. Type your question (or 'exit').\n")
    while True:
        try:
            question = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit", "salir"}:
            break

        result = chain.invoke({"input": question})
        print("\nAI  >", result["answer"].strip())

        sources = {doc.metadata.get("source", "?") for doc in result.get("context", [])}
        if sources:
            print("Sources:", ", ".join(sorted(sources)))
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
