"""Quality and sharpness metrics for the extension experiment.

Full-reference: PSNR, SSIM (possible because every degraded image has a clean pair).
Paper metrics:  PLCC (Eq. 36), SROCC (Eq. 37) from gregory_usm.metrics.
MOS proxy:      SSIM(output, clean), used because these domain images have no
                human MOS. The algorithm score is a no-reference sharpness
                (variance of the Laplacian / Tenengrad-style).

If sharpening only amplifies noise, the Laplacian variance rises while SSIM
falls, so PLCC/SROCC drop. Restoration-then-sharpening should raise both
full-reference scores *and* the agreement between 'looks sharp' and 'is closer
to the clean image'.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import laplace, sobel
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gregory_usm.metrics import plcc, srocc


def _gray(image: np.ndarray) -> np.ndarray:
    image = np.asarray(image, dtype=np.float64)
    if image.ndim == 3:
        return image.mean(axis=-1)
    return image


def psnr_score(reference: np.ndarray, test: np.ndarray) -> float:
    return float(psnr(reference, test, data_range=1.0))


def ssim_score(reference: np.ndarray, test: np.ndarray) -> float:
    kwargs = dict(data_range=1.0)
    if reference.ndim == 3:
        kwargs["channel_axis"] = -1
    return float(ssim(reference, test, **kwargs))


def laplacian_variance(image: np.ndarray) -> float:
    """No-reference sharpness: variance of Laplacian (Pech-Pacheco et al.)."""
    return float(np.var(laplace(_gray(image))))


def tenengrad(image: np.ndarray) -> float:
    """No-reference sharpness: mean squared Sobel gradient energy."""
    g = _gray(image)
    gx = sobel(g, axis=1)
    gy = sobel(g, axis=0)
    return float(np.mean(gx**2 + gy**2))


def pair_metrics(reference: np.ndarray, test: np.ndarray) -> dict[str, float]:
    return dict(
        psnr=psnr_score(reference, test),
        ssim=ssim_score(reference, test),
        lapvar=laplacian_variance(test),
        tenengrad=tenengrad(test),
    )


def correlation_block(sharpness: np.ndarray, quality: np.ndarray) -> dict[str, float]:
    """PLCC/SROCC between a no-reference sharpness score and SSIM-to-clean."""
    sharpness = np.asarray(sharpness, dtype=np.float64)
    quality = np.asarray(quality, dtype=np.float64)
    if len(sharpness) < 3 or np.allclose(sharpness, sharpness[0]) or np.allclose(quality, quality[0]):
        return dict(plcc=float("nan"), srocc=float("nan"))
    return dict(plcc=plcc(sharpness, quality), srocc=srocc(sharpness, quality))
