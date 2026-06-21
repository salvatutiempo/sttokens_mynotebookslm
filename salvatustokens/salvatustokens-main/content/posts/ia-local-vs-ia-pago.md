---
title_es: "Repartir tareas entre IA local"
subtitle_es: "y modelos de pago sin quemar tokens"
description_es: "Lab práctico para repartir tareas entre IA local, modelos de pago, GPUs externas y routers automáticos como LiteLLM u OpenRouter."
title_en: "Splitting work between local AI"
subtitle_en: "and paid models without burning tokens"
description_en: "A practical lab for splitting work between local AI, paid models, external GPUs and automatic routers such as LiteLLM or OpenRouter."
slug: ia-local-vs-ia-pago
author: salvatustokens
tags_es: IA local, IA de pago, Runpod, LiteLLM
tags_en: Local AI, paid AI, Runpod, LiteLLM
reading_time: 13 min
date: 2026-05-01
published: false
---

<!-- es -->

# ÍNDICE

1. Introducción
2. Prerrequisitos
3. ¿Qué vamos a construir?
4. Nivel 1: reglas y scripts
5. Nivel 2: IA local
6. Nivel 3: GPU externa con Runpod
7. Nivel 4: modelo de pago
8. Automatizar el cambio de modelo
9. Ejemplo de router sencillo
10. Extras
11. Quiero el flujo completo

# 1. Introducción

¿No nos ha pasado alguna vez que empezamos a usar inteligencia artificial para todo y, cuando nos damos cuenta, cada pequeña tarea acaba pasando por el modelo más caro?

Esto es muy cómodo, sí. Pero también es una forma bastante rápida de gastar tokens en tareas que no lo necesitan. En esta web nos gusta optimizar los recursos que consumen tiempo y dinero, por lo que vamos a montar una forma sencilla de decidir qué se queda en local, qué puede ir a una GPU alquilada y qué merece la pena mandar a un modelo de pago.

¡Vamos a ello!

# 2. Prerrequisitos

Para este lab necesitaremos:

- Tener identificadas varias tareas que ya estemos haciendo con IA.
- Saber aproximadamente cuántas veces se ejecutan al mes.
- Conocer el precio por millón de tokens del modelo de pago que usamos.
- Tener disponible una IA local o, al menos, una herramienta barata para hacer preprocesado.
- Tener claro qué tareas son críticas y cuáles son revisables.

# 3. ¿Qué vamos a construir?

En resumen, estas son las tareas que vamos a realizar:

- Crear un inventario rápido de prompts.
- Clasificar cada tarea según riesgo y repetición.
- Resolver primero con reglas cuando sea posible.
- Mover lo mecánico a local.
- Usar GPU externa si local no tiene potencia suficiente.
- Reservar el modelo de pago para razonamiento y salida final.
- Automatizar el cambio de modelo según contexto.

Esta sería una captura de ejemplo del inventario que usaremos:

![Inventario de prompts y gasto mensual por flujo](capture-token-inventory.svg)

# 4. Nivel 1: reglas y scripts

Antes de meter IA en todo, conviene preguntarse si la tarea necesita IA.

Ejemplos que muchas veces se resuelven con reglas:

- eliminar duplicados,
- detectar campos vacíos,
- validar JSON,
- clasificar por palabras clave,
- extraer fechas con expresiones regulares,
- cortar logs por nivel de error.

Ejemplo:

```python
def detectar_tipo_ticket(texto):
    texto = texto.lower()
    if "vpn" in texto or "forticlient" in texto:
        return "vpn"
    if "correo" in texto or "outlook" in texto:
        return "correo"
    if "pantalla" in texto or "teclado" in texto:
        return "hardware"
    return "revisar"
```

Si esto funciona en el 40% de los casos, ya has evitado llamadas innecesarias.

# 5. Nivel 2: IA local

La IA local encaja cuando la tarea requiere algo de lenguaje, pero no demasiado razonamiento.

Buenas tareas:

- resumir tickets,
- clasificar mensajes,
- convertir texto a JSON,
- extraer entidades,
- preparar contexto,
- detectar si una petición necesita escalar.

El reparto sano suele quedar así:

![Pipeline para repartir trabajo entre IA local e IA de pago](capture-local-routing.svg)

IA local:

- limpia,
- clasifica,
- resume,
- extrae campos,
- agrupa entradas parecidas.

IA de pago:

- razona,
- decide,
- redacta la versión final,
- revisa casos ambiguos,
- propone soluciones cuando hay varias opciones.

# 6. Nivel 3: GPU externa con Runpod

Hay un punto intermedio entre “todo en mi PC” y “todo por API de pago”: alquilar GPU cuando necesitas potencia puntual.

