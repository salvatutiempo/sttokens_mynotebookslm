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
    # Check for the actual exported model, not just the folder, so a partial
    # or failed previous export is not mistaken for a finished one.
    if (out_dir / "openvino_model.xml").exists():
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


def main(argv: list[str]) -> int:
    # LLM(s) to export: the ids passed as arguments, or the default from config.
    # Example: python download_models.py "Qwen/Qwen2.5-1.5B-Instruct"
    llm_ids = argv[1:] or [config.LLM_MODEL_ID]
    for model_id in llm_ids:
        # Data-free weight-only INT4 (explicit --group-size/--ratio): no
        # calibration dataset, so it does not need the `datasets` library and is
        # faster/lighter. Quality is more than enough for SLM-based RAG.
        export(
            model_id,
            config.llm_dir(model_id),
            [
                "--weight-format", "int4",
                "--group-size", "128",
                "--ratio", "1.0",
                "--task", "text-generation-with-past",
            ],
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
    sys.exit(main(sys.argv))
