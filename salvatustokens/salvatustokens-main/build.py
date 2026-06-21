import html
import re
import shutil
import sys
import unicodedata
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from string import Template
from urllib.parse import quote

from site_config import SITE


ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
POSTS_DIR = ROOT / "content" / "posts"
STATIC_DIR = ROOT / "static"
TEMPLATES_DIR = ROOT / "templates"

LANG = {
    "es": {
        "prefix": "",
        "articles_path": "/articulos/",
        "calculator_path": "/calculadora/",
        "guide_path": "/guia/",
        "home_label": "Inicio",
        "method_label": "Método",
        "calculator_label": "Calculadora",
        "articles_label": "Artículos",
        "guide_label": "Guía rápida",
        "switch_label": "EN",
        "switch_title": "Read in English",
        "footer_articles": "Artículos",
        "footer_guide": "Guía rápida",
        "contact": "Contacto",
    },
    "en": {
        "prefix": "/en",
        "articles_path": "/en/articles/",
        "calculator_path": "/en/calculator/",
        "guide_path": "/en/guide/",
        "home_label": "Home",
        "method_label": "Method",
        "calculator_label": "Calculator",
        "articles_label": "Articles",
        "guide_label": "Quick guide",
        "switch_label": "ES",
        "switch_title": "Leer en español",
        "footer_articles": "Articles",
        "footer_guide": "Quick guide",
        "contact": "Contact",
    },
}

