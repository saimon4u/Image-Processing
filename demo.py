"""Demo / evaluation of the modified unsharp masking pipeline from:

  Aarthy & Srutha Keerthi, "Enhancing Image Sharpness by Modified Unsharp
  Masking Using Coefficient Bounds Obtained for a Subclass of Analytic
  Functions", Arabian J. Sci. Eng. (2025).

Dataset note
------------
CSIQ / LIVE require a registration form; TID2013 / KADID-10k are only
distributed as single multi-hundred-MB / multi-GB archives (no per-file
HTTP access), so a true "subset download" isn't possible for them without
pulling the whole archive first. As a stand-in we use a handful of images
from the public-domain Kodak test suite (data/reference/) and reproduce
the *blur* distortion category the paper's datasets use: each reference
image is Gaussian-blurred at 5 increasing sigma levels, exactly mirroring
Figs. 7-9 ("Sharpening of various images ... at different blur levels").
This lets the full pipeline run end-to-end and be sanity-checked, but it
is not a reproduction of Table 1 / Table 2 (those require the real MOS
subjective scores shipped with CSIQ/LIVE/TID2013/KADID-10k).
"""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter
from skimage import io, img_as_float
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim

from gregory_usm import a2_bound, a3_bound, modified_unsharp_masking
from gregory_usm.sharpening import sharpening_factor

ROOT = Path(__file__).parent
REF_DIR = ROOT / "data" / "reference"
OUT_DIR = ROOT / "output"
OUT_DIR.mkdir(exist_ok=True)

T, LAM = 0.6, 0.0
BLUR_SIGMAS = [1.0, 2.0, 3.0, 4.0, 5.0]  # 5 blur levels, as in CSIQ/LIVE/TID2013
USM_SIGMA = 2.0  # Gaussian sigma for the smoothing step inside the pipeline (Eq. 35);
# not numerically specified in the paper, chosen as a typical edge-extraction scale.


def main():
    print(f"t = {T}, lambda = {LAM}")
    print(f"|a2| bound = {a2_bound(T, LAM):.4f}")
    print(f"|a3| bound = {a3_bound(T, LAM):.4f}")
    k = sharpening_factor(T, LAM)
    print(f"sharpening factor k = |a2| + |a3| = {k:.4f}\n")

    ref_paths = sorted(REF_DIR.glob("*.png"))
    if not ref_paths:
        raise SystemExit(f"No reference images found in {REF_DIR}")

    rows = []
    for ref_path in ref_paths:
        name = ref_path.stem
        original = img_as_float(io.imread(ref_path))
        if original.ndim == 2:
            original = np.stack([original] * 3, axis=-1)
        original = original[..., :3]

        for sigma in BLUR_SIGMAS:
            blurred = np.stack(
                [gaussian_filter(original[..., c], sigma=sigma) for c in range(3)],
                axis=-1,
            )
            sharpened = modified_unsharp_masking(
                original, blurred, t=T, lam=LAM, sigma=USM_SIGMA
            )

            psnr_before = psnr(original, blurred, data_range=1.0)
            psnr_after = psnr(original, sharpened, data_range=1.0)
            ssim_before = ssim(original, blurred, data_range=1.0, channel_axis=-1)
            ssim_after = ssim(original, sharpened, data_range=1.0, channel_axis=-1)

            tag = f"{name}_blur{sigma:.0f}"
            io.imsave(OUT_DIR / f"{tag}_blurred.png", (blurred * 255).astype(np.uint8), check_contrast=False)
            io.imsave(OUT_DIR / f"{tag}_sharpened.png", (sharpened * 255).astype(np.uint8), check_contrast=False)

            rows.append(
                dict(
                    image=name,
                    blur_sigma=sigma,
                    psnr_before=psnr_before,
                    psnr_after=psnr_after,
                    ssim_before=ssim_before,
                    ssim_after=ssim_after,
                )
            )
            print(
                f"{tag:20s} PSNR {psnr_before:6.2f} -> {psnr_after:6.2f}  "
                f"SSIM {ssim_before:.4f} -> {ssim_after:.4f}"
            )

    with open(OUT_DIR / "results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    improved = sum(1 for r in rows if r["psnr_after"] > r["psnr_before"])
    print(f"\nPSNR improved vs. blurred input in {improved}/{len(rows)} cases.")
    print(f"Outputs written to {OUT_DIR}")


if __name__ == "__main__":
    main()