[Runpod](https://www.runpod.io) ofrece GPUs bajo demanda. Su documentación separa dos ideas interesantes:

- [Pods](https://docs.runpod.io/pods/overview): máquinas con GPU donde tienes control del entorno, acceso por SSH, JupyterLab o VS Code, y puedes montar tu software.
- [Serverless](https://docs.runpod.io/serverless/overview): endpoints para ejecutar workloads de IA sin gestionar servidores, pagando por tiempo real de cómputo y evitando coste ocioso cuando no hay peticiones.

## 6.1. Cómo usar Runpod Pods paso a paso

Usaría Pods cuando quiero una máquina con GPU para probar, desarrollar o ejecutar un modelo durante unas horas.

1. Crea cuenta en Runpod.
2. Entra en la sección de Pods.
3. Elige una GPU según VRAM necesaria. Para modelos pequeños no hace falta irse a lo más caro.
4. Elige una plantilla, por ejemplo una de PyTorch/Jupyter si vas a experimentar.
5. Configura almacenamiento si necesitas persistir modelos o datasets.
6. Arranca el Pod.
7. Conéctate por JupyterLab, SSH o VS Code.
8. Instala tu runtime o servidor de inferencia.
9. Prueba el modelo con un conjunto pequeño.
10. Para el Pod cuando termines, para no seguir pagando.

## 6.2. Cómo usar Runpod Serverless paso a paso

Usaría Serverless cuando ya tengo una función o contenedor y quiero un endpoint que escale con peticiones.

1. Prepara un contenedor con tu modelo o worker.
2. Define una función handler que reciba entrada y devuelva salida.
3. Sube la imagen a un registry.
4. Crea un endpoint Serverless en Runpod.
5. Selecciona GPU, escalado y límites.
6. Prueba el endpoint con una petición pequeña.
7. Mide latencia, coste y errores.
8. Conecta ese endpoint desde tu router de modelos.

¿Cuándo usar Runpod o un servicio parecido?

- Cuando tu equipo local no tiene VRAM suficiente.
- Cuando necesitas probar modelos grandes durante unas horas.
- Cuando quieres servir un modelo privado sin comprar GPU.
- Cuando tienes picos de trabajo y no quieres pagar máquina encendida todo el día.

¿Cuándo no lo usaría?

- Para tareas pequeñas que Ollama resuelve en local.
- Para flujos con datos sensibles si no has revisado bien privacidad, región y almacenamiento.
- Para cargas muy constantes donde quizá compense infraestructura propia o una API ya optimizada.

# 7. Nivel 4: modelo de pago

El modelo de pago sigue siendo muy valioso. La clave es usarlo donde realmente cambia el resultado:

- razonamiento multi paso,
- decisiones ambiguas,
- redacción final,
- análisis de arquitectura,
- revisión crítica,
- casos con poco margen de error.

No se trata de evitar pagar. Se trata de pagar por inteligencia, no por transportar ruido.

# 8. Automatizar el cambio de modelo

Aquí es donde la cosa se pone interesante. En vez de decidir a mano cada vez, podemos montar un router.

Opciones disponibles:

## 8.1. LiteLLM

[LiteLLM](https://docs.litellm.ai/) ofrece una interfaz compatible con formato OpenAI para llamar a muchos proveedores. Su documentación destaca funciones como proxy, tracking de gasto, presupuestos, logging y lógica de retry/fallback mediante router.

Pasos para usarlo como gateway:

1. Decide qué modelos/proveedores quieres exponer.
2. Crea un archivo de configuración con esos modelos.
3. Arranca LiteLLM Proxy.
4. Cambia tu aplicación para llamar al proxy en vez de llamar directamente a cada proveedor.
5. Activa logging/cost tracking si lo necesitas.
6. Añade reglas de fallback para cuando un modelo falle.

Ejemplo conceptual:

```yaml
model_list:
  - model_name: barato
    litellm_params:
      model: ollama/llama3.2:1b
      api_base: http://localhost:11434
  - model_name: calidad
    litellm_params:
      model: openai/gpt-4o-mini
      api_key: os.environ/OPENAI_API_KEY
```

Encaja si quieres:

- un gateway interno para varios modelos,
- medir gasto por proyecto,
- usar claves virtuales,
- añadir fallback entre proveedores,
- tener una API común para tu aplicación.

## 8.2. OpenRouter

[OpenRouter](https://openrouter.ai/docs/model-routing) permite enrutar peticiones entre modelos. Su documentación habla de `openrouter/auto` para seleccionar modelo automáticamente y del parámetro `models` para probar fallbacks cuando el modelo principal falla, está limitado o no responde.

Pasos para probarlo:

1. Crea una cuenta en OpenRouter.
2. Genera una API key.
3. Usa su endpoint compatible con OpenAI.
4. Prueba primero `openrouter/auto` si quieres selección automática.
5. Prueba después una lista `models` si quieres fallbacks en orden.
6. Registra qué modelo se usó finalmente y cuánto costó.

Ejemplo conceptual:

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="OPENROUTER_API_KEY",
)

respuesta = client.chat.completions.create(
    model="openrouter/auto",
    messages=[{"role": "user", "content": "Resume este ticket"}],
)
```

Encaja si quieres:

- probar muchos modelos con una API común,
- tener fallback sin montar tu propio router,
- comparar modelos externos rápido.

## 8.3. LangChain y middlewares

LangChain tiene middleware de fallback de modelos en su referencia. Puede encajar si ya estás construyendo agentes o workflows con LangChain.

## 8.4. Router propio

Para empezar, muchas veces basta con una función propia:

- si es clasificación simple, local,
- si es texto largo, resumir local,
- si contiene riesgo, pago,
- si local falla, fallback,
- si necesita GPU grande, Runpod.

# 9. Ejemplo de router sencillo

```python
def elegir_modelo(tarea):
    if tarea["riesgo"] == "alto":
        return "pago"
    if tarea["tipo"] in {"clasificacion", "extraccion", "resumen"}:
        return "local"
    if tarea["tokens"] > 50000 and tarea["privacidad"] == "baja":
        return "runpod"
    return "pago"
```

Y una versión un poco más real:

```python
def ejecutar_tarea(tarea):
    modelo = elegir_modelo(tarea)

    if modelo == "local":
        resultado = llamar_ollama(tarea)
        if resultado["confianza"] >= 0.8:
            return resultado
        return llamar_modelo_pago(tarea)

    if modelo == "runpod":
        return llamar_endpoint_runpod(tarea)

    return llamar_modelo_pago(tarea)
```

La automatización no tiene que ser perfecta desde el primer día. Tiene que evitar que todo vaya por defecto al modelo más caro.

# 10. Extras

## 10.1. Cachear respuestas

Si una pregunta se repite mucho, no vuelvas a pagarla. Guarda el resultado y reutilízalo cuando la entrada sea igual o muy parecida.

## 10.2. Etiquetar sensibilidad

No todo debe salir de tu equipo. Marca cada flujo con sensibilidad:

- baja: puede ir a servicios externos,
- media: revisar caso,
- alta: local o proveedor con garantías claras.

## 10.3. Medir por flujo, no por prompt

Un prompt aislado puede parecer barato. Un flujo repetido mil veces al mes puede ser el agujero real.

# 11. Quiero el flujo completo

La receta sería:

1. Inventario de prompts.
2. Clasificación por riesgo.
3. Reglas antes de IA.
4. IA local para tareas mecánicas.
5. Runpod o GPU externa para potencia puntual.
6. Modelo de pago para calidad y razonamiento.
7. Router automático con LiteLLM, OpenRouter, LangChain o una función propia.
8. Medición mensual del ahorro.

Y a partir de ahí, iterar. Como en cualquier automatización buena, el primer objetivo no es hacerlo perfecto: es dejar de hacerlo a ciegas.

<!-- en -->

# INDEX

1. Introduction
2. Requirements
3. What we are building
4. Level 1: rules and scripts
5. Level 2: local AI
6. Level 3: external GPU with Runpod
7. Level 4: paid model
8. Automating model switching
9. Simple router example
10. Extras
11. Full workflow

# 1. Introduction

The mistake is not using paid models. The mistake is sending every small task to the most expensive model by default.

This lab builds a routing strategy: rules first, local AI second, external GPU when useful, paid AI for quality and reasoning.

# 2. Requirements

We need a prompt inventory, approximate monthly volume, paid model pricing, a local AI option and a clear idea of which tasks are critical.

# 3. What we are building

We classify tasks by risk and repetition, use rules when possible, move mechanical work local, use external GPU when local is not enough and automate model choice.

![Prompt inventory and monthly token spend by workflow](capture-token-inventory-en.svg)

# 4. Level 1: rules and scripts

Many tasks do not need AI: deduplication, JSON validation, keyword routing, regex extraction and log slicing.

```python
def detect_ticket_type(text):
    text = text.lower()
    if "vpn" in text:
        return "vpn"
    if "outlook" in text or "email" in text:
        return "email"
    return "review"
```

# 5. Level 2: local AI

Local AI fits classification, summarization, JSON extraction, context preparation and escalation detection.

![Pipeline for splitting work between local AI and paid AI](capture-local-routing-en.svg)

# 6. Level 3: external GPU with Runpod

[Runpod](https://www.runpod.io) offers on-demand GPUs. Its docs separate [Pods](https://docs.runpod.io/pods/overview), where you control a GPU environment, from [Serverless](https://docs.runpod.io/serverless/overview), where endpoints run workloads without managing servers and avoid idle compute costs.

Use it when local hardware is not enough or when you need temporary GPU power.

# 7. Level 4: paid model

Use paid models for complex reasoning, ambiguous decisions, final writing, architecture and critical review.

# 8. Automating model switching

Options:

- [LiteLLM](https://docs.litellm.ai/) for a gateway, spend tracking and retry/fallback logic.
- [OpenRouter](https://openrouter.ai/docs/model-routing) for model routing, `openrouter/auto` and fallback arrays.
- LangChain middleware if you are already building agents.
- Your own simple router.

# 9. Simple router example

```python
def choose_model(task):
    if task["risk"] == "high":
        return "paid"
    if task["type"] in {"classification", "extraction", "summary"}:
        return "local"
    if task["tokens"] > 50000 and task["privacy"] == "low":
        return "runpod"
    return "paid"
```

# 10. Extras

Cache repeated answers, tag sensitivity and measure cost by workflow instead of by isolated prompt.

# 11. Full workflow

Inventory prompts, classify risk, use rules, route mechanical work local, use external GPU when needed, pay for quality, automate routing and measure monthly.