COPY = {
    "es": {
        "site_tagline": "Ahorra tokens, dinero y contexto sin renunciar a una buena IA.",
        "home_title": f"{SITE['name']} - Ahorra tokens, dinero y contexto sin renunciar a una buena IA.",
        "home_description": SITE["description"],
        "eyebrow": "IA local + IA de pago, cada una donde aporta",
        "hero_lead": "Aprende a reducir gasto en tokens, elegir modelos con criterio y montar flujos de IA que no quemen dinero en tareas que tu máquina puede resolver.",
        "primary_cta": "Empezar con la guía",
        "secondary_cta": "Leer artículos",
        "visual_label": "Esquema de reparto de tareas entre IA local e IA de pago",
        "local": "Local",
        "local_desc": "clasificar, resumir, limpiar",
        "paid": "Pago",
        "paid_desc": "razonar, decidir, producir",
        "saving_estimate": "Ahorro estimado",
        "strip_1": "Menos contexto basura",
        "strip_2": "Más prompts reutilizables",
        "strip_3": "Modelos locales primero",
        "strip_4": "Pago solo cuando compensa",
        "method_eyebrow": "Método",
        "method_title": "Un filtro simple antes de gastar tokens",
        "method_text": "La web gira alrededor de una pregunta: qué parte del trabajo necesita realmente un modelo caro y qué parte puede prepararse antes.",
        "reduce": "Reduce",
        "reduce_text": "Limpia entradas, elimina duplicados, resume ruido y conserva solo los datos que cambian la decisión.",
        "split": "Reparte",
        "split_text": "Usa IA local para tareas masivas y repetibles, y reserva la IA de pago para razonamiento, calidad y casos límite.",
        "measure": "Mide",
        "measure_text": "Calcula coste por flujo, no por prompt aislado. Si no se mide, el ahorro se convierte en intuición.",
        "calc_eyebrow": "Calculadora",
        "calc_title": "Estima cuánto puedes ahorrar",
        "calc_text": "Introduce un flujo habitual y prueba qué porcentaje podrías mover a IA local, reglas o preprocesado antes de llamar a un modelo de pago.",
        "calc_full_button": "Abrir calculadora completa",
        "input_tokens": "Tokens de entrada al mes",
        "output_tokens": "Tokens de salida al mes",
        "input_price": "Precio entrada por 1M",
        "output_price": "Precio salida por 1M",
        "local_share": "Trabajo movido a local o reglas",
        "monthly_saving": "Ahorro mensual aproximado",
        "routes_eyebrow": "Rutas de aprendizaje",
        "routes_title": "De gastar por inercia a gastar con intención",
        "route_1": "Inventario de prompts",
        "route_1_text": "Detecta donde se van los tokens cada semana.",
        "route_2": "IA local útil",
        "route_2_text": "Tareas que puedes mover sin complicarte la vida.",
        "route_3": "IA de pago con criterio",
        "route_3_text": "Cuando merece la pena pagar por calidad.",
        "route_4": "Plantillas y procesos",
        "route_4_text": "Convierte ahorros puntuales en sistema.",
        "blog_eyebrow": "Blog",
        "latest": "Últimos artículos",
        "view_all": "Ver todos",
        "articles_title": "Artículos - salvatustokens",
        "articles_h1": "Guías para ahorrar tokens con IA real",
        "articles_intro": "Casos prácticos, flujos, comparativas y decisiones para combinar IA local e IA de pago sin perder calidad.",
        "calculator_title": "Calculadora de tokens y ahorro - salvatustokens",
        "calculator_h1": "Calculadora de tokens, coste y ahorro",
        "calculator_intro": "Pega un texto real, calcula una estimación de tokens, compara modelos y simula cuánto puedes ahorrar con caché, reglas, IA local o preprocesado.",
        "calculator_notice": "Los precios son editables y sirven para estimar. Antes de presupuestar producción, verifica siempre la tarifa oficial del proveedor.",
        "calculator_note_label": "Nota",
        "calc_tab_text": "Texto",
        "calc_tab_flow": "Flujo mensual",
        "calc_tab_local": "IA local",
        "calc_text_label": "Texto, prompt, JSON, código o contexto",
        "calc_text_default": "Pega aquí un prompt real, una conversación, un fragmento de documentación o una respuesta que quieras enviar a un modelo de pago.",
        "calc_sample_prompt": "Prompt de ejemplo",
        "calc_sample_json": "JSON",
        "calc_clear": "Limpiar",
        "metric_tokens": "Tokens estimados",
        "metric_words": "Palabras",
        "metric_chars": "Caracteres",
        "metric_type": "Tipo detectado",
        "expected_output": "Salida esperada por petición",
        "requests_month": "Peticiones al mes",
        "cacheable_input": "Entrada cacheable",
        "table_model": "Modelo",
        "table_provider": "Proveedor",
        "table_context": "Contexto",
        "table_input": "Entrada / 1M",
        "table_output": "Salida / 1M",
        "table_monthly": "Coste mensual",
        "flow_input": "Tokens de entrada al mes",
        "flow_output": "Tokens de salida al mes",
        "flow_input_price": "Precio entrada / 1M",
        "flow_output_price": "Precio salida / 1M",
        "flow_reduction": "Reducido por limpieza previa",
        "flow_local": "Movido a IA local o reglas",
        "flow_before": "Antes",
        "flow_after": "Después",
        "flow_saving": "Ahorro mensual",
        "local_model_size": "Tamaño del modelo",
        "local_model_size_help": "En miles de millones de parámetros. Ejemplo: 3, 7, 14, 32.",
        "quantization": "Cuantización",
        "local_output_tokens": "Tokens de salida",
        "local_speed": "Velocidad estimada",
        "local_speed_help": "Tokens por segundo.",
        "local_ram": "RAM/VRAM aproximada",
        "local_ram_buffer": "Con margen operativo",
        "local_generation_time": "Tiempo de generación",
        "price_reference": "Precios de referencia en USD por millón de tokens, editables: ajústalos a tu caso y verifica siempre la tarifa oficial del proveedor.",
        "price_updated_label": "Actualización automática de precios:",
        "currency_label": "Coste mensual en:",
        "local_hw_title": "¿En qué hardware corre?",
        "local_hw_help": "Según el tamaño del modelo y la cuantización, esto es lo que necesita y dónde encaja. Verde = cabe holgado en memoria; gris = se queda corta.",
        "guide_title": "Guía rápida - salvatustokens",
        "guide_h1": "El mapa base para gastar menos en IA",
        "guide_intro": "Una forma simple de decidir antes de enviar contexto a un modelo de pago.",
        "guide_1_title": "Haz inventario de prompts",
        "guide_1_text": "Lista tus flujos repetidos: correos, informes, código, clasificación, análisis de documentos, soporte o investigación. Anota frecuencia, tokens aproximados, modelo usado y resultado esperado.",
        "guide_2_title": "Mueve lo mecánico a local",
        "guide_2_text": "La IA local suele encajar en clasificar, extraer campos, resumir borradores, limpiar texto, generar variantes y preparar contexto. Si la tarea tolera algún ajuste manual, probablemente no necesita el modelo más caro.",
        "guide_3_title": "Reserva pago para calidad",
        "guide_3_text": "Usa IA de pago donde el error cuesta: razonamiento complejo, decisiones ambiguas, redacción final, arquitectura, estrategia, revisión crítica o tareas con poco margen de corrección.",
        "guide_4_title": "Plantillas, cache y memoria corta",
        "guide_4_text": "Guarda prompts probados, cachea resultados repetidos y evita reenviar documentos enteros. La pregunta no es solo qué modelo usar, sino cuánto contexto necesita de verdad.",
        "article_cta_title": "Convierte esto en un sistema",
        "article_cta_text": "El ahorro aparece cuando cada flujo tiene una regla clara: qué va a local, qué se resume, qué se cachea y qué se paga.",
        "article_cta_button": "Ver la guía rápida",
    },
    "en": {
        "site_tagline": "Save tokens, money and context without giving up strong AI.",
        "home_title": f"{SITE['name']} - Save tokens, money and context without giving up strong AI.",
        "home_description": "Practical guides for splitting work between local AI and paid AI, reducing token spend and building sustainable AI workflows.",
        "eyebrow": "Local AI + paid AI, each where it shines",
        "hero_lead": "Learn how to reduce token spend, choose models with intent and build AI workflows that do not burn money on work your own machine can handle.",
        "primary_cta": "Start with the guide",
        "secondary_cta": "Read articles",
        "visual_label": "Task routing between local AI and paid AI",
        "local": "Local",
        "local_desc": "classify, summarize, clean",
        "paid": "Paid",
        "paid_desc": "reason, decide, produce",
        "saving_estimate": "Estimated saving",
        "strip_1": "Less noisy context",
        "strip_2": "Reusable prompts",
        "strip_3": "Local models first",
        "strip_4": "Paid only when it pays off",
        "method_eyebrow": "Method",
        "method_title": "A simple filter before spending tokens",
        "method_text": "The site revolves around one question: which part of the job truly needs an expensive model, and which part can be prepared first.",
        "reduce": "Reduce",
        "reduce_text": "Clean inputs, remove duplicates, summarize noise and keep only the data that changes the decision.",
        "split": "Route",
        "split_text": "Use local AI for high-volume repeatable work, and reserve paid AI for reasoning, quality and edge cases.",
        "measure": "Measure",
        "measure_text": "Calculate cost per workflow, not per isolated prompt. If you do not measure it, saving becomes guesswork.",
        "calc_eyebrow": "Calculator",
        "calc_title": "Estimate how much you can save",
        "calc_text": "Enter a common workflow and test how much you could move to local AI, rules or preprocessing before calling a paid model.",
        "calc_full_button": "Open full calculator",
        "input_tokens": "Input tokens per month",
        "output_tokens": "Output tokens per month",
        "input_price": "Input price per 1M",
        "output_price": "Output price per 1M",
        "local_share": "Work moved to local or rules",
        "monthly_saving": "Approximate monthly saving",
        "routes_eyebrow": "Learning paths",
        "routes_title": "From spending by habit to spending with intent",
        "route_1": "Prompt inventory",
        "route_1_text": "Find where your tokens go every week.",
        "route_2": "Useful local AI",
        "route_2_text": "Tasks you can move without overcomplicating things.",
        "route_3": "Paid AI with criteria",
        "route_3_text": "When paying for quality is actually worth it.",
        "route_4": "Templates and processes",
        "route_4_text": "Turn one-off savings into a system.",
        "blog_eyebrow": "Blog",
        "latest": "Latest articles",
        "view_all": "View all",
        "articles_title": "Articles - salvatustokens",
        "articles_h1": "Guides for saving tokens with real AI workflows",
        "articles_intro": "Practical cases, workflows, comparisons and decisions for combining local AI and paid AI without losing quality.",
        "calculator_title": "Token and saving calculator - salvatustokens",
        "calculator_h1": "Token, cost and saving calculator",
        "calculator_intro": "Paste real text, estimate tokens, compare models and simulate how much you can save with cache, rules, local AI or preprocessing.",
        "calculator_notice": "Prices are editable estimates. Before budgeting production, always verify the provider's official pricing.",
        "calculator_note_label": "Note",
        "calc_tab_text": "Text",
        "calc_tab_flow": "Monthly flow",
        "calc_tab_local": "Local AI",
        "calc_text_label": "Text, prompt, JSON, code or context",
        "calc_text_default": "Paste a real prompt, a conversation, a documentation excerpt or a response you plan to send to a paid model.",
        "calc_sample_prompt": "Sample prompt",
        "calc_sample_json": "JSON",
        "calc_clear": "Clear",
        "metric_tokens": "Estimated tokens",
        "metric_words": "Words",
        "metric_chars": "Characters",
        "metric_type": "Detected type",
        "expected_output": "Expected output per request",
        "requests_month": "Requests per month",
        "cacheable_input": "Cacheable input",
        "table_model": "Model",
        "table_provider": "Provider",
        "table_context": "Context",
        "table_input": "Input / 1M",
        "table_output": "Output / 1M",
        "table_monthly": "Monthly cost",
        "flow_input": "Input tokens per month",
        "flow_output": "Output tokens per month",
        "flow_input_price": "Input price / 1M",
        "flow_output_price": "Output price / 1M",
        "flow_reduction": "Reduced by cleanup",
        "flow_local": "Moved to local AI or rules",
        "flow_before": "Before",
        "flow_after": "After",
        "flow_saving": "Monthly saving",
        "local_model_size": "Model size",
        "local_model_size_help": "In billions of parameters. Example: 3, 7, 14, 32.",
        "quantization": "Quantization",
        "local_output_tokens": "Output tokens",
        "local_speed": "Estimated speed",
        "local_speed_help": "Tokens per second.",
        "local_ram": "Approximate RAM/VRAM",
        "local_ram_buffer": "With operating margin",
        "local_generation_time": "Generation time",
        "price_reference": "Reference prices in USD per million tokens, editable: adjust them to your case and always verify the provider's official rate.",
        "price_updated_label": "Automatic price update:",
        "currency_label": "Monthly cost in:",
        "local_hw_title": "What hardware runs it?",
        "local_hw_help": "Based on model size and quantization, this is what it needs and where it fits. Green = fits comfortably in memory; grey = too small.",
        "guide_title": "Quick guide - salvatustokens",
        "guide_h1": "The base map for spending less on AI",
        "guide_intro": "A simple way to decide before sending context to a paid model.",
        "guide_1_title": "Inventory your prompts",
        "guide_1_text": "List repeated workflows: email, reports, code, classification, document analysis, support or research. Track frequency, approximate tokens, model used and expected result.",
        "guide_2_title": "Move mechanical work local",
        "guide_2_text": "Local AI usually fits classification, field extraction, draft summaries, text cleaning, variants and context preparation. If a task tolerates manual adjustment, it probably does not need the most expensive model.",
        "guide_3_title": "Reserve paid AI for quality",
        "guide_3_text": "Use paid AI where mistakes matter: complex reasoning, ambiguous decisions, final writing, architecture, strategy, critical review or tasks with little room for correction.",
        "guide_4_title": "Templates, cache and short memory",
        "guide_4_text": "Save proven prompts, cache repeated results and avoid resending entire documents. The question is not only which model to use, but how much context it truly needs.",
        "article_cta_title": "Turn this into a system",
        "article_cta_text": "Savings appear when each workflow has a clear rule: what goes local, what gets summarized, what gets cached and what gets paid.",
        "article_cta_button": "Open the quick guide",
    },
}


