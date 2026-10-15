"""Auto-restore a folder of already-degraded images (no clean reference needed).

    python auto_restore_cli.py <input_dir> [<output_dir>]

For every image: reports what was detected (impulse / Gaussian noise / blur and
their estimated strength), which filters were applied, and no-reference
before/after numbers (noise sigma, sharpness). The blur-sigma estimator is
trained on all clean images in data/ and data_extra/.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent))

from auto_detect import BlurSigmaModel, blur_features, estimate_noise_sigma  # noqa: E402
from auto_pipeline import auto_restore, pre_blur_stage  # noqa: E402
from degradations import load_float, save_float  # noqa: E402
from metrics_eval import laplacian_variance, tenengrad  # noqa: E402
from run_auto_experiment import CALIB_DRAWS, calibration_set, load_tiles  # noqa: E402


def train_model() -> BlurSigmaModel:
    calib = calibration_set(load_tiles())
    return BlurSigmaModel().fit(np.stack([r[1] for r in calib]), np.array([r[2] for r in calib]))


def main():
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.parent / (src.name + "_restored")
    dst.mkdir(parents=True, exist_ok=True)
    model = train_model()
    rows = []
    for path in sorted(p for p in src.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}):
        img = load_float(path)
        out, plan = auto_restore(img, model)
        save_float(dst / f"{path.stem}.png", out)
        rows.append(dict(
            image=path.name,
            impulse=plan["has_impulse"], impulse_density=round(plan["impulse_density"], 4),
            gaussian_noise=plan["has_noise"], noise_sigma_before=round(plan["noise_sigma"], 4),
            noise_sigma_after=round(estimate_noise_sigma(out), 4),
            blur=plan["has_blur"], blur_sigma=round(plan["blur_sigma"], 2),
            filters="+".join(plan["applied"]) or "none",
            tenengrad_before=round(tenengrad(img), 5), tenengrad_after=round(tenengrad(out), 5),
        ))
        print(rows[-1])
    pd.DataFrame(rows).to_csv(dst / "detection_report.csv", index=False)


if __name__ == "__main__":
    main()
