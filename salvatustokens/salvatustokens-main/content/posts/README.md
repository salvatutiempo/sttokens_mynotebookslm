# Posts

Cada articulo es un archivo Markdown con frontmatter.

Campos recomendados:

```yaml
---
title_es: "Titulo"
subtitle_es: "Resumen corto visible en tarjetas"
description_es: "Descripcion SEO"
title_en: "Title"
subtitle_en: "Short summary visible in cards"
description_en: "SEO description"
slug: titulo
date: 2026-05-01
author: salvatustokens
tags_es: IA local, tokens, ahorro
tags_en: Local AI, tokens, savings
reading_time: 5 min
published: true
---
```

Usa `published: false` para borradores.

Separa los idiomas con marcadores:

```markdown
<!-- es -->

# Titulo

Contenido en espanol.

<!-- en -->

# Title

English content.
```