def language_url(lang, page, slug=None):
    info = LANG[lang]
    if page == "home":
        return info["prefix"] + "/" if info["prefix"] else "/"
    if page == "articles":
        return info["articles_path"]
    if page == "calculator":
        return info["calculator_path"]
    if page == "guide":
        return info["guide_path"]
    if page == "post":
        return f"{info['articles_path']}{slug}/"
    return info["prefix"] + "/"


def read_template(name):
    return Template((TEMPLATES_DIR / name).read_text(encoding="utf-8"))


def render(name, lang="es", page="home", slug=None, **context):
    page_context = dict(COPY[lang])
    page_context.update(LANG[lang])
    page_context.update(context)
    page_context.setdefault("site_name", SITE["name"])
    page_context.setdefault("site_url", SITE["url"])
    page_context.setdefault("site_description", page_context.get("home_description", SITE["description"]))
    page_context.setdefault("year", datetime.now().year)
    page_context.setdefault("canonical", SITE["url"] + language_url(lang, page, slug))
    page_context["nav"] = ""
    page_context["footer"] = ""
    content = read_template(name).safe_substitute(**page_context)
    base_context = dict(page_context)
    base_context.update(
        nav=nav_html(lang, page, slug),
        footer=footer_html(lang),
        content=content,
        html_lang=lang,
    )
    return read_template("base.html").safe_substitute(**base_context)


