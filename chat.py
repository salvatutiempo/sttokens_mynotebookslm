"""Interactive NotebookLM-style chat: ask about your documents, offline.

    python chat.py

Requires running first:  python download_models.py  and  python ingest.py
"""

import sys

import core


def main() -> int:
    if not core.index_exists():
        print("[!] No index found. Run first: python ingest.py")
        return 1

    print("[>] Loading models (this may take a few seconds)...")
    embeddings = core.get_embeddings()
    retriever = core.get_retriever(embeddings)
    llm = core.get_llm()

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

        docs = retriever.invoke(question)
        context = core.format_context(docs)

        print("\nAI  > ", end="", flush=True)
        for token in llm.stream(question, context):
            print(token, end="", flush=True)
        print()

        sources = core.sources_of(docs)
        if sources:
            print("Sources:", ", ".join(sources))
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
