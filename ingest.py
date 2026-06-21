"""Index the documents in ./documents into the FAISS vector index.

Incremental: only new or changed documents are (re)embedded.
Run it every time you add or change documents:
    python ingest.py
"""

import sys

import config
import core


def main() -> int:
    print(f"[>] Indexing documents from {config.DOCUMENTS_DIR}")
    embeddings = core.get_embeddings()
    summary = core.build_or_update_index(embeddings)

    if summary["action"] == "empty":
        print("[!] No .txt, .md or .pdf files found in the documents/ folder")
        return 1
    if summary["action"] == "uptodate":
        print("[OK] Index already up to date.")
        return 0

    print(f"[OK] {summary['action']}: {summary['files']} file(s), "
          f"{summary['chunks']} new chunk(s) -> {config.INDEX_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