def nav_html(lang, page, slug=None):
    info = LANG[lang]
    other = "en" if lang == "es" else "es"
    switch = LANG[other]
    switch_url = language_url(other, page, slug)
    home = language_url(lang, "home")
    articles = language_url(lang, "articles")
    calculator = language_url(lang, "calculator")
    guide = language_url(lang, "guide")
    return f"""
<header class="site-nav" data-nav>
  <a class="brand" href="{home}">
    <img src="/static/assets/salvatustokens-logo.svg" alt="salvatustokens">
  </a>
  <button class="nav-toggle" type="button" aria-label="Abrir menu" data-nav-toggle>
    <span></span><span></span><span></span>
  </button>
  <nav class="nav-links" data-nav-links>
    <a href="{home}#metodo">{info["method_label"]}</a>
    <a href="{calculator}">{info["calculator_label"]}</a>
    <a href="{articles}">{info["articles_label"]}</a>
    <a href="{guide}">{info["guide_label"]}</a>
    <a class="language-switch" href="{switch_url}" title="{info["switch_title"]}">{info["switch_label"]}</a>
  </nav>
</header>
"""


def footer_html(lang):
    info = LANG[lang]
    copy = COPY[lang]
    return f"""
<footer class="site-footer">
  <div>
    <img src="/static/assets/salvatustokens-icon.svg" alt="" aria-hidden="true">
    <p><strong>{SITE["name"]}</strong><br>{copy["site_tagline"]}</p>
  </div>
  <div>
    <a href="{info["articles_path"]}">{info["footer_articles"]}</a>
    <a href="{info["calculator_path"]}">{info["calculator_label"]}</a>
    <a href="{info["guide_path"]}">{info["footer_guide"]}</a>
    <a href="mailto:{SITE["email"]}">{info["contact"]}</a>
    <a href="/rss.xml">RSS</a>
  </div>
</footer>
"""


