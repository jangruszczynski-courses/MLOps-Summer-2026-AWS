"""
client.py
~~~~~~~~~
Send a single image to the Triton Inference Server via gRPC and print the
top-5 predicted ImageNet classes.

Usage:
    python client.py <path-to-image>          # e.g. python client.py cat.jpg
    python client.py                          # uses the built-in test pattern

Triton must be running and reachable at localhost:8001 (see docker-compose.yml).
"""

import sys
import urllib.request
import pathlib

import numpy as np
from PIL import Image
import tritonclient.grpc as grpcclient

# ── Constants ──────────────────────────────────────────────────────────────────

TRITON_URL     = "localhost:8001"
MODEL_NAME     = "image_classifier"
MODEL_VERSION  = "1"

INPUT_SIZE     = (224, 224)

# Standard ImageNet per-channel mean and std used during MobileNetV3 training.
IMAGENET_MEAN  = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD   = np.array([0.229, 0.224, 0.225], dtype=np.float32)

# Synset labels shipped with this repo (downloaded on first run).
LABELS_URL     = (
    "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
)
LABELS_PATH    = pathlib.Path("imagenet_classes.txt")

# ── Helpers ────────────────────────────────────────────────────────────────────

def load_labels() -> list[str]:
    """Return the 1 000 ImageNet class names (downloads once if absent)."""
    if not LABELS_PATH.exists():
        print(f"Downloading ImageNet labels to '{LABELS_PATH}' …")
        urllib.request.urlretrieve(LABELS_URL, LABELS_PATH)
    return LABELS_PATH.read_text().splitlines()


def preprocess(image_path: str) -> np.ndarray:
    """
    Load an image and apply the same preprocessing as during model training:
      1. Resize to INPUT_SIZE  (bilinear)
      2. Convert to float32 in [0, 1]
      3. Normalise with ImageNet mean / std
      4. Reorder axes to NCHW  and add batch dimension → [1, 3, 224, 224]
    """
    img = Image.open(image_path).convert("RGB")
    img = img.resize(INPUT_SIZE, Image.BILINEAR)

    arr = np.array(img, dtype=np.float32) / 255.0      # HWC, [0, 1]
    arr = (arr - IMAGENET_MEAN) / IMAGENET_STD          # normalise
    arr = arr.transpose(2, 0, 1)                        # HWC → CHW
    arr = np.expand_dims(arr, axis=0)                   # CHW → NCHW [1,3,H,W]
    return arr


def make_test_image(path: str = "test_pattern.png") -> str:
    """Create a simple colourful test image when no real image is available."""
    img = Image.new("RGB", (300, 300))
    pixels = img.load()
    for y in range(300):
        for x in range(300):
            pixels[x, y] = (x % 256, y % 256, (x + y) % 256)
    img.save(path)
    print(f"No image supplied – generated test pattern '{path}'.")
    return path


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    image_path = sys.argv[1] if len(sys.argv) > 1 else make_test_image()

    # ── 1. Preprocess ──────────────────────────────────────────────────────────
    print(f"Preprocessing '{image_path}' …")
    input_data = preprocess(image_path)          # shape: [1, 3, 224, 224]

    # ── 2. Build gRPC request ──────────────────────────────────────────────────
    inputs = [
        grpcclient.InferInput("input", input_data.shape, "FP32"),
    ]
    inputs[0].set_data_from_numpy(input_data)

    outputs = [
        grpcclient.InferRequestedOutput("output"),
    ]

    # ── 3. Send request ────────────────────────────────────────────────────────
    print(f"Connecting to Triton at {TRITON_URL} …")
    client = grpcclient.InferenceServerClient(url=TRITON_URL)

    response = client.infer(
        model_name=MODEL_NAME,
        model_version=MODEL_VERSION,
        inputs=inputs,
        outputs=outputs,
    )

    # ── 4. Decode results ──────────────────────────────────────────────────────
    logits = response.as_numpy("output")[0]          # shape: [1000]
    # Softmax for human-readable probabilities.
    exp_logits = np.exp(logits - logits.max())
    probs = exp_logits / exp_logits.sum()

    labels = load_labels()
    top5_idx = probs.argsort()[::-1][:5]

    print("\nTop-5 predictions:")
    for rank, idx in enumerate(top5_idx, start=1):
        print(f"  {rank}. [{idx:>4d}] {labels[idx]:<40s}  {probs[idx]*100:6.2f}%")


if __name__ == "__main__":
    main()
