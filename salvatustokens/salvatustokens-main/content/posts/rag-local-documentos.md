---
title_es: "RAG local con tus documentos"
subtitle_es: "privacidad total y cero tokens de pago"
description_es: "Lab práctico paso a paso para montar un RAG local con Ollama: chatea con tus PDFs y notas sin que tus datos salgan del equipo y sin pagar por token."
title_en: "Local RAG with your documents"
subtitle_en: "full privacy and zero paid tokens"
description_en: "A practical step-by-step lab to build a local RAG with Ollama: chat with your PDFs and notes without your data leaving the machine and without paying per token."
slug: rag-local-documentos
author: salvatustokens
tags_es: IA local, RAG, Ollama, privacidad, embeddings
tags_en: Local AI, RAG, Ollama, privacy, embeddings
reading_time: 14 min
date: 2026-06-16
published: false
---

<!-- es -->

# ÍNDICE

1. Introducción
2. Prerrequisitos
3. ¿Qué vamos a montar?
4. Qué es un RAG (sin tecnicismos)
5. Paso 1: instalar Ollama y los dos modelos
6. Paso 2: preparar tus documentos
7. Paso 3: trocear e indexar en local
8. Paso 4: preguntar a tus documentos
9. La versión sin código: Open WebUI
10. Medir el ahorro (y la privacidad)
11. Extras
12. Quiero el flujo completo

# 1. Introducción

¿Cuántas veces hemos copiado un PDF entero en un chat de IA de pago solo para preguntarle una cosa concreta? Un contrato, un manual de 40 páginas, las notas de la reunión... y a tragar tokens cada vez que volvemos a preguntar.

Funciona, sí. Pero pagamos por subir el documento completo una y otra vez, y además ese documento sale de nuestro equipo y acaba en el servidor de otro. Si encima son contratos, facturas o datos de clientes, la cosa ya no es solo de coste: es de privacidad.

La buena noticia es que hoy podemos montar un **RAG local**: un asistente que lee *nuestros* documentos, los deja indexados en nuestro disco y responde preguntas sobre ellos sin enviar nada a internet y sin gastar un euro en APIs. En este lab lo montamos de cero, primero con un script pequeño y luego con una interfaz bonita sin tocar código.

¡Vamos a ello!

# 2. Prerrequisitos

Para este lab necesitaremos:

