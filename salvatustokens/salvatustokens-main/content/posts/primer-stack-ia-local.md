---
title_es: "Montar un primer stack"
subtitle_es: "de IA local para ahorrar tokens"
description_es: "Lab práctico para montar un primer stack con Ollama, modelos pequeños, API local y criterios para decidir qué tareas mover a SLM."
title_en: "Building a first"
subtitle_en: "local AI stack to save tokens"
description_en: "A practical lab for building a first local AI stack with Ollama, small models, local API and criteria for choosing SLM tasks."
slug: primer-stack-ia-local
author: salvatustokens
tags_es: IA local, Ollama, SLM, productividad
tags_en: Local AI, Ollama, SLM, productivity
reading_time: 12 min
date: 2026-05-01
published: false
---

<!-- es -->

# ÍNDICE

1. Introducción
2. Prerrequisitos
3. ¿Qué vamos a montar?
4. Instalar Ollama
5. Elegir modelos pequeños
6. Definir tareas válidas para SLM
7. Crear un servicio local de clasificación
8. Medir calidad, coste y tiempo
9. Extras
10. Quiero el stack completo

# 1. Introducción

Cuando hablamos de IA local, muchas veces parece que tenemos que comprar una GPU enorme, montar servidores y convertir nuestra mesa en un mini datacenter.

La realidad es que para empezar a ahorrar tokens no necesitamos tanto. Necesitamos encontrar tareas estrechas, repetitivas y de bajo riesgo donde un modelo pequeño pueda preparar el terreno antes de llamar a un modelo de pago.

El objetivo de este lab no es sustituir toda la IA de pago. El objetivo es crear una primera capa barata.

# 2. Prerrequisitos

Para este lab necesitaremos:

