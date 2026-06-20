# NotebookLM offline en un Intel N100

Un clon mínimo y local de NotebookLM: haz preguntas en lenguaje natural sobre
tus propios documentos (**texto, Markdown y PDF**) **sin conexión a internet**,
usando un modelo de lenguaje pequeño (**SLM**) acelerado con **OpenVINO** sobre
un **Intel N100**. Todo orquestado con **LangChain** mediante un patrón RAG
(*Retrieval-Augmented Generation*).

> Tras la descarga inicial de los modelos, el sistema funciona 100% offline.
> Tus documentos nunca salen del equipo.

---

## ¿Por qué estas elecciones?

| Pieza | Elección | Motivo |
|-------|----------|--------|
| **SLM** | `Qwen2.5-1.5B-Instruct` (INT4) | Reciente, multilingüe (buen español) y ~1 GB en INT4: cabe holgado en la N100. |
| **Aceleración** | **OpenVINO** | Es el runtime de Intel; exprime los 4 núcleos (y opcionalmente la iGPU) de la N100. |
| **Embeddings** | `multilingual-e5-small` | Ligero (~118 M) y multilingüe, también vía OpenVINO. |
| **Vector store** | **FAISS** | Local, sin servidor, sin dependencias externas. |
| **Orquestación** | **LangChain** | Conecta carga de documentos, recuperación y generación con poco código. |

El **Intel N100** es una CPU de 6 W con 4 núcleos sin GPU dedicada. La clave
para que un LLM sea usable es: **modelo pequeño + cuantización INT4 + OpenVINO**.

Los PDFs se extraen con **PyMuPDF4LLM**, que convierte incluso las **tablas a
Markdown** (en C++, rápido y con poca RAM); si no está instalado, se recurre a
`PyPDFLoader`.

> **Nota de diseño.** A diferencia de los enfoques habituales (Ollama o
> llama.cpp con modelos GGUF, que solo usan OpenVINO para los *embeddings* o
> como backend opcional), aquí **el propio SLM se ejecuta sobre OpenVINO** vía
> `optimum-intel` en INT4. Así se exprime el runtime de Intel de extremo a
> extremo, que es justo el objetivo en una N100.

---

## Arquitectura (RAG en una frase)

```
documentos (.txt/.md/.pdf)
        │  ingest.py
        ▼
  fragmentos ──► embeddings (OpenVINO) ──► índice FAISS  (en disco)
                                               │
pregunta ──► embedding ──► recupera K fragmentos relevantes
                                               │
                       ┌───────────────────────┘
                       ▼
        SLM (Qwen2.5 INT4, OpenVINO) ──► respuesta + fuentes
```

---

## Instalación (entorno aislado)

Requisitos: Python 3.10+ y conexión a internet **solo** la primera vez.

```bash
bash setup.sh                  # crea .venv e instala todo de forma aislada
source .venv/bin/activate
python download_models.py      # descarga y exporta los modelos a OpenVINO (1 vez)
```

> El entorno virtual `.venv` mantiene las dependencias separadas del sistema,
> tal y como pedía el requisito de aislamiento.

---

## Uso

1. Pon tus documentos en `documents/` (`.txt`, `.md`, `.pdf`).
2. Indexa:

   ```bash
   python ingest.py
   ```

3. Pregunta. Tienes dos interfaces:

   **Terminal:**

   ```bash
   python chat.py
   ```

   ```
   Tú > ¿En qué año se fundó Vinotopía?
   IA  > Según el documento, en el año 2026.
   Fuentes: documents/ejemplo.md
   ```

   **Web (Streamlit):**

   ```bash
   streamlit run app_web.py
   ```

   Abre el navegador en `http://localhost:8501`, con chat y un botón para
   reindexar documentos desde la propia interfaz.

Cada vez que añadas o cambies documentos, vuelve a ejecutar `python ingest.py`
(o pulsa **Indexar documentos** en la interfaz web).

---

## Estructura del proyecto

```
config.py           Parámetros: modelos, rutas, chunking, dispositivo.
core.py             Lógica RAG: carga, embeddings, SLM, FAISS y cadena.
download_models.py  Exporta SLM (INT4) y embeddings a OpenVINO. Una sola vez.
ingest.py           Indexa documents/ en el índice FAISS.
chat.py             Chat interactivo por terminal.
app_web.py          Interfaz web (Streamlit) con chat y reindexado.
requirements.txt    Dependencias del entorno aislado.
setup.sh            Crea el venv e instala todo.
documents/          Tus fuentes (incluye un ejemplo.md de prueba).
```

---

## Personalización rápida (`config.py`)

- **Más calidad**: `LLM_MODEL_ID = "meta-llama/Llama-3.2-3B-Instruct"` (más lento).
- **Más ligereza/velocidad**: `LLM_MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"`.
- **Probar la iGPU**: `DEVICE = "GPU"` (o `"AUTO"`).
- **Respuestas más largas/cortas**: ajusta `MAX_NEW_TOKENS`.
- **Recuperar más contexto**: sube `RETRIEVER_K` (a costa de velocidad).

---

## Notas y limitaciones

- La **primera respuesta** es más lenta porque carga el modelo en memoria.
- En INT4 sobre N100, espera del orden de unos pocos *tokens/segundo*: perfecto
  para consultas, no para generar textos largos.
- Es un RAG sencillo (sin memoria conversacional ni reranking) **a propósito**:
  el objetivo es que sea mínimo, limpio y fácil de entender para el blog.
- PDFs escaneados (imágenes) no se leen: necesitarían OCR.

---

## Licencia

Código de ejemplo de uso libre. Los modelos descargados conservan sus
respectivas licencias (Qwen, e5).
