"""Restoration methods matched to the three degradations. See STUDY.md."""
from __future__ import annotations

import numpy as np
from scipy.ndimage import median_filter
from skimage.restoration import denoise_nl_means, estimate_sigma, wiener

from config import (
    MEDIAN_SIZE_BY_AMOUNT,
    NLM_H_SCALE,
    NLM_PATCH_DISTANCE,
    NLM_PATCH_SIZE,
    WIENER_BALANCE,
)


def gaussian_psf(sigma: float, truncate: float = 4.0) -> np.ndarray:
    """Discrete Gaussian kernel matching scipy.ndimage.gaussian_filter's default truncation."""
    radius = max(1, int(truncate * sigma + 0.5))
    ax = np.arange(-radius, radius + 1, dtype=np.float64)
    xx, yy = np.meshgrid(ax, ax)
    kernel = np.exp(-(xx**2 + yy**2) / (2.0 * sigma**2))
    kernel /= kernel.sum()
    return kernel


def restore_salt_pepper(image: np.ndarray, amount: float) -> np.ndarray:
    """Median filter. Window grows with impulse density (3 then 5)."""
    size = MEDIAN_SIZE_BY_AMOUNT.get(float(amount), 5)
    if image.ndim == 3:
        restored = np.stack(
            [median_filter(image[..., c], size=size) for c in range(image.shape[2])],
            axis=-1,
        )
    else:
        restored = median_filter(image, size=size)
    return np.clip(restored, 0.0, 1.0)


def restore_gaussian_noise(image: np.ndarray, sigma: float | None = None) -> np.ndarray:
    """Non-local means (Buades, Coll & Morel 2005), edge-preserving AWGN denoiser."""
    channel_axis = -1 if image.ndim == 3 else None
    if sigma is None:
        est = estimate_sigma(image, average_sigmas=True, channel_axis=channel_axis)
        sigma = float(est)
    h = NLM_H_SCALE * float(sigma)
    restored = denoise_nl_means(
        image,
        h=h,
        fast_mode=True,
        patch_size=NLM_PATCH_SIZE,
        patch_distance=NLM_PATCH_DISTANCE,
        channel_axis=channel_axis,
    )
    return np.clip(np.asarray(restored, dtype=np.float64), 0.0, 1.0)


def restore_blur(image: np.ndarray, sigma: float) -> np.ndarray:
    """Wiener deconvolution with the known Gaussian PSF, reflect-padded.

    FFT deconvolution wraps the image torus-like. Without padding that produces
    bright/dark bands at the border, which the subsequent USM then amplifies.
    Reflect padding of ~4σ (the Gaussian kernel support) suppresses that.
    """
    psf = gaussian_psf(sigma)
    pad = max(8, int(4.0 * sigma + 2))
    work = _reflect_pad(image, pad)
    if work.ndim == 3:
        restored = np.stack(
            [
                wiener(work[..., c], psf, balance=WIENER_BALANCE, clip=True)
                for c in range(work.shape[2])
            ],
            axis=-1,
        )
    else:
        restored = wiener(work, psf, balance=WIENER_BALANCE, clip=True)
    restored = _crop_pad(np.asarray(restored, dtype=np.float64), pad)
    return np.clip(restored, 0.0, 1.0)


def _reflect_pad(image: np.ndarray, pad: int) -> np.ndarray:
    if image.ndim == 2:
        return np.pad(image, pad, mode="reflect")
    return np.pad(image, ((pad, pad), (pad, pad), (0, 0)), mode="reflect")


def _crop_pad(image: np.ndarray, pad: int) -> np.ndarray:
    if image.ndim == 2:
        return image[pad:-pad, pad:-pad]
    return image[pad:-pad, pad:-pad, :]


def restore(image: np.ndarray, degradation: str, record: dict) -> np.ndarray:
    if degradation == "salt_pepper":
        return restore_salt_pepper(image, record["amount"])
    if degradation == "gaussian_noise":
        return restore_gaussian_noise(image, record.get("sigma"))
    if degradation == "blur":
        return restore_blur(image, record["sigma"])
    raise ValueError(f"unknown degradation {degradation!r}")
