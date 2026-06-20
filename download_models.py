"""Download and export the models to the OpenVINO (IR) format.

Run this ONCE (it needs internet). After that, everything works 100% offline.
The SLM is quantized to INT4 so it fits comfortably on the N100.

Usage:
    python download_models.py
"""

import subprocess
import sys

import config


def export(model_id: str, out_dir, extra_args: list[str]) -> None:
    if out_dir.exists():
        print(f"[=] Already exists, skipping: {out_dir}")
        return
    out_dir.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "optimum-cli", "export", "openvino",
        "--model", model_id,
        *extra_args,
        str(out_dir),
    ]
    print(f"[>] Exporting {model_id} -> {out_dir}")
    subprocess.run(cmd, check=True)


def main() -> int:
    # SLM quantized to INT4 (weights ~1 GB for Qwen2.5-1.5B).
    export(
        config.LLM_MODEL_ID,
        config.LLM_OV_DIR,
        ["--weight-format", "int4", "--task", "text-generation-with-past"],
    )
    # Embeddings (feature-extraction), default precision.
    export(
        config.EMBED_MODEL_ID,
        config.EMBED_OV_DIR,
        ["--task", "feature-extraction"],
    )
    print("\n[OK] Models ready in", config.MODELS_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