def parse_frontmatter(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :].strip()
    meta = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip().lower()] = value.strip().strip('"').strip("'")
    return meta, body


def split_languages(body):
    matches = list(re.finditer(r"<!--\s*(?:lang:)?(es|en)\s*-->", body, re.I))
    if not matches:
        return {"es": body.strip(), "en": body.strip()}
    sections = {}
    for index, match in enumerate(matches):
        lang = match.group(1).lower()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections[lang] = body[start:end].strip()
    sections.setdefault("es", sections.get("en", ""))
    sections.setdefault("en", sections.get("es", ""))
    return sections


def parse_bool(value, default=False):
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "si", "s"}


def parse_date(value, path):
    if value:
        for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                pass
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)


def slugify(text):
    text = unicodedata.normalize("NFKD", text.lower().strip())
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "post"


def inline_markdown(text):
    text = html.escape(text)

    def image_repl(match):
        alt = html.escape(match.group(1), quote=True)
        src = match.group(2).strip()
        if not re.match(r"^(https?:)?//", src) and not src.startswith("/"):
            src = "/static/assets/" + quote(src)
        return f'<figure><img src="{html.escape(src, quote=True)}" alt="{alt}"><figcaption>{alt}</figcaption></figure>'

    def link_repl(match):
        label = match.group(1)
        href = html.escape(match.group(2), quote=True)
        return f'<a href="{href}">{label}</a>'

    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", image_repl, text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_repl, text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return text


