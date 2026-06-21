# salvatustokens

Web estática para `salvatustokens.salvatutiempo.com`, centrada en ahorrar tokens y dinero usando IA local e IA de pago con criterio.

El sitio está pensado para GitHub + Cloudflare Pages: no necesita Flask en producción, no tiene dependencias externas y genera todo el HTML en la carpeta `dist`.

Incluye una calculadora completa en `/calculadora/` para estimar tokens, comparar costes, simular ahorro mensual y calcular RAM/VRAM aproximada para IA local.

## Requisitos

- Python 3.13.3, fijado en `.python-version`.
- Git.
- Opcional: Wrangler, solo si quieres desplegar manualmente desde terminal.

## Previsualizar en local

```powershell
python _preview_server.py
```

Abre `http://127.0.0.1:5051/`.

## Crear un artículo

```powershell
python tools/new_post.py "Cómo ahorrar tokens en un flujo de trabajo real"
```

Edita el archivo creado en `content/posts` y cambia `published: false` a `published: true` cuando esté listo.

Los posts son bilingües. Cada archivo tiene metadatos `*_es` y `*_en`, y el cuerpo separado por:

```markdown
<!-- es -->

Contenido en español.

<!-- en -->

English content.
```

## Generar el sitio

```powershell
python build.py
```

La salida queda en `dist`.

## Subir a GitHub

Si partes de esta carpeta como repositorio nuevo:

```powershell
git init
git branch -M main
git remote add origin https://github.com/salvatutiempo/salvatustokens.git
git add .
git commit -m "Publica primera version de salvatustokens"
git push -u origin main
```

El repositorio incluye un workflow en `.github/workflows/build.yml` que ejecuta `python build.py` en cada push y pull request.

## Cloudflare Pages

Configuración sugerida en Cloudflare Pages:

- Framework preset: `None`
- Build command: `python build.py`
- Build output directory: `dist`
- Root directory: raíz del repo
- Production branch: `main`
- Custom domain: `salvatustokens.salvatutiempo.com`

También se incluye `wrangler.toml` con `pages_build_output_dir = "./dist"` para que Cloudflare tenga la salida declarada en el código.

Más detalle en `CLOUDFLARE_PAGES.md`.
