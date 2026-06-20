"""Descarga y exporta los modelos al formato OpenVINO (IR).

Se ejecuta UNA sola vez (necesita internet). A partir de ahí, todo funciona
100% offline. El SLM se cuantiza a INT4 para caber holgadamente en la N100.

Uso:
    python download_models.py
"""

import subprocess
import sys

import config


def export(model_id: str, out_dir, extra_args: list[str]) -> None:
    if out_dir.exists():
        print(f"[=] Ya existe, se omite: {out_dir}")
        return
    out_dir.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "optimum-cli", "export", "openvino",
        "--model", model_id,
        *extra_args,
        str(out_dir),
    ]
    print(f"[>] Exportando {model_id} -> {out_dir}")
    subprocess.run(cmd, check=True)


def main() -> int:
    # SLM cuantizado a INT4 (pesos ~1 GB para Qwen2.5-1.5B).
    export(
        config.LLM_MODEL_ID,
        config.LLM_OV_DIR,
        ["--weight-format", "int4", "--task", "text-generation-with-past"],
    )
    # Embeddings (feature-extraction), precisión por defecto.
    export(
        config.EMBED_MODEL_ID,
        config.EMBED_OV_DIR,
        ["--task", "feature-extraction"],
    )
    print("\n[OK] Modelos listos en", config.MODELS_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
