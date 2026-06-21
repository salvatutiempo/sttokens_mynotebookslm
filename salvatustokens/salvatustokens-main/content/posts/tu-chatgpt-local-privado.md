---
title_es: "Tu propio ChatGPT en local"
subtitle_es: "privado, gratis y montado en una tarde"
description_es: "Guía práctica para montar tu propia IA en local con Ollama, Qwen 3 y Open WebUI: un ChatGPT privado, sin coste por token y sin que tus datos salgan del equipo."
title_en: "Your own ChatGPT, running locally"
subtitle_en: "private, free and built in one afternoon"
description_en: "A practical guide to build your own local AI with Ollama, Qwen 3 and Open WebUI: a private ChatGPT, with no cost per token and without your data leaving the machine."
slug: tu-chatgpt-local-privado
author: salvatustokens
tags_es: IA local, Ollama, Qwen 3, privacidad, ahorro
tags_en: Local AI, Ollama, Qwen 3, privacy, savings
reading_time: 15 min
date: 2026-06-17
published: true
---

<!-- es -->

# ÍNDICE

1. Introducción
2. Prerrequisitos
3. ¿Qué vamos a montar?
4. Paso 1: instalar Ollama
5. Paso 2: elegir tu modelo según la RAM
6. Paso 3: tu ChatGPT privado con Open WebUI
7. Paso 4: conectarlo a tu código
8. Paso 5: el enfoque híbrido (local + pago)
9. ¿Cuánto te ahorras de verdad?
10. Extras
11. Quiero el montaje completo

# 1. Introducción

Voy a hacerte una pregunta incómoda: ¿sabes cuánto te gastas al mes en IA de pago?

Suma la suscripción del chat, las llamadas a la API, ese servicio que probaste y se renueva solo... Cuando echas cuentas de verdad, a más de uno le sale un susto. Y la tendencia va hacia arriba: las APIs no van a bajar de precio, y cada vez metemos IA en más cosas.

Aquí va la idea que mueve toda esta web: **para una buena parte de lo que usamos la IA a diario, no necesitamos pagar nada.** Resumir, redactar un email, reescribir un texto, clasificar, generar ideas, ayudarnos con código... todo eso lo puede hacer un modelo que corre en tu propio equipo, gratis, sin límite de tokens y sin que tus datos salgan de tu máquina.

Y no, no hablamos de algo cutre de hace dos años. En 2026 tenemos modelos abiertos como **Qwen 3**, **Gemma 4** o **Llama 4** que, en tu portátil, te resuelven el día a día sin despeinarse. Lo notas: respuesta instantánea, sin "estás en la cola", sin contador de tokens corriendo.

En este artículo montamos un **ChatGPT privado, en local, en una sola tarde**. Con su interfaz bonita, conectado a tu código y combinándolo con la IA de pago solo cuando de verdad hace falta.

¡Vamos a ello!

# 2. Prerrequisitos

Para esto necesitamos bastante poco:

- Un equipo normal. Con **8 GB de RAM** ya empezamos; con **16 GB** vamos sobrados para el día a día.
- Windows, Mac o Linux. Da igual, [Ollama](https://docs.ollama.com/) funciona en los tres.
- 20 minutos para descargar el primer modelo (pesa unos GB).
- Ganas de dejar de mirar el contador de tokens.

No hace falta GPU de 2.000 €, ni cuenta en ningún sitio, ni tarjeta de crédito. Todo corre en tu casa.

# 3. ¿Qué vamos a montar?

En resumen, estas son las piezas que vamos a juntar:

- **Ollama**: el motor que descarga y ejecuta los modelos.
- **Un modelo abierto** (Qwen 3, por ejemplo): el cerebro que piensa y responde.
- **Open WebUI**: una interfaz de chat clavada a ChatGPT, pero en tu navegador y 100% local.
- **La API local**: para enchufar la IA a tus scripts y automatizaciones.

Visto en conjunto, queda así:

![Arquitectura de un asistente de IA que corre entero en tu equipo, sin nube](capture-asistente-arquitectura.svg)

Fíjate en lo importante: **no hay ninguna flecha que salga a internet.** Tu pregunta entra, el modelo la procesa en tu equipo y la respuesta sale. Punto. Eso es justo lo que en esta web nos gusta: cero coste por token y cero datos viajando por ahí.

# 4. Paso 1: instalar Ollama

Ollama es lo que hace que todo esto sea fácil. Se encarga de descargar el modelo, usar tu GPU si la tienes y levantar una API local sin que tú toques nada raro.

## 4.1. Cómo instalarlo paso a paso

1. Entra en la [documentación oficial de Ollama](https://docs.ollama.com/) y descarga el instalador para tu sistema.
2. Instálalo como cualquier otro programa.
3. Abre una terminal.
4. Lanza tu primer modelo con un solo comando:

```bash
ollama run qwen3:8b
```

La primera vez se descarga el modelo (unos GB, paciencia). Cuando termina, te deja hablar con él ahí mismo, en la terminal:

![Terminal instalando Ollama y arrancando Qwen 3 en local](capture-asistente-instalacion.svg)

Y ya está. Sí, así de simple. Eso que estás viendo es un modelo de IA corriendo en tu equipo, respondiendo sin enviar nada a internet y sin cobrarte un céntimo.

Un par de comandos que te vendrán bien:

```bash
ollama list          # ver los modelos que tienes
ollama pull gemma3:4b   # descargar otro modelo
ollama rm qwen3:8b   # borrar uno para liberar espacio
```

# 5. Paso 2: elegir tu modelo según la RAM

Aquí está la pregunta del millón: **¿qué modelo descargo?** Y la respuesta honesta es: el que te entre con holgura en la RAM, no el que tenga mejor fama.

Un modelo enorme que va a tirones no sirve de nada. Es mejor uno mediano que vuele. Esta es la chuleta que yo seguiría a junio de 2026:

![Qué modelo de IA local elegir según la RAM de tu equipo](capture-asistente-modelos.svg)

Resumiendo:

## 5.1. Si tienes 8 GB de RAM

Tira de modelos de 3B-4B como `qwen3:4b`, `gemma3:4b` o `llama3.2:3b`. Van de sobra para resumir, clasificar, reescribir y tareas del día a día.

## 5.2. Si tienes 16 GB de RAM (el punto dulce)

`qwen3:8b` y para casa. Es el equilibrio perfecto entre listo y ligero: te sirve como asistente general y además se defiende muy bien con código. Si solo vas a instalar un modelo, instala este.

¿Necesitas que razone más (matemáticas, lógica, problemas de varios pasos)? Prueba un modelo de razonamiento como `deepseek-r1:8b`.

## 5.3. Si tienes 32 GB o más

Aquí ya puedes con `qwen3:32b`, `gemma4:27b` o `llama4-scout`. Esto es nivel "doy servicio a todo mi equipo" o "monto un RAG serio con mis documentos".

La regla que aplico siempre:

> No te enamores del nombre del modelo. Descarga dos, pásales tus tareas reales y quédate con el que vaya fino en TU equipo. La mejor IA local es la que no te hace esperar.

# 6. Paso 3: tu ChatGPT privado con Open WebUI

Hablar con el modelo desde la terminal está bien para probar, pero seamos sinceros: queremos algo que se parezca a ChatGPT. Eso es [Open WebUI](https://docs.openwebui.com/): una interfaz de chat que se conecta a Ollama y te da historial de conversaciones, varios modelos, subida de archivos... todo en tu navegador y sin salir de tu equipo.

## 6.1. Cómo ponerlo en marcha

La vía más cómoda es con Docker. Con Ollama ya corriendo, lanzas:

```bash
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main
```

Después:

1. Abre `http://localhost:3000` en el navegador.
2. Crea tu usuario (es local, se queda en tu equipo).
3. Arriba selecciona el modelo, por ejemplo `qwen3:8b`.
4. Empieza a chatear.

Y te encuentras con esto, que reconocerás al instante:

![Interfaz de chat tipo ChatGPT corriendo en local con Open WebUI](capture-asistente-chat.svg)

Mismo aspecto que el chat de pago, misma comodidad. La diferencia es que aquí no hay suscripción, no hay límite de mensajes y nada de lo que escribes se va a un servidor ajeno. Para gente del equipo que no es técnica, esto es oro: usan "el ChatGPT de la empresa" sin que ningún dato sensible salga de la oficina.

# 7. Paso 4: conectarlo a tu código

Aquí es donde la cosa se pone seria de verdad. Ollama no es solo un chat: levanta una **API local** en `http://localhost:11434`, y además es compatible con el formato de OpenAI. ¿Qué significa eso? Que puedes reutilizar el mismo código que ya usas para la IA de pago, cambiando solo dos líneas.

Mira qué bonito. Instalas la librería:

```bash
pip install openai
```

Y apuntas al modelo local en vez de a un servicio de pago:

```python
from openai import OpenAI

# Apuntamos a Ollama en local, no a la nube
cliente = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # da igual lo que pongas, es local
)

respuesta = cliente.chat.completions.create(
    model="qwen3:8b",
    messages=[
        {"role": "system", "content": "Eres un asistente claro y directo."},
        {"role": "user", "content": "Resume este email en 3 puntos: ..."},
    ],
)

print(respuesta.choices[0].message.content)
```

Eso es todo. Ese script funciona, no envía nada a internet y no te cuesta un euro por mucho que lo ejecutes mil veces. Imagina lo que esto significa para una automatización que procesa cientos de textos al día: lo que antes era una factura, ahora es gratis.

¿Y si prefieres no depender de ninguna librería? La API cruda también es sencilla:

```python
import requests

respuesta = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "qwen3:8b",
        "stream": False,
        "messages": [{"role": "user", "content": "Dame 5 ideas de post para LinkedIn"}],
    },
    timeout=120,
)

print(respuesta.json()["message"]["content"])
```

# 8. Paso 5: el enfoque híbrido (local + pago)

Ahora la parte honesta, porque en esta web no vendemos humo: **la IA local no lo sustituye todo.** Un modelo de 8B que corre en tu portátil no razona como el último modelo gigante de pago. Y no pasa nada.

La jugada inteligente no es "todo local" ni "todo pago". Es **híbrida**:

- Lo mecánico y repetitivo → **local** (gratis y privado).
- Lo difícil, ambiguo o crítico → **pago** (pagas por inteligencia de verdad).

¿Dónde pongo yo la línea?

> Si el fallo se detecta rápido y se corrige fácil, va a local. Si el fallo cuesta dinero, reputación o seguridad, paga calidad.

Y esto se puede automatizar con una función pequeña que decida sola por dónde mandar cada tarea:

```python
def elegir_modelo(tarea):
    if tarea["riesgo"] == "alto":
        return "pago"
    if tarea["tipo"] in {"resumen", "clasificacion", "reescritura", "extraccion"}:
        return "local"
    if tarea["tokens"] > 8000:   # texto largo: que lo prepare local primero
        return "local"
    return "pago"
```

La gracia es que el 80% de las consultas del día a día caen en "local" y se resuelven gratis. Solo el 20% difícil llega al modelo de pago. Ahí es donde está el ahorro de verdad.

Si quieres profundizar en cómo repartir tareas y montar un router automático, lo tienes detallado en el resto de labs de la web.

# 9. ¿Cuánto te ahorras de verdad?

Vamos a los números, que es lo que mueve esto. Pensemos en alguien que usa IA de forma intensiva: suscripciones premium, llamadas a API en sus automatizaciones, etc. Es fácil irse a unos 200 € al mes. Al año:

![Comparativa de coste anual entre IA de pago e IA local](capture-asistente-ahorro.svg)

```text
IA de pago (uso intensivo):   ~200 €/mes  ->  ~2.400 €/año
IA local:                     luz + equipo ya amortizado  ->  ~0 €
```

Ojo, no es magia: el equipo cuesta dinero y la luz también. Pero si ya tienes un portátil decente, el coste extra de mover a local buena parte de tus tareas es prácticamente cero. Y cada mes que pasa, el ahorro se acumula.

Y hay un segundo ahorro que no sale en la factura pero que cada vez vale más: la **privacidad**. Tus contratos, los datos de tus clientes, tu código... no salen de tu equipo. Con la **EU AI Act** apretando a partir de agosto de 2026 sobre los sistemas de alto riesgo, para sectores como legal, salud o banca esto ya no es un extra simpático: empieza a ser un requisito.

Tres columnas que yo apuntaría siempre:

- **Coste**: con local, baja a casi cero.
- **Privacidad**: tus datos se quedan en casa.
- **Calidad**: para el día a día va sobrado; para lo difícil, escalas a pago. Lo mejor de los dos mundos.

# 10. Extras

## 10.1. Dale personalidad a tu asistente

Con un `Modelfile` puedes crear tu propia versión del modelo con instrucciones fijas, para que siempre responda como tú quieres:

```text
FROM qwen3:8b
SYSTEM Eres el asistente de redacción de salvatustokens. Respondes en español, claro y directo, sin rodeos.
PARAMETER temperature 0.4
```

```bash
ollama create mi-asistente -f Modelfile
ollama run mi-asistente
```

## 10.2. También entiende imágenes

Modelos como `gemma3:4b` o las variantes con visión aceptan imágenes directamente. Puedes pasarle una captura y pedirle que la resuma o extraiga el texto, todo en local.

## 10.3. Mídelo con tus tareas, no con benchmarks

Un modelo puede ir muy arriba en un ranking y fallar justo en lo tuyo. Coge 20 ejemplos reales de tu día a día, pásaselos y decide con eso. La mejor métrica es "¿me resuelve MIS tareas?".

## 10.4. No lo cierres al apagar

Ollama puede quedarse corriendo de fondo para que el asistente esté siempre listo. Y si te quedas sin internet, sigue funcionando igual. Esa sensación de "mi IA no depende de nadie" engancha.

# 11. Quiero el montaje completo

La receta, de principio a fin:

1. **Ollama** instalado.
2. Un **modelo acorde a tu RAM** (`qwen3:8b` si tienes 16 GB y solo quieres uno).
3. **Open WebUI** para tener tu ChatGPT privado en el navegador.
4. La **API local** conectada a tus scripts con dos líneas de código.
5. Un **router híbrido** que mande lo fácil a local y lo difícil a pago.
6. Una **medición** mensual de coste, privacidad y calidad.

Con esto tienes una IA que es tuya de verdad: rápida, privada, sin contador de tokens y montada en una tarde. No es renunciar a la IA de pago, es dejar de pagarla para lo que no hace falta.

Y esa, al final, es la idea de toda esta web: que la IA trabaje para ti sin vaciarte la cartera.

<!-- en -->

# INDEX

1. Introduction
2. Requirements
3. What we are building
4. Step 1: install Ollama
5. Step 2: choose your model by RAM
6. Step 3: your private ChatGPT with Open WebUI
7. Step 4: connect it to your code
8. Step 5: the hybrid approach (local + paid)
9. How much do you really save?
10. Extras
11. Full setup

# 1. Introduction

An uncomfortable question: do you know how much you spend on paid AI every month?

Add up the chat subscription, the API calls, that service you tried and now auto-renews... When you actually do the math, many people get a scare. And the trend points up: APIs are not getting cheaper, and we keep putting AI into more things.

Here is the idea behind this whole site: **for a big chunk of what we use AI for daily, we do not need to pay anything.** Summarizing, drafting an email, rewriting, classifying, brainstorming, helping with code... all of that can run on your own machine, for free, with no token limit and without your data leaving your computer.

And no, this is not the clunky stuff from two years ago. In 2026 we have open models like **Qwen 3**, **Gemma 4** or **Llama 4** that handle your day-to-day on a laptop without breaking a sweat: instant answers, no queue, no token counter ticking.

In this article we build a **private, local ChatGPT in a single afternoon**, with a proper interface, wired to your code and combined with paid AI only when it is really needed.

Let's get to it!

# 2. Requirements

Very little: a normal machine (**8 GB of RAM** to start, **16 GB** is plenty for daily use), Windows, Mac or Linux (Ollama runs on all three), 20 minutes to download the first model, and the will to stop staring at a token counter. No 2,000 € GPU, no account anywhere, no credit card. Everything runs at home.

# 3. What we are building

- **Ollama**: the engine that downloads and runs the models.
- **An open model** (Qwen 3, for example): the brain.
- **Open WebUI**: a ChatGPT-like chat interface in your browser, 100% local.
- **The local API**: to plug AI into your scripts.

![Architecture of an AI assistant running entirely on your machine, no cloud](capture-asistente-arquitectura-en.svg)

Notice the key detail: **no arrow leaves to the internet.** Your prompt goes in, the model processes it on your machine, the answer comes out. That's it: zero cost per token, zero data traveling around.

# 4. Step 1: install Ollama

Ollama makes all of this easy: it downloads the model, uses your GPU if you have one and serves a local API without you touching anything weird.

1. Download the installer from the [official Ollama docs](https://docs.ollama.com/).
2. Install it like any other program.
3. Open a terminal.
4. Launch your first model:

```bash
ollama run qwen3:8b
```

![Terminal installing Ollama and starting Qwen 3 locally](capture-asistente-instalacion-en.svg)

That's it. What you're seeing is an AI model running on your machine, answering without sending anything to the internet and without charging you a cent.

```bash
ollama list           # see your models
ollama pull gemma3:4b # download another one
ollama rm qwen3:8b    # delete one to free space
```

# 5. Step 2: choose your model by RAM

The million-dollar question: **which model do I download?** Honest answer: the one that fits comfortably in your RAM, not the one with the best reputation. A huge model that stutters is useless; a mid one that flies wins.

![Which local AI model to choose based on your RAM](capture-asistente-modelos-en.svg)

- **8 GB**: 3B-4B models like `qwen3:4b`, `gemma3:4b` or `llama3.2:3b`. Plenty for summaries, classification, rewriting.
- **16 GB (sweet spot)**: `qwen3:8b` and done. The perfect balance of smart and light, and good at code too. If you install one model, install this. Need more reasoning? Try `deepseek-r1:8b`.
- **32 GB+**: `qwen3:32b`, `gemma4:27b` or `llama4-scout`. Team-serving, serious RAG territory.

> Don't fall in love with the model name. Download two, run your real tasks through them and keep the one that flies on YOUR machine. The best local AI is the one that doesn't make you wait.

# 6. Step 3: your private ChatGPT with Open WebUI

The terminal is fine for testing, but we want something that feels like ChatGPT. That's [Open WebUI](https://docs.openwebui.com/): a chat interface that connects to Ollama with conversation history, multiple models and file uploads, all in your browser.

With Ollama running, the easiest path is Docker:

```bash
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main
```

Then open `http://localhost:3000`, create your local user, pick `qwen3:8b` and start chatting.

![ChatGPT-style chat interface running locally with Open WebUI](capture-asistente-chat-en.svg)

Same look, same comfort, but no subscription, no message limit and nothing leaving your machine. For non-technical teammates this is gold: they use "the company ChatGPT" without any sensitive data leaving the office.

# 7. Step 4: connect it to your code

Ollama serves a **local API** at `http://localhost:11434`, and it is OpenAI-compatible. That means you can reuse the same code you already use for paid AI, changing just two lines.

```bash
pip install openai
```

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # anything works, it's local
)

response = client.chat.completions.create(
    model="qwen3:8b",
    messages=[
        {"role": "system", "content": "You are a clear, direct assistant."},
        {"role": "user", "content": "Summarize this email in 3 bullets: ..."},
    ],
)

print(response.choices[0].message.content)
```

That script works, sends nothing to the internet and costs nothing no matter how many times you run it. For an automation processing hundreds of texts a day, what used to be an invoice is now free.

# 8. Step 5: the hybrid approach (local + paid)

The honest part: **local AI does not replace everything.** An 8B model on your laptop does not reason like the latest giant paid model. And that's fine.

The smart move is **hybrid**: mechanical and repetitive work → **local** (free and private); hard, ambiguous or critical work → **paid** (pay for real intelligence).

> If a mistake is caught fast and fixed easily, go local. If a mistake costs money, reputation or security, pay for quality.

```python
def choose_model(task):
    if task["risk"] == "high":
        return "paid"
    if task["type"] in {"summary", "classification", "rewrite", "extraction"}:
        return "local"
    if task["tokens"] > 8000:
        return "local"
    return "paid"
```

About 80% of daily queries fall into "local" and are solved for free. Only the hard 20% reaches the paid model. That's where the real saving is.

# 9. How much do you really save?

Think of someone using AI intensively: premium subscriptions, API calls in automations... easily around 200 € a month. Per year:

![Annual cost comparison between paid AI and local AI](capture-asistente-ahorro-en.svg)

```text
Paid AI (intensive use):   ~200 €/month  ->  ~2,400 €/year
Local AI:                  power + already-amortized machine  ->  ~0 €
```

Not magic: the machine and the electricity cost money. But if you already have a decent laptop, moving a big chunk of your tasks to local costs almost nothing extra, and the saving compounds every month.

There's a second saving that never shows on the invoice: **privacy**. Your contracts, client data and code never leave your machine. With the **EU AI Act** tightening on high-risk systems from August 2026, for sectors like legal, health or banking this stops being a nice extra and becomes a requirement.

Three columns to track: **cost** (drops to near zero), **privacy** (your data stays home) and **quality** (plenty for daily work; escalate the hard stuff to paid). The best of both worlds.

# 10. Extras

- **Give it personality** with a `Modelfile` (fixed system prompt + temperature), then `ollama create mi-asistente -f Modelfile`.
- **It also reads images**: models like `gemma3:4b` accept screenshots to summarize or extract text, all local.
- **Measure with your tasks, not benchmarks**: 20 real examples beat any ranking.
- **Keep it running**: Ollama can stay in the background so your assistant is always ready, and it still works offline.

# 11. Full setup

1. **Ollama** installed.
2. A **model that fits your RAM** (`qwen3:8b` if you have 16 GB and want just one).
3. **Open WebUI** for your private ChatGPT in the browser.
4. The **local API** wired to your scripts in two lines.
5. A **hybrid router** sending easy tasks local and hard ones to paid.
6. Monthly **measurement** of cost, privacy and quality.

You get an AI that is truly yours: fast, private, no token counter, built in one afternoon. Not giving up paid AI, just not paying for what doesn't need it.

That, in the end, is the idea behind this whole site: let AI work for you without emptying your wallet.