- Un equipo donde podamos instalar [Ollama](https://docs.ollama.com/).
- Un conjunto de textos reales de prueba.
- Varias tareas candidatas de bajo riesgo.
- Una forma de medir aciertos y errores.
- Un modelo de pago para comparar resultado final cuando haga falta.

# 3. ¿Qué vamos a montar?

En resumen, estas son las tareas que vamos a realizar:

- Instalar Ollama.
- Descargar un modelo pequeño.
- Probar tareas de clasificación, resumen y extracción.
- Crear una pequeña función local.
- Escalar a modelo de pago cuando el resultado no sea fiable.

El flujo quedaría así:

![Pipeline para usar IA local como primera capa](capture-local-routing.svg)

# 4. Instalar Ollama

Ollama expone una API local por defecto en `http://localhost:11434/api`, y permite ejecutar modelos desde terminal o vía HTTP. La documentación oficial incluye endpoints como `/api/generate` y `/api/chat`.

## 4.1. Cómo usar Ollama paso a paso

1. Instala Ollama desde su web/documentación oficial.
2. Abre una terminal.
3. Descarga y ejecuta un modelo pequeño:

```bash
ollama run llama3.2:1b
```

4. Escribe una prueba sencilla en la consola del modelo:

```text
Clasifica este ticket en una palabra: no puedo acceder a la VPN.
```

5. Si responde razonablemente, prueba el mismo modelo desde API:

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2:1b",
  "messages": [
    {"role": "user", "content": "Clasifica este ticket: no puedo acceder a la VPN"}
  ],
  "stream": false
}'
```

6. Si la respuesta es muy pobre, prueba con un modelo algo mayor:

```bash
ollama run llama3.2:3b
```

7. Crea una tabla de pruebas con 30 o 50 ejemplos reales.
8. Ejecuta el mismo prompt contra cada modelo.
9. Quédate con el modelo que dé menos errores en tu tarea, no con el que tenga mejor fama.

¿Por qué Ollama para empezar?

- Es sencillo de instalar.
- Permite cambiar de modelo rápido.
- Tiene API local.
- Es suficiente para laboratorios pequeños.
- Evita depender de una API externa para tareas repetitivas.

# 5. Elegir modelos pequeños

Un SLM no tiene que ser brillante en todo. Tiene que ser suficientemente bueno en una tarea concreta.

Según la ficha de [Llama 3.2 en Ollama](https://ollama.com/library/llama3.2), hay variantes pequeñas como 1B y 3B. La propia página presenta Llama 3.2 como una familia orientada a casos como diálogo multilingüe, recuperación, resumen y tareas de reescritura.

Yo empezaría así:

## 5.1. Modelo 1B

Útil para:

- clasificación simple,
- etiquetas,
- reescrituras cortas,
- normalizar texto,
- detectar idioma,
- generar títulos internos.

No lo usaría para:

- razonamiento complejo,
- decisiones ambiguas,
- redacción final importante,
- análisis profundo de código.

Ejemplo de tarea válida:

```text
Entrada: "El usuario no puede entrar a Forticlient desde casa"
Salida esperada: vpn
```

## 5.2. Modelo 3B

Útil para:

- resumir tickets,
- limpiar notas,
- convertir texto libre a JSON,
- preparar contexto para otro modelo,
- clasificar con algo más de matiz.

No lo usaría como juez único en temas críticos.

Ejemplo de tarea válida:

```text
Entrada: ticket largo con síntomas, cambios recientes y error.
Salida esperada: resumen de 5 líneas + categoría.
```

## 5.3. Otros modelos pequeños

Ollama también permite trabajar con familias como Gemma, Qwen, DeepSeek o Phi, dependiendo del catálogo disponible y de tu equipo. Mi recomendación práctica es no enamorarse del nombre del modelo: prueba 30 ejemplos reales y quédate con el que falle menos en tu tarea.

# 6. Definir tareas válidas para SLM

Buenas candidatas:

- clasificar emails,
- resumir notas internas,
- extraer fechas o importes,
- detectar duplicados,
- preparar contexto para otro modelo,
- convertir texto a estructura,
- crear un primer borrador que revisarás.

Malas candidatas para empezar:

- decisiones críticas,
- redacción final para clientes,
- tareas con mucho matiz,
- tareas donde no puedas revisar el resultado,
- casos legales, médicos o financieros sensibles.

La regla sencilla:

> Si el fallo se detecta rápido y se corrige fácil, puede ir a local. Si el fallo cuesta dinero, reputación o seguridad, paga calidad.

# 7. Crear un servicio local de clasificación

Podemos crear una función pequeña que mande a Ollama una tarea concreta. Por ejemplo: clasificar tickets en `vpn`, `correo`, `hardware`, `software` u `otro`.

Pasos:

1. Define las categorías permitidas.
2. Prepara 30 tickets reales ya clasificados a mano.
3. Escribe un prompt que obligue a responder solo una categoría.
4. Llama a Ollama desde Python.
5. Valida que la respuesta pertenece a la lista.
6. Si la respuesta no es válida, reintenta o escala a modelo de pago.

```python
import requests

def clasificar_ticket(texto):
    prompt = f"""
Clasifica el siguiente ticket en una sola categoria:
vpn, correo, hardware, software, otro.

Ticket:
{texto}

Responde solo con la categoria.
"""
    respuesta = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3.2:1b",
            "stream": False,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    respuesta.raise_for_status()
    return respuesta.json()["message"]["content"].strip().lower()
```

Esto no es una arquitectura final. Es un laboratorio. La gracia es probar si, con 100 tickets reales, el modelo acierta lo suficiente.

Una validación mínima:

```python
CATEGORIAS = {"vpn", "correo", "hardware", "software", "otro"}

categoria = clasificar_ticket("No puedo abrir Outlook")
if categoria not in CATEGORIAS:
    categoria = "revisar_con_modelo_pago"
