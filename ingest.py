"""Indexa los documentos de ./documents en el índice vectorial FAISS.

Ejecútalo cada vez que añadas o cambies documentos:
    python ingest.py
"""

import sys

import config
import core


def main() -> int:
    print(f"[>] Leyendo documentos de {config.DOCUMENTS_DIR}")
    docs = core.load_documents()
    if not docs:
        print("[!] No se encontraron .txt, .md o .pdf en la carpeta documents/")
        return 1

    chunks = core.split_documents(docs)
    print(f"[>] {len(docs)} documento(s) -> {len(chunks)} fragmento(s)")

    print("[>] Calculando embeddings con OpenVINO...")
    embeddings = core.get_embeddings()
    core.build_index(chunks, embeddings)

    print(f"[OK] Índice guardado en {config.INDEX_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