INDEX_TITLES = {"ÍNDICE", "INDICE", "INDEX"}


def build_toc_entries(markdown):
    entries = []
    for raw in markdown.splitlines():
        match = re.match(r"^#\s+(.+)$", raw.strip())
        if not match:
            continue
        text = match.group(1).strip()
        if text.upper() in INDEX_TITLES:
            continue
        title_html = inline_markdown(text)
        plain = re.sub(r"<[^>]+>", "", title_html)
        entries.append((slugify(plain), plain))
    return entries


def render_toc(entries, label):
    if not entries:
        return ""
    items = "".join(
        f'<li><a href="#{ident}">{display}</a></li>' for ident, display in entries
    )
    return (
        '<nav class="toc" data-toc>'
        '<button class="toc__toggle" type="button" data-toc-toggle aria-expanded="true">'
        f'<span class="toc__label">{label}</span>'
        '<span class="toc__caret" aria-hidden="true"></span>'
        '</button>'
        f'<ul class="toc__list">{items}</ul>'
        '</nav>'
    )


def markdown_to_html(markdown):
    lines = markdown.splitlines()
    toc_entries = build_toc_entries(markdown)
    parts = []
    paragraph = []
    index = 0
    skip_next_ol = False

    def flush():
        if paragraph:
            parts.append("<p>" + inline_markdown(" ".join(paragraph).strip()) + "</p>")
            paragraph.clear()

    while index < len(lines):
        line = lines[index].rstrip()
        stripped = line.strip()
        if not stripped:
            flush()
            index += 1
            continue
        if stripped.startswith("```"):
            flush()
            lang = stripped[3:].strip()
            code = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code.append(lines[index])
                index += 1
            index += 1
            cls = f' class="language-{html.escape(lang, quote=True)}"' if lang else ""
            parts.append(f"<pre><code{cls}>{html.escape(chr(10).join(code))}</code></pre>")
            continue
        heading = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if heading:
            flush()
            level = len(heading.group(1))
            raw_title = heading.group(2).strip()
            if level == 1 and raw_title.upper() in INDEX_TITLES:
                label = "Index" if raw_title.upper() == "INDEX" else "Índice"
                parts.append(render_toc(toc_entries, label))
                skip_next_ol = True
                index += 1
                continue
            title = inline_markdown(heading.group(2))
            ident = slugify(re.sub(r"<[^>]+>", "", title))
            parts.append(f'<h{level} id="{ident}">{title}</h{level}>')
            index += 1
            continue
        if re.match(r"^[-*]\s+", stripped):
            flush()
            items = []
            while index < len(lines) and re.match(r"^[-*]\s+", lines[index].strip()):
                item = re.sub(r"^[-*]\s+", "", lines[index].strip())
                items.append("<li>" + inline_markdown(item) + "</li>")
                index += 1
            parts.append("<ul>" + "".join(items) + "</ul>")
            continue
        if re.match(r"^\d+\.\s+", stripped):
            flush()
            items = []
            while index < len(lines) and re.match(r"^\d+\.\s+", lines[index].strip()):
                item = re.sub(r"^\d+\.\s+", "", lines[index].strip())
                items.append("<li>" + inline_markdown(item) + "</li>")
                index += 1
            if skip_next_ol:
                skip_next_ol = False
                continue
            parts.append("<ol>" + "".join(items) + "</ol>")
            continue
        if stripped.startswith(">"):
            flush()
            quotes = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                quotes.append(lines[index].strip().lstrip(">").strip())
                index += 1
            parts.append("<blockquote><p>" + inline_markdown(" ".join(quotes)) + "</p></blockquote>")
            continue
        if stripped == "---":
            flush()
            parts.append("<hr>")
            index += 1
            continue
        if re.match(r"^!\[[^\]]*\]\([^)]+\)$", stripped):
            flush()
            parts.append(inline_markdown(stripped))
            index += 1
            continue
        paragraph.append(stripped)
        index += 1

    flush()
    return "\n".join(parts)


