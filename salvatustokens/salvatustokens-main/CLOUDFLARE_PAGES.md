# Cloudflare Pages

Configuración recomendada para conectar este repositorio desde GitHub:

- Framework preset: `None`
- Build command: `python build.py`
- Build output directory: `dist`
- Root directory: raíz del repo
- Production branch: `main`
- Build system: v3

Dominio de producción:

```text
salvatustokens.salvatutiempo.com
```

El build genera:

- `index.html`
- `/articulos/`
- `/calculadora/`
- `/guia/`
- `/en/`
- `/en/calculator/`
- `/articulos/<slug>/`
- `rss.xml`
- `robots.txt`
- `sitemap.txt`
- `_headers`
- `_redirects`

No hace falta servidor Flask en producción. Cloudflare Pages solo publica la carpeta `dist`.

## Variables y versiones

Cloudflare Pages soporta Python en su build image. Este proyecto fija la versión con `.python-version`:

```text
3.13.3
```

No hay dependencias externas, pero se mantiene `requirements.txt` para que GitHub Actions y Cloudflare tengan un punto estándar de instalación.

## Wrangler

El archivo `wrangler.toml` declara:

```toml
name = "salvatustokens"
pages_build_output_dir = "./dist"
compatibility_date = "2026-05-01"
```

Esto no sustituye la configuración del panel de Cloudflare Pages, pero ayuda a documentar el proyecto y permite despliegues manuales con Wrangler si los necesitas.

## Headers

El generador crea `dist/_headers` con reglas básicas de seguridad y caché. Cloudflare Pages aplica ese archivo automáticamente al publicar la carpeta `dist`.
