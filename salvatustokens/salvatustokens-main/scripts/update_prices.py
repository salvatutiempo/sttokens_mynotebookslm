#!/usr/bin/env python3
"""Refresca static/data/models.json con tarifas del dataset público de LiteLLM.

LiteLLM mantiene `model_prices_and_context_window.json` con el coste por token
(entrada/salida) de cientos de modelos. Este script lo descarga, convierte a
coste por millón de tokens y actualiza solo los precios de los modelos que
seguimos (los identificados con su clave `litellm`). El resto de campos
—nombres, notas, contexto, orden— se conservan tal cual.

Sin dependencias externas: usa solo la librería estándar.
"""

import datetime
import json
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "static" / "data" / "models.json"
SOURCE_URL = (
    "https://raw.githubusercontent.com/BerriAI/litellm/main/"
    "model_prices_and_context_window.json"
)


def fetch_prices(url):
    request = urllib.request.Request(
        url, headers={"User-Agent": "salvatustokens-price-bot"}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def per_million(value):
    """Convierte coste por token a coste por millón de tokens."""
    return round(float(value) * 1_000_000, 4)


def main():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    try:
        prices = fetch_prices(SOURCE_URL)
    except Exception as error:  # noqa: BLE001 - el log lo verá la Action
        print(f"No se pudo descargar el dataset de precios: {error}", file=sys.stderr)
        return 1

    changed = False
    matched = []
    missing = []

    for model in data["models"]:
        key = model.get("litellm")
        if not key:
            continue
        entry = prices.get(key)
        if not entry:
            missing.append(key)
            continue
        matched.append(key)

        new_input = entry.get("input_cost_per_token")
        if new_input is not None:
            value = per_million(new_input)
            if value != model.get("input"):
                model["input"] = value
                changed = True

        new_output = entry.get("output_cost_per_token")
        if new_output is not None:
            value = per_million(new_output)
            if value != model.get("output"):
                model["output"] = value
                changed = True

    print(f"Modelos emparejados: {len(matched)} | sin coincidencia: {missing or 'ninguno'}")

    if changed:
        data["updated"] = datetime.date.today().isoformat()
        DATA_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"Precios actualizados. Fecha: {data['updated']}")
    else:
        print("Sin cambios de precio.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