def localized(meta, key, lang, default=""):
    return meta.get(f"{key}_{lang}") or meta.get(key) or default


def read_posts(include_drafts=False):
    posts = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        if path.name.startswith("_") or path.name.upper() == "README.MD":
            continue
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        if not meta:
            print(
                f"  AVISO: '{path.name}' no tiene front matter válido (¿faltan las "
                "vallas '---'?). Se ignoran sus metadatos, incluido 'published', y el "
                "artículo se publicará con valores por defecto.",
                file=sys.stderr,
            )
        published = parse_bool(meta.get("published"), default=True)
        if not published and not include_drafts:
            continue
        title = localized(meta, "title", "es", path.stem.replace("-", " ").title())
        slug = meta.get("slug") or slugify(title)
        sections = split_languages(body)
        date = parse_date(meta.get("date"), path)
        post = {
            "slug": slug,
            "date": date,
            "date_display": date.strftime("%d/%m/%Y"),
            "author": meta.get("author", SITE["author"]),
            "reading_time": meta.get("reading_time", "6 min"),
            "published": published,
            "lang": {},
        }
        for lang in ("es", "en"):
            tags = localized(meta, "tags", lang, meta.get("tags", ""))
            post["lang"][lang] = {
                "title": localized(meta, "title", lang, title),
                "subtitle": localized(meta, "subtitle", lang, ""),
                "description": localized(meta, "description", lang, localized(meta, "subtitle", lang, "")),
                "tags": [tag.strip() for tag in tags.split(",") if tag.strip()],
                "content": markdown_to_html(sections.get(lang, "")),
                "url": language_url(lang, "post", slug),
            }
        posts.append(post)
    return sorted(posts, key=lambda item: item["date"], reverse=True)


def post_cards(posts, lang, limit=None):
    selected = posts[:limit] if limit else posts
    cards = []
    for post in selected:
        data = post["lang"][lang]
        tags = "".join(f"<span>{html.escape(tag)}</span>" for tag in data["tags"][:3])
        cards.append(
            f"""
<article class="post-card" data-animate>
  <div class="post-card__meta">
    <time datetime="{post["date"].date()}">{post["date_display"]}</time>
    <span>{html.escape(post["reading_time"])}</span>
  </div>
  <h3><a href="{data["url"]}">{html.escape(data["title"])}</a></h3>
  <p>{html.escape(data["subtitle"])}</p>
  <div class="post-card__tags">{tags}</div>
</article>
"""
        )
    return "\n".join(cards)


