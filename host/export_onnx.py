"""
export_onnx.py
~~~~~~~~~~~~~~
Export the smallest available pretrained ImageNet classifier from timm to ONNX
so that Triton can serve it.

Model chosen: mobilenetv3_small_050  (~1.6 M parameters, ~6 MB on disk)
  - Trained on ImageNet-1k
  - Accepts: float32 tensor of shape [1, 3, 224, 224]  (NCHW, normalised)
  - Produces: float32 tensor of shape [1, 1000]         (raw logits)

Run once before starting Triton:
    python export_onnx.py
"""

import pathlib

import timm
import torch

# ── Configuration ──────────────────────────────────────────────────────────────

MODEL_NAME  = "mobilenetv3_small_050.lamb_in1k"   # ~1.6 M params
OUTPUT_PATH = pathlib.Path("model_repository/image_classifier/1/model.onnx")
OPSET       = 17

# ── Export ─────────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"Loading '{MODEL_NAME}' (pretrained=True) …")
    model = timm.create_model(MODEL_NAME, pretrained=True)
    model.eval()

    # Retrieve the preprocessing config that was used during training so we can
    # document it – the client must apply the same transform.
    data_cfg = timm.data.resolve_model_data_config(model)
    print("Preprocessing expected by the model:")
    print(f"  input_size : {data_cfg['input_size']}")
    print(f"  mean       : {data_cfg['mean']}")
    print(f"  std        : {data_cfg['std']}")

    dummy = torch.zeros(1, *data_cfg["input_size"])   # [1, 3, 224, 224]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nExporting to '{OUTPUT_PATH}' (opset {OPSET}) …")
    torch.onnx.export(
        model,
        dummy,
        str(OUTPUT_PATH),
        input_names=["input"],
        output_names=["output"],
        opset_version=OPSET,
        # Fixed shapes – no dynamic axes because batching is disabled in Triton.
        dynamic_axes=None,
    )

    size_mb = OUTPUT_PATH.stat().st_size / 1024 / 1024
    print(f"Done – {size_mb:.1f} MB written to '{OUTPUT_PATH}'")


if __name__ == "__main__":
    main()
