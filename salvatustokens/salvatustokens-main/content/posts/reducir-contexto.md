---
title_es: "Reducir contexto"
subtitle_es: "antes de llamar a un modelo caro"
description_es: "Lab práctico con varias soluciones para reducir tokens de entrada: limpieza, resúmenes operativos, Caveman, plantillas y medición."
title_en: "Reducing context"
subtitle_en: "before calling an expensive model"
description_en: "A practical lab with several ways to reduce input tokens: cleanup, operational summaries, Caveman, templates and measurement."
slug: reducir-contexto
author: salvatustokens
tags_es: prompts, contexto, tokens, Caveman
tags_en: prompts, context, tokens, Caveman
reading_time: 11 min
date: 2026-05-01
published: false
---

<!-- es -->

# ÍNDICE

1. Introducción
2. Prerrequisitos
3. ¿Qué problema vamos a resolver?
4. Solución 1: limpiar ruido antes del prompt
5. Solución 2: resumen operativo
6. Solución 3: comprimir memoria con Caveman
7. Solución 4: plantillas por tipo de tarea
8. Solución 5: medir y decidir
9. Extras
10. Quiero el flujo completo

# 1. Introducción

Muchas veces pensamos que ahorrar tokens consiste en escribir prompts más cortos. Y sí, ayuda. Pero el ahorro grande suele estar antes: en no enviar basura al modelo.

Logs completos, historiales duplicados, emails con firmas infinitas, documentos con secciones que no importan... Todo eso entra en la factura. En este lab vamos a preparar una entrada más pequeña y más útil antes de llamar a un modelo de pago.

La idea no es recortar por recortar. La idea es que el modelo caro reciba solamente lo que necesita para razonar bien.

# 2. Prerrequisitos

Para este lab necesitaremos:

- Un texto largo o repetitivo que usemos habitualmente con IA.
- Un criterio claro de qué queremos obtener.
- Un paso de limpieza local, que puede ser un script, reglas o IA local.
- Un modelo de pago para la respuesta final.
- Una forma de medir tokens antes y después.

# 3. ¿Qué problema vamos a resolver?

En resumen, estas son las tareas que vamos a realizar:

- Separar información útil de ruido.
- Crear un resumen operativo.
- Comprimir memoria de proyecto cuando se carga siempre.
- Enviar al modelo caro solo el contexto que decide.
- Medir tokens antes y después.

La idea visual sería esta:

![Reducción de contexto antes y después](capture-context-reduction.svg)

# 4. Solución 1: limpiar ruido antes del prompt

El ruido suele aparecer en sitios muy concretos:

- cabeceras repetidas,
- firmas,
- trazas sin error,
- mensajes duplicados,
- histórico antiguo,
- campos que no usaremos para decidir.

Antes de llamar al modelo, conviene hacer una limpieza mínima. No hace falta IA para todo. Muchas veces basta con reglas.

```python
def limpiar_lineas(texto):
    lineas = []
    vistas = set()

    for linea in texto.splitlines():
        normalizada = linea.strip()
        if not normalizada:
            continue
        if "DEBUG" in normalizada:
            continue
        if "firma corporativa" in normalizada.lower():
            continue
        if normalizada in vistas:
            continue

        vistas.add(normalizada)
        lineas.append(linea)

    return "\n".join(lineas)
```

¿Cuándo usar esta solución?

- Cuando hay texto repetido.
- Cuando el formato es bastante estable.
- Cuando el error de limpieza no es crítico.
- Cuando quieres una mejora rápida sin montar una arquitectura.

# 5. Solución 2: resumen operativo

Un formato que funciona bastante bien es:

```text
Objetivo:
Datos relevantes:
Restricciones:
Cambios recientes:
Pregunta concreta:
```

Esto obliga a comprimir. Y cuando comprimimos bien, el modelo de pago razona sobre material más limpio.

Ejemplo:

```text
Objetivo: detectar por qué falla el despliegue.
Datos relevantes: error 504 al pasar por proxy, aplicación responde localmente.
Restricciones: no se puede reiniciar base de datos en horario laboral.
Cambios recientes: actualización de reglas del balanceador.
Pregunta concreta: ¿qué tres comprobaciones harías primero?
```

¿Cuándo usar esta solución?

- Cuando hay documentos largos.
- Cuando el texto original viene de reuniones, tickets o logs.
- Cuando quieres conservar intención, datos y restricciones.
- Cuando el modelo de pago debe razonar, no limpiar.

# 6. Solución 3: comprimir memoria con Caveman

Aquí entra una idea interesante: no todo el contexto viene del prompt que escribimos hoy. A veces el coste se va en archivos que se cargan siempre, como memorias de proyecto, preferencias, instrucciones o documentación resumida.

[Caveman](https://github.com/JuliusBrussee/caveman) tiene una parte llamada `caveman-compress` enfocada justo a esto: comprimir archivos de memoria como `CLAUDE.md`, todos o preferencias para que cada sesión cargue menos tokens. Según su README, mantiene copia humana en `.original.md`, comprime el archivo que leerá el asistente y preserva elementos críticos como bloques de código, URLs, rutas, comandos, términos técnicos, encabezados, tablas, fechas y valores numéricos.

## 6.1. Cómo usar Caveman paso a paso

El flujo que yo seguiría sería este:

1. Localiza el archivo que se carga siempre en tus sesiones, por ejemplo `CLAUDE.md`, `PROJECT.md`, `MEMORY.md` o una nota de preferencias.
2. Haz una copia manual si es un archivo importante. Caveman también trabaja con copia `.original.md`, pero al principio prefiero tener backup adicional.
3. Revisa que el archivo no mezcle secretos, claves o datos sensibles. No queremos comprimir y conservar basura peligrosa.
4. Ejecuta la compresión sobre el archivo:

```text
/caveman:compress CLAUDE.md
```

5. Comprueba que se ha creado una versión original legible, normalmente algo como:

```text
CLAUDE.md           -> versión comprimida que carga la IA
CLAUDE.original.md  -> copia legible para editar
```

6. Abre `CLAUDE.md` y revisa que las instrucciones críticas siguen estando.
7. Abre `CLAUDE.original.md` y úsalo como fuente humana de edición.
8. Cuando edites la versión original, vuelve a comprimir.
9. Mide tamaño o tokens aproximados antes y después.

¿Dónde encaja Caveman?

- Proyectos donde `CLAUDE.md` o notas similares se cargan en cada sesión.
- Equipos que han ido acumulando instrucciones largas.
- Repos donde hay preferencias, decisiones y recordatorios que conviene conservar.
- Casos donde el ahorro se repite muchas veces, no solo una.

Ventaja: el ahorro es recurrente. Si reduces una memoria que se carga en cada sesión, cada apertura del proyecto empieza más barata.

Riesgo: hay que revisar la versión comprimida. Cualquier compresor puede perder matices si el texto original mezcla instrucciones, ejemplos y excepciones.

## 6.2. Cuándo no usar Caveman

No lo usaría para:

- código fuente,
- configuraciones delicadas,
- JSON/YAML que deba conservar formato exacto,
- documentación legal,
- instrucciones donde cada palabra sea importante.

Para esos casos, mejor usar resúmenes manuales o plantillas controladas.

# 7. Solución 4: plantillas por tipo de tarea

No uses la misma plantilla para tickets, reuniones y código. Cada flujo tiene sus campos importantes.

Plantilla para tickets:

```text
Tipo de incidencia:
Síntoma:
Impacto:
Cambios recientes:
Evidencia:
Pregunta:
```

Plantilla para reuniones:

```text
Decisiones:
Tareas:
Bloqueos:
Fechas:
Personas responsables:
```

Plantilla para revisión de código:

```text
Objetivo del cambio:
Archivos tocados:
Riesgos:
Errores observados:
Qué quiero revisar:
```

¿Por qué ayuda? Porque una plantilla estable evita reenviar instrucciones largas cada vez. Además, fuerza a separar datos variables de instrucciones fijas.

# 8. Solución 5: medir y decidir

Podemos medir de forma sencilla:

```python
tokens_originales = 9800
tokens_resumen = 5100
reduccion = 1 - tokens_resumen / tokens_originales
print(f"Reducción: {reduccion:.1%}")
```

Pero no basta con medir tokens. Yo apuntaría cuatro columnas:

- tokens antes,
- tokens después,
- calidad de respuesta,
- tiempo humano de revisión.

Si reduces casi a la mitad y la respuesta final no pierde calidad, acabas de encontrar ahorro recurrente. Si ahorras tokens pero luego tienes que revisar el doble, no has ahorrado: has movido el coste a tu tiempo.

# 9. Extras

## 9.1. Cuidado con resumir demasiado

Reducir contexto no significa borrar información importante. Si el modelo necesita fechas, cantidades o condiciones, tienen que sobrevivir al resumen.

## 9.2. Usa IA local como filtro

Un modelo local pequeño puede preparar el resumen operativo. No tiene que resolver el problema final. Solo tiene que dejar el material limpio.

## 9.3. Guarda el contexto limpio

Si el mismo documento se usa varias veces, guarda la versión reducida. No vuelvas a pagar por limpiar lo mismo.

# 10. Quiero el flujo completo

La receta sería:

1. Recibir texto original.
2. Eliminar ruido con reglas.
3. Generar resumen operativo con IA local o plantilla.
4. Comprimir memorias recurrentes con herramientas tipo Caveman cuando aplique.
5. Enviar al modelo de pago solo lo importante.
6. Medir tokens, calidad y tiempo de revisión.

No es magia, pero funciona: menos ruido, menos coste y normalmente mejores respuestas.

<!-- en -->

# INDEX

1. Introduction
2. Requirements
3. The problem
4. Solution 1: clean noise before prompting
5. Solution 2: operational summary
6. Solution 3: compress memory with Caveman
7. Solution 4: task-specific templates
8. Solution 5: measure and decide
9. Extras
10. Full workflow

# 1. Introduction

Saving tokens is not only about shorter prompts. The biggest saving often happens before the prompt: not sending junk to the model.

In this lab we clean repeated text, create operational summaries, compress repeated project memory and only send the expensive model what it really needs.

# 2. Requirements

We need a long text, a clear target, a local cleanup step, a paid model for the final answer and a way to measure tokens before and after.

# 3. The problem

We will separate useful information from noise, create a smaller input, compress repeated memory when relevant and measure the result.

![Context reduction before and after](capture-context-reduction-en.svg)

# 4. Solution 1: clean noise before prompting

Rules are often enough for repeated headers, signatures, duplicated lines or useless debug traces.

```python
def clean_lines(text):
    lines = []
    seen = set()
    for line in text.splitlines():
        normalized = line.strip()
        if not normalized or "DEBUG" in normalized:
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        lines.append(line)
    return "\n".join(lines)
```

# 5. Solution 2: operational summary

Use a small, stable structure:

```text
Goal:
Relevant data:
Constraints:
Recent changes:
Concrete question:
```

This keeps reasoning material and removes filler.

# 6. Solution 3: compress memory with Caveman

[Caveman](https://github.com/JuliusBrussee/caveman) includes `caveman-compress`, a tool for compressing memory files such as `CLAUDE.md`, todos or preferences so every session loads fewer tokens. Its README explains that it keeps a human-readable `.original.md` backup and preserves code blocks, URLs, paths, commands, technical terms, headings, tables, dates and numeric values.

This is useful when the same project memory is loaded repeatedly.

# 7. Solution 4: task-specific templates

Use different templates for tickets, meetings and code review. Each workflow has different fields that matter.

# 8. Solution 5: measure and decide

Track tokens before, tokens after, answer quality and human review time. Saving tokens is only useful if the review cost does not explode.

# 9. Extras

Use local AI as a filter, keep cleaned context, and avoid summarizing away dates, numbers or constraints.

# 10. Full workflow

Clean, summarize, compress recurring memory, call the paid model only with relevant context, and measure.