```

# 8. Medir calidad, coste y tiempo

Podemos apuntarlo así:

```text
Tarea: clasificar tickets
Modelo local: llama3.2:1b
Aciertos: 86 de 100
Tokens evitados: 420.000 al mes
Revisión manual: baja
Decisión: usar local con fallback a pago
```

Si falla en casos concretos, no lo descartes todavía. Puedes añadir reglas:

- si la confianza es baja, escalar a pago,
- si aparecen palabras críticas, escalar a pago,
- si el texto supera cierto tamaño, resumir primero,
- si el resultado no está en la lista permitida, repetir o escalar.

# 9. Extras

## 9.1. Usa Modelfile cuando quieras especializar

Ollama permite crear modelos personalizados con `Modelfile`. La documentación oficial indica que `FROM` define el modelo base y que se pueden añadir parámetros o instrucciones.

Pasos:

1. Crea un archivo llamado `Modelfile`.
2. Indica el modelo base con `FROM`.
3. Añade una instrucción de sistema.
4. Baja la temperatura si quieres respuestas más repetibles.
5. Crea el modelo personalizado.
6. Pruébalo con tus ejemplos reales.

Ejemplo de `Modelfile`:

```text
FROM llama3.2:1b
SYSTEM Eres un clasificador de tickets. Responde solo con una categoria permitida.
PARAMETER temperature 0
```

Comando conceptual:

```bash
ollama create clasificador-tickets -f Modelfile
ollama run clasificador-tickets
```

Esto ayuda a que el modelo sea menos creativo y más repetible.

## 9.2. Guarda ejemplos fallidos

Los fallos son oro. Sirven para saber cuándo pasar a modelo de pago automáticamente.

## 9.3. No midas solo velocidad

Un modelo local puede ser rápido y barato, pero si te obliga a revisar todo manualmente, no has ahorrado.

# 10. Quiero el stack completo

La versión inicial sería:

1. Ollama instalado.
2. Modelo pequeño, por ejemplo `llama3.2:1b` o `llama3.2:3b`.
3. Carpeta con ejemplos reales.
4. Script de prueba.
5. Medición de aciertos.
6. Regla para escalar a modelo de pago.

Con esto ya tenemos algo mantenible, barato y fácil de mejorar.

<!-- en -->

# INDEX

1. Introduction
2. Requirements
3. What we are building
4. Installing Ollama
5. Choosing small models
6. Valid SLM tasks
7. Local classification service
8. Measuring quality, cost and time
9. Extras
10. Full stack

# 1. Introduction

Local AI does not have to start with a huge GPU. The first goal is to find narrow, repeated, low-risk tasks where a small model can prepare work before a paid model is called.

# 2. Requirements

We need a machine for [Ollama](https://docs.ollama.com/), real examples, candidate low-risk tasks, a way to measure accuracy and a paid model for comparison.

# 3. What we are building

We install Ollama, download a small model, test classification, summarization and extraction, create a local function and escalate to paid AI when needed.

![Pipeline for using local AI as a first layer](capture-local-routing-en.svg)

# 4. Installing Ollama

Ollama serves a local API at `http://localhost:11434/api` and provides endpoints such as `/api/generate` and `/api/chat`.

```bash
ollama run llama3.2:1b
```

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2:1b",
  "messages": [
    {"role": "user", "content": "Classify this ticket: I cannot access VPN"}
  ],
  "stream": false
}'
```

# 5. Choosing small models

The [Llama 3.2 page on Ollama](https://ollama.com/library/llama3.2) lists small 1B and 3B variants. Use 1B for simple classification, tags and short rewrites; use 3B for summaries, JSON extraction and slightly more nuanced classification.

# 6. Valid SLM tasks

Good tasks: classify emails, summarize internal notes, extract dates, detect duplicates, prepare context and create drafts. Bad first tasks: critical decisions, final client writing and anything hard to review.

# 7. Local classification service

```python
import requests

def classify_ticket(text):
    prompt = f"Classify this ticket as vpn, email, hardware, software or other:\n{text}"
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3.2:1b",
            "stream": False,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["message"]["content"].strip().lower()
```

# 8. Measuring quality, cost and time

Track accuracy, avoided tokens, manual review and decision. If the model fails only in specific cases, add escalation rules.

# 9. Extras

Use Ollama `Modelfile` to specialize behavior, keep failed examples, and do not measure speed alone.

# 10. Full stack

Ollama, a small model, real examples, a test script, accuracy tracking and a fallback rule to paid AI.
