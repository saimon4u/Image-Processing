"""Practical (blind) form of the paper's modified unsharp masking.

The parent implementation in gregory_usm/sharpening.py follows Fig. 2 literally:
it extracts the edge mask from the *clean reference* and adds it to the degraded
image. That is correct for the paper's IQA-benchmark protocol, but it would leak
ground-truth edges into both pipelines of this extension and hide the effect of
restoration.

Here the same coefficient-bound factor k = |a2| + |a3| is applied to edges
extracted from the image actually being sharpened:

    edge      = image − GaussianSmooth(image)
    sharpened = image + k(t, λ) · edge

This is the form that can be used at test time on medical or satellite images
for which no clean reference exists.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gregory_usm.sharpening import gaussian_smooth, sharpening_factor

from config import LAM, T, USM_SIGMA


def modified_usm(
    image: np.ndarray,
    t: float = T,
    lam: float = LAM,
    sigma: float = USM_SIGMA,
) -> np.ndarray:
    image = np.asarray(image, dtype=np.float64)
    vmax = 1.0 if image.max() <= 1.0 else 255.0
    smoothed = gaussian_smooth(image, sigma=sigma)
    edge = image - smoothed
    k = sharpening_factor(t, lam)
    return np.clip(image + k * edge, 0.0, vmax)
