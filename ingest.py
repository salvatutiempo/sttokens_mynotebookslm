"""Index the documents in ./documents into the FAISS vector index.

Run it every time you add or change documents:
    python ingest.py
"""

import sys

import config
import core


def main() -> int:
    print(f"[>] Reading documents from {config.DOCUMENTS_DIR}")
    docs = core.load_documents()
    if not docs:
        print("[!] No .txt, .md or .pdf files found in the documents/ folder")
        return 1

    chunks = core.split_documents(docs)
    print(f"[>] {len(docs)} document(s) -> {len(chunks)} chunk(s)")

    print("[>] Computing embeddings with OpenVINO...")
    embeddings = core.get_embeddings()
    core.build_index(chunks, embeddings)

    print(f"[OK] Index saved to {config.INDEX_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
