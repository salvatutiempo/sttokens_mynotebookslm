import sys
import unicodedata
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "content" / "posts"


def slugify(text):
    text = unicodedata.normalize("NFKD", text.lower().strip())
    text = text.encode("ascii", "ignore").decode("ascii")
    slug = []
    previous_dash = False
    for char in text:
        if char.isalnum():
            slug.append(char)
            previous_dash = False
        elif not previous_dash:
            slug.append("-")
            previous_dash = True
    return "".join(slug).strip("-") or "nuevo-articulo"


def main():
    if len(sys.argv) < 2:
        print('Uso: python tools/new_post.py "Titulo del articulo"')
        raise SystemExit(1)

    title = " ".join(sys.argv[1:])
    slug = slugify(title)
    path = POSTS_DIR / f"{slug}.md"
    if path.exists():
        print(f"Ya existe: {path}")
        raise SystemExit(1)

    path.write_text(
        f"""---
title_es: "{title}"
subtitle_es: "Resumen breve del articulo."
description_es: "Descripcion SEO del articulo."
title_en: "{title}"
subtitle_en: "Short article summary."
description_en: "SEO description."
slug: {slug}
date: {date.today().isoformat()}
author: salvatustokens
tags_es: IA local, tokens, ahorro
tags_en: Local AI, tokens, savings
reading_time: 5 min
published: false
---

<!-- es -->

# {title}

Escribe aqui la introduccion.

## El problema

Describe el coste, el contexto o el flujo.

## La solucion

- Paso uno.
- Paso dos.
- Paso tres.

## Como medirlo

Explica que comparar antes y despues.

<!-- en -->

# {title}

Write the introduction here.

## The problem

Describe the cost, context or workflow.

## The solution

- Step one.
- Step two.
- Step three.

## How to measure it

Explain what to compare before and after.
""",
        encoding="utf-8",
    )
    print(f"Creado: {path}")


if __name__ == "__main__":
    main()
