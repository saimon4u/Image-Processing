"""Modified unsharp masking pipeline (Sect. 4.1-4.3, Fig. 2).

Pipeline exactly as described in the paper:
  1. Gaussian-smooth the ORIGINAL (reference) image                 (Sect. 4.2, Eq. 35)
  2. edge_image        = original - smoothed                       (Fig. 2, the "-" node)
  3. enhanced_edge      = k(t, lam) * edge_image                    (Fig. 2, the "*" node)
       where k combines the coefficient bounds |a2|, |a3| from
       Theorem 1 (Eqs. 32, 34). The paper does not give an explicit
       combination formula for the two bounds into one scalar; per
       the accompanying implementation decision we use k = |a2| + |a3|.
  4. sharpened_image    = blurred + enhanced_edge                   (Fig. 2, the "+" node)

Best-performing parameters reported in the paper: t = 0.6, lambda = 0.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter

from .coefficients import a2_bound, a3_bound


def gaussian_smooth(image: np.ndarray, sigma: float = 2.0) -> np.ndarray:
    """Gaussian smoothing (Eq. 35). Works on grayscale (H,W) or color (H,W,C)."""
    image = image.astype(np.float64)
    if image.ndim == 3:
        return np.stack(
            [gaussian_filter(image[..., c], sigma=sigma) for c in range(image.shape[2])],
            axis=-1,
        )
    return gaussian_filter(image, sigma=sigma)


def sharpening_factor(t: float = 0.6, lam: float = 0.0) -> float:
    """k(t, lambda) = |a2| + |a3|, the coefficient-bound sharpening factor."""
    return a2_bound(t, lam) + a3_bound(t, lam)


def modified_unsharp_masking(
    original: np.ndarray,
    blurred: np.ndarray,
    t: float = 0.6,
    lam: float = 0.0,
    sigma: float = 2.0,
) -> np.ndarray:
    """Apply the paper's modified unsharp masking to sharpen `blurred`
    using edge detail extracted from `original` (Fig. 2 / Sect. 4.3 steps 1-5).

    original, blurred: float arrays in [0, 255] or [0, 1], same shape.
    Returns the sharpened image, clipped to the input's value range.
    """
    if original.shape != blurred.shape:
        raise ValueError("original and blurred images must have the same shape")

    original = original.astype(np.float64)
    blurred = blurred.astype(np.float64)

    vmax = 255.0 if original.max() > 1.0 else 1.0

    smoothed = gaussian_smooth(original, sigma=sigma)
    edge_image = original - smoothed
    k = sharpening_factor(t, lam)
    enhanced_edge = k * edge_image
    sharpened = blurred + enhanced_edge
    return np.clip(sharpened, 0.0, vmax)