- Un equipo donde podamos instalar [Ollama](https://docs.ollama.com/) (vale un portátil normal; con 8 GB de RAM ya se puede empezar).
- Una carpeta con documentos reales: PDFs, Word, notas en texto, lo que tengamos.
- Python 3 instalado si queremos la versión con script.
- Un poco de paciencia la primera vez que descarguemos los modelos.
- Ganas de dejar de copiar y pegar documentos enteros en un chat.

No necesitamos GPU de gama alta ni cuenta en ningún sitio. Todo corre en local.

# 3. ¿Qué vamos a montar?

En resumen, estas son las tareas que vamos a realizar:

- Instalar Ollama y dos modelos: uno para entender preguntas y otro para "leer" documentos.
- Trocear nuestros documentos en pedazos manejables.
- Convertir esos pedazos en vectores (embeddings) y guardarlos en una base local.
- Preguntar en lenguaje natural y recuperar solo los trozos que importan.
- Dejar que el modelo local responda con ese contexto recortado, citando la fuente.

Este es el esquema completo de lo que vamos a construir:

![Pipeline de un RAG local con tus propios documentos](capture-rag-pipeline.svg)

Fíjate en lo importante: al modelo no le mandamos el documento entero. Le mandamos solo los 3 o 4 trozos relevantes para la pregunta. Eso es justo lo que en esta web nos gusta: menos contexto, menos coste y normalmente mejor respuesta.

# 4. Qué es un RAG (sin tecnicismos)

RAG son las siglas de *Retrieval-Augmented Generation*, pero olvida las siglas. La idea es muy sencilla y se entiende con una analogía:

> Un modelo de IA es como un compañero muy listo que no se ha leído tus documentos. Un RAG es darle, justo antes de responder, las dos o tres páginas exactas que necesita para contestar bien.

En vez de meter el manual entero en su cabeza (caro y lento), le pasamos solo el fragmento que toca. Para encontrar ese fragmento usamos **embeddings**: una forma de convertir texto en números de manera que los textos que hablan de lo mismo queden "cerca". Cuando preguntamos algo, buscamos los trozos más cercanos a la pregunta y se los damos al modelo.

Lo bonito es que todo este proceso —trocear, vectorizar, buscar y responder— lo podemos hacer en local. Tus documentos nunca salen del equipo.

# 5. Paso 1: instalar Ollama y los dos modelos

Para un RAG necesitamos dos modelos distintos:

- Un **modelo de chat**, que será quien redacte la respuesta. Nos vale uno pequeño como `llama3.2:3b`.
- Un **modelo de embeddings**, especializado en convertir texto en vectores. Aquí `nomic-embed-text` es una opción ligera y muy usada.

## 5.1. Cómo prepararlo paso a paso

1. Instala Ollama desde su [documentación oficial](https://docs.ollama.com/).
2. Abre una terminal.
3. Descarga el modelo de chat:

```bash
ollama pull llama3.2:3b
```

4. Descarga el modelo de embeddings:

```bash
ollama pull nomic-embed-text
```

5. Comprueba que los tienes:

```bash
ollama list
```

Si todo va bien, deberías ver algo parecido a esto en la terminal:

![Terminal descargando los modelos locales para el RAG](capture-rag-terminal.svg)

Con esto ya tenemos el motor. Recuerda: Ollama deja una API local en `http://localhost:11434`, que es la que vamos a usar tanto para embeddings como para chat.

# 6. Paso 2: preparar tus documentos

Antes de indexar, conviene ordenar un poco. No por capricho, sino porque la calidad del RAG depende muchísimo de la calidad de la entrada.

Recomendaciones prácticas:

- Mete los documentos en una sola carpeta, por ejemplo `./documentos`.
- Si tienes PDFs escaneados (imágenes), pásalos antes por un OCR; si no, no tendrán texto que leer.
- Quita lo que sea puro ruido: plantillas vacías, páginas de portada repetidas, anexos irrelevantes.
- Pon nombres de archivo claros. Cuando el asistente cite la fuente, agradecerás que ponga `contrato-alquiler.pdf` y no `escaneo_final_v3.pdf`.

Una regla sencilla que aplico siempre:

> Si un humano no entendería el documento sin contexto, el RAG tampoco. Limpia primero, indexa después.

# 7. Paso 3: trocear e indexar en local

Aquí está el corazón del asunto. Vamos a leer los documentos, cortarlos en trozos y guardar sus vectores en una base local. Para no complicarnos, usamos [ChromaDB](https://docs.trychroma.com/), que guarda el índice en una carpeta de tu disco.

Instalamos lo necesario:

```bash
pip install chromadb pypdf requests
```

Y montamos un script de indexado. La idea: por cada archivo, lo leemos, lo cortamos en trozos de tamaño parecido y pedimos a Ollama el embedding de cada trozo.

```python
import os
import requests
import chromadb
from pypdf import PdfReader

OLLAMA = "http://localhost:11434"
db = chromadb.PersistentClient(path="./db_local")
coleccion = db.get_or_create_collection("documentos")


def leer_texto(ruta):
    if ruta.lower().endswith(".pdf"):
        return "\n".join(p.extract_text() or "" for p in PdfReader(ruta).pages)
    with open(ruta, encoding="utf-8", errors="ignore") as f:
        return f.read()


def trocear(texto, tam=900, solape=150):
    trozos, i = [], 0
    while i < len(texto):
        trozos.append(texto[i:i + tam])
        i += tam - solape
    return [t.strip() for t in trozos if t.strip()]


def embedding(texto):
    r = requests.post(
        f"{OLLAMA}/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": texto},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["embedding"]


def indexar(carpeta):
    n = 0
    for nombre in os.listdir(carpeta):
        ruta = os.path.join(carpeta, nombre)
        for j, trozo in enumerate(trocear(leer_texto(ruta))):
            coleccion.add(
                ids=[f"{nombre}-{j}"],
                documents=[trozo],
                embeddings=[embedding(trozo)],
                metadatas=[{"fuente": nombre, "trozo": j}],
            )
            n += 1
    print(f"Indexados {n} trozos en ./db_local")


if __name__ == "__main__":
    indexar("./documentos")
```

Lo ejecutamos una vez:

```bash
python indexar.py
```

Dos detalles que marcan la diferencia:

- El **solape** (overlap) entre trozos evita cortar una frase justo por la mitad y perder el sentido.
- El **tamaño del trozo** es un equilibrio: trozos grandes dan más contexto pero diluyen la búsqueda; trozos pequeños afinan pero pueden quedarse cortos. Empieza por 900 caracteres y ajusta.

Lo bonito: este paso se hace una sola vez por documento. Una vez indexado, preguntar es instantáneo y gratis.

# 8. Paso 4: preguntar a tus documentos

Ahora la parte divertida. Cuando hacemos una pregunta:

1. Calculamos el embedding de la pregunta.
2. Buscamos en Chroma los trozos más cercanos.
3. Se los pasamos al modelo de chat como contexto.
4. Le pedimos que responda **solo** con eso y que cite la fuente.

```python
import requests
import chromadb

OLLAMA = "http://localhost:11434"
db = chromadb.PersistentClient(path="./db_local")
coleccion = db.get_collection("documentos")


def embedding(texto):
    r = requests.post(
        f"{OLLAMA}/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": texto},
        timeout=120,
    )
    return r.json()["embedding"]


def preguntar(pregunta, k=4):
    res = coleccion.query(query_embeddings=[embedding(pregunta)], n_results=k)
    trozos = res["documents"][0]
    fuentes = {m["fuente"] for m in res["metadatas"][0]}

    contexto = "\n---\n".join(trozos)
    prompt = f"""Responde a la pregunta usando SOLO el contexto.
Si la respuesta no está en el contexto, di que no lo sabes.

Contexto:
{contexto}

Pregunta: {pregunta}
"""
    r = requests.post(
        f"{OLLAMA}/api/chat",
        json={
            "model": "llama3.2:3b",
            "stream": False,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=180,
    )
    respuesta = r.json()["message"]["content"]
    return respuesta, fuentes


if __name__ == "__main__":
    texto, fuentes = preguntar("¿Cuántos días de preaviso pide el contrato?")
    print(texto)
    print("\nFuentes:", ", ".join(fuentes))
```

Y el resultado se parece a esto: una respuesta concreta, con sus fuentes, sin que nada haya salido del equipo.

![Respuesta del RAG local citando los documentos de origen](capture-rag-answer.svg)

Fíjate en el detalle del prompt: le decimos *"si la respuesta no está en el contexto, di que no lo sabes"*. Esto reduce muchísimo las alucinaciones. Un RAG bien montado prefiere decir "no lo sé" antes que inventarse una cláusula que no existe.

# 9. La versión sin código: Open WebUI

¿Y si no queremos tocar Python? Se puede. [Open WebUI](https://docs.openwebui.com/) es una interfaz de chat que se conecta a Ollama y trae RAG integrado: subes documentos, crea una colección y ya puedes chatear con ellos desde el navegador.

## 9.1. Cómo usarlo paso a paso

1. Asegúrate de tener Ollama corriendo con los dos modelos del paso 1.
2. Instala Open WebUI siguiendo su documentación (la vía habitual es con Docker).
3. Ábrelo en `http://localhost:3000` y crea tu usuario local.
4. Ve a la sección de documentos o "Knowledge" y crea una colección.
5. Sube tus PDFs o notas a esa colección.
6. En el chat, selecciona la colección y empieza a preguntar.

La experiencia es prácticamente la misma que un chat de pago, pero todo vive en tu equipo:

![Interfaz tipo Open WebUI con una colección de documentos cargada en local](capture-rag-openwebui.svg)

¿Cuándo elegir script y cuándo interfaz?

- **Script propio**: cuando quieres integrarlo en un flujo, automatizarlo o controlar cada paso.
- **Open WebUI**: cuando quieres que lo use gente no técnica del equipo, o simplemente para probar rápido sin programar.

# 10. Medir el ahorro (y la privacidad)

Como en cualquier lab de esta web, no vale con que "funcione": hay que medir si compensa.

Imagina un equipo que consulta sus manuales 40 veces al día. Si cada consulta sube un PDF de unas 12.000 palabras a un modelo de pago, el coste se va en transportar el mismo documento una y otra vez:

```text
Sin RAG (subiendo el documento entero):
  Consultas/mes:        ~880
  Tokens entrada/consulta: ~16.000
  Tokens/mes:           ~14.080.000

Con RAG local (solo 4 trozos relevantes):
  Tokens enviados a API de pago: 0
  Coste por token:               0
  Documentos fuera del equipo:   0
```

Dos columnas que apunto siempre:

- **Coste**: con RAG local pasa a cero, porque el modelo corre en tu máquina.
- **Privacidad**: ningún contrato, factura o dato de cliente sale del equipo. Para sectores regulados (legal, salud, banca) esto no es un extra, es el requisito.

Y una tercera, la honesta: **calidad**. Un modelo de 3B no razona como uno de pago grande. Para preguntas factuales sobre tus documentos suele ir sobrado; para análisis profundo o redacción final delicada, quizá quieras escalar a un modelo de pago solo en ese paso. La gracia del RAG local es que el 90% de las consultas las resuelves gratis y en privado.

# 11. Extras

## 11.1. Reindexar solo lo que cambia

No vuelvas a indexar toda la carpeta cada vez. Guarda la fecha de modificación de cada archivo y reprocesa solo los nuevos o los que han cambiado. El índice se mantiene barato.

## 11.2. Cuidado con los PDFs escaneados

Si un PDF es una foto, no tiene texto. Pásalo antes por OCR o el RAG no "verá" nada. Es el fallo número uno cuando alguien dice "no me encuentra nada".

## 11.3. Sube el número de trozos con cabeza

Recuperar 4 trozos suele ir bien. Si las respuestas se quedan cortas, prueba 6 u 8. Pero ojo: cuantos más trozos, más contexto y más lento; y si metes ruido, la respuesta empeora. Más no siempre es mejor.

## 11.4. Combínalo con el resto del stack

Este RAG local encaja perfecto como primera capa: responde gratis lo factual y, si detectas que una consulta necesita razonamiento serio, la escalas a un modelo de pago. Justo lo que vimos en los otros labs de la web.

# 12. Quiero el flujo completo

La receta sería:

1. Ollama instalado con `llama3.2:3b` y `nomic-embed-text`.
2. Carpeta `./documentos` limpia y con nombres claros.
3. Script de indexado que trocea y guarda embeddings en ChromaDB.
4. Script de preguntas que recupera los trozos relevantes y responde citando fuentes.
5. Open WebUI si quieres una interfaz para todo el equipo.
6. Medición de coste, privacidad y calidad.

Con esto tienes un asistente que conoce tus documentos, no se los enseña a nadie y no te cuesta un céntimo por pregunta. No es magia: es poner el modelo a leer solo lo que necesita, en tu propia casa.

<!-- en -->

# INDEX

1. Introduction
2. Requirements
3. What we are building
4. What a RAG is (no jargon)
5. Step 1: install Ollama and the two models
6. Step 2: prepare your documents
7. Step 3: chunk and index locally
8. Step 4: ask your documents
9. The no-code version: Open WebUI
10. Measuring the saving (and the privacy)
11. Extras
12. Full workflow

# 1. Introduction

How many times have we pasted a whole PDF into a paid AI chat just to ask one specific thing? A contract, a 40-page manual, the meeting notes... burning tokens every time we ask again.

It works, yes. But we pay to upload the whole document over and over, and that document leaves our machine and ends up on someone else's server. If those are contracts, invoices or client data, it stops being only about cost: it is about privacy.

The good news is that today we can build a **local RAG**: an assistant that reads *our* documents, keeps them indexed on our disk and answers questions about them without sending anything to the internet and without spending a cent on APIs. In this lab we build it from scratch, first with a small script and then with a nice no-code interface.

Let's get to it!

# 2. Requirements

We need a machine for [Ollama](https://docs.ollama.com/) (a normal laptop works; 8 GB of RAM is enough to start), a folder with real documents, Python 3 for the script version, some patience the first time we download the models, and the will to stop copy-pasting whole documents into a chat.

No high-end GPU and no account anywhere. Everything runs locally.

# 3. What we are building

We install Ollama and two models (one for chat, one for embeddings), chunk our documents, turn those chunks into vectors stored in a local database, ask in natural language to retrieve only the relevant chunks, and let the local model answer with that trimmed context, citing the source.

![Pipeline of a local RAG with your own documents](capture-rag-pipeline-en.svg)

The key point: we never send the whole document to the model, only the 3 or 4 chunks relevant to the question. Less context, less cost and usually a better answer.

# 4. What a RAG is (no jargon)

RAG stands for *Retrieval-Augmented Generation*, but forget the acronym:

> An AI model is like a very smart colleague who has not read your documents. A RAG hands them, right before answering, the exact two or three pages they need.

To find that fragment we use **embeddings**: a way to turn text into numbers so that texts about the same topic end up "close". When we ask something, we search for the chunks closest to the question and give them to the model. The whole process runs locally and your documents never leave the machine.

# 5. Step 1: install Ollama and the two models

A RAG needs two models: a **chat model** to write the answer (a small `llama3.2:3b` is fine) and an **embedding model** to turn text into vectors (`nomic-embed-text` is a light, popular choice).

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
ollama list
```

![Terminal downloading the local models for the RAG](capture-rag-terminal-en.svg)

Ollama exposes a local API at `http://localhost:11434`, which we will use for both embeddings and chat.

# 6. Step 2: prepare your documents

Put everything in one folder like `./documentos`, run OCR on scanned PDFs, remove pure noise (empty templates, repeated cover pages) and use clear file names so the citations are readable.

> If a human would not understand the document without context, neither will the RAG. Clean first, index later.

# 7. Step 3: chunk and index locally

We read the documents, cut them into similar-sized chunks and store their vectors in [ChromaDB](https://docs.trychroma.com/), which saves the index in a folder on your disk.

```bash
pip install chromadb pypdf requests
```

```python
import os
import requests
import chromadb
from pypdf import PdfReader

OLLAMA = "http://localhost:11434"
db = chromadb.PersistentClient(path="./db_local")
collection = db.get_or_create_collection("documents")


def read_text(path):
    if path.lower().endswith(".pdf"):
        return "\n".join(p.extract_text() or "" for p in PdfReader(path).pages)
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def chunk(text, size=900, overlap=150):
    out, i = [], 0
    while i < len(text):
        out.append(text[i:i + size])
        i += size - overlap
    return [c.strip() for c in out if c.strip()]


def embedding(text):
    r = requests.post(
        f"{OLLAMA}/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text},
        timeout=120,
    )
    return r.json()["embedding"]


def index(folder):
    for name in os.listdir(folder):
        for j, piece in enumerate(chunk(read_text(os.path.join(folder, name)))):
            collection.add(
                ids=[f"{name}-{j}"],
                documents=[piece],
                embeddings=[embedding(piece)],
                metadatas=[{"source": name, "chunk": j}],
            )
    print("Done")


if __name__ == "__main__":
    index("./documentos")
```

The **overlap** avoids cutting a sentence in half, and the **chunk size** is a trade-off: bigger gives more context but dilutes search; smaller is sharper but may fall short. Start at 900 characters and adjust. This runs once per document; after that, asking is instant and free.

# 8. Step 4: ask your documents

We embed the question, search Chroma for the nearest chunks, pass them to the chat model and ask it to answer **only** with that and cite the source.

```python
import requests
import chromadb

OLLAMA = "http://localhost:11434"
db = chromadb.PersistentClient(path="./db_local")
collection = db.get_collection("documents")


def embedding(text):
    r = requests.post(
        f"{OLLAMA}/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text},
        timeout=120,
    )
    return r.json()["embedding"]


def ask(question, k=4):
    res = collection.query(query_embeddings=[embedding(question)], n_results=k)
    chunks = res["documents"][0]
    sources = {m["source"] for m in res["metadatas"][0]}
    context = "\n---\n".join(chunks)
    prompt = (
        "Answer using ONLY the context. If it is not there, say you do not know.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}"
    )
    r = requests.post(
        f"{OLLAMA}/api/chat",
        json={
            "model": "llama3.2:3b",
            "stream": False,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=180,
    )
    return r.json()["message"]["content"], sources
```

![Local RAG answer citing the source documents](capture-rag-answer-en.svg)

Notice the prompt: *"if it is not in the context, say you do not know"*. This kills most hallucinations. A well-built RAG prefers to say "I don't know" over inventing a clause that does not exist.

# 9. The no-code version: Open WebUI

If you do not want to touch Python, [Open WebUI](https://docs.openwebui.com/) is a chat interface that connects to Ollama and has RAG built in: upload documents, create a collection and chat with them from the browser.

1. Have Ollama running with the two models from step 1.
2. Install Open WebUI (usually via Docker).
3. Open `http://localhost:3000` and create your local user.
4. Create a collection under documents / "Knowledge".
5. Upload your PDFs or notes.
6. Select the collection in the chat and start asking.

![Open WebUI-style interface with a document collection loaded locally](capture-rag-openwebui-en.svg)

Use a **script** when you want to automate or integrate it; use **Open WebUI** when non-technical teammates should use it or you just want to test fast.

# 10. Measuring the saving (and the privacy)

```text
Without RAG (uploading the whole document):
  Queries/month:        ~880
  Input tokens/query:   ~16,000
  Tokens/month:         ~14,080,000

With local RAG (only 4 relevant chunks):
  Tokens sent to paid API: 0
  Cost per token:          0
  Documents leaving the machine: 0
```

Three columns to track: **cost** (drops to zero, the model runs on your machine), **privacy** (no contract or client data leaves the device — for regulated sectors this is the requirement, not a bonus) and the honest one, **quality**: a 3B model does not reason like a big paid one. For factual questions over your documents it is usually plenty; for deep analysis escalate just that step to a paid model. The point of local RAG is that 90% of queries are solved for free and in private.

# 11. Extras

- **Reindex only what changes**: store each file's modification date and reprocess only new or changed files.
- **Watch out for scanned PDFs**: if it is an image, run OCR first or the RAG sees nothing. This is the number one "it finds nothing" cause.
- **Raise the chunk count carefully**: 4 chunks is a good default; more context is slower and noisy chunks hurt the answer. More is not always better.
- **Combine it with the rest of the stack**: let the local RAG answer factual queries for free and escalate to a paid model only when real reasoning is needed.

# 12. Full workflow

1. Ollama with `llama3.2:3b` and `nomic-embed-text`.
2. A clean `./documentos` folder with clear names.
3. An indexing script that chunks and stores embeddings in ChromaDB.
4. A query script that retrieves relevant chunks and answers with sources.
5. Open WebUI if you want an interface for the whole team.
6. Measurement of cost, privacy and quality.

You get an assistant that knows your documents, shows them to no one and costs nothing per question. Not magic: just letting the model read only what it needs, in your own home.