def write(path, content):
    target = DIST / path.strip("/")
    if path in {"_headers", "_redirects"}:
        target.write_text(content, encoding="utf-8")
    elif path.endswith("/") or not target.suffix:
        target.mkdir(parents=True, exist_ok=True)
        target = target / "index.html"
        target.write_text(content, encoding="utf-8")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def copy_static():
    target = DIST / "static"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(STATIC_DIR, target)


def build_language(lang, posts):
    copy = COPY[lang]
    write(
        language_url(lang, "home"),
        render(
            "index.html",
            lang=lang,
            page="home",
            title=copy["home_title"],
            description=copy["home_description"],
            latest_posts=post_cards(posts, lang, limit=3),
        ),
    )
    write(
        language_url(lang, "articles"),
        render(
            "post_list.html",
            lang=lang,
            page="articles",
            title=copy["articles_title"],
            description=copy["articles_intro"],
            post_cards=post_cards(posts, lang),
        ),
    )
    write(
        language_url(lang, "calculator"),
        render(
            "calculator.html",
            lang=lang,
            page="calculator",
            title=copy["calculator_title"],
            description=copy["calculator_intro"],
        ),
    )
    write(
        language_url(lang, "guide"),
        render(
            "guide.html",
            lang=lang,
            page="guide",
            title=copy["guide_title"],
            description=copy["guide_intro"],
        ),
    )
    for post in posts:
        data = post["lang"][lang]
        write(
            data["url"],
            render(
                "post.html",
                lang=lang,
                page="post",
                slug=post["slug"],
                title=f"{data['title']} - salvatustokens",
                description=data["description"],
                post_title=html.escape(data["title"]),
                post_subtitle=html.escape(data["subtitle"]),
                post_date=post["date_display"],
                post_author=html.escape(post["author"]),
                post_reading_time=html.escape(post["reading_time"]),
                post_tags="".join(f"<span>{html.escape(tag)}</span>" for tag in data["tags"]),
                post_content=data["content"],
            ),
        )


def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    copy_static()

    posts = read_posts()
    for lang in ("es", "en"):
        build_language(lang, posts)

    urls = []
    for lang in ("es", "en"):
        urls.extend([
            language_url(lang, "home"),
            language_url(lang, "articles"),
            language_url(lang, "calculator"),
            language_url(lang, "guide"),
        ])
        urls.extend(post["lang"][lang]["url"] for post in posts)
    sitemap = "\n".join(SITE["url"] + url for url in urls)
    write("sitemap.txt", sitemap + "\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.txt\n")

    rss_items = "\n".join(
        f"""
    <item>
      <title>{html.escape(post["lang"]["es"]["title"])}</title>
      <link>{SITE["url"]}{post["lang"]["es"]["url"]}</link>
      <guid>{SITE["url"]}{post["lang"]["es"]["url"]}</guid>
      <pubDate>{format_datetime(post["date"])}</pubDate>
      <description>{html.escape(post["lang"]["es"]["description"])}</description>
    </item>"""
        for post in posts[:20]
    )
    write(
        "rss.xml",
        f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>{SITE["name"]}</title>
    <link>{SITE["url"]}/</link>
    <description>{SITE["description"]}</description>{rss_items}
  </channel>
</rss>
""",
    )
    write(
        "_headers",
        """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
""",
    )
    write(
        "_redirects",
        """/lang/en /en/ 302
/lang/es / 302
""",
    )
    print(f"Built {len(posts)} posts in 2 languages into {DIST}")


if __name__ == "__main__":
    build()
