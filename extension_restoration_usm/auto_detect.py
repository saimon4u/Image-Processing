"""Blind degradation detector: decides which restoration filters an image needs.

No clean reference and no degradation metadata are used. Three independent
checks, in the order the degradations are physically applied in reverse
(impulse -> Gaussian noise -> blur):

  1. impulse (salt-and-pepper): pixels stuck at 0/1 that disagree with their
     3x3 median. Gives a per-pixel mask and a density.
  2. Gaussian noise: wavelet-MAD sigma estimate (Donoho) on the image after
     impulse pixels are repaired.
  3. blur: multi-scale gradient-energy ratios on the denoised image, mapped to
     a Gaussian sigma by a small regressor calibrated on blurred training
     images (see BlurSigmaModel).
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter, median_filter, sobel
from sklearn.ensemble import GradientBoostingRegressor

IMPULSE_DENSITY_MIN = 0.005   # below this the image is treated as impulse-free
NOISE_SIGMA_MIN = 0.015       # wavelet-MAD sigma above this => Gaussian noise present
BLUR_SIGMA_MIN = 1.0          # estimated blur sigma above this => blurred
_EXTREME = 1.5 / 255.0
_IMPULSE_DEV = 0.25


def _channels(image: np.ndarray):
    if image.ndim == 2:
        return [image]
    return [image[..., c] for c in range(image.shape[2])]


def detect_impulse(image: np.ndarray) -> tuple[np.ndarray, float]:
    """Return (boolean mask shaped like image, density)."""
    mask = np.zeros(image.shape, dtype=bool)
    for idx, ch in enumerate(_channels(image)):
        med = median_filter(ch, size=3)
        extreme = (ch <= _EXTREME) | (ch >= 1.0 - _EXTREME)
        m = extreme & (np.abs(ch - med) > _IMPULSE_DEV)
        if image.ndim == 2:
            mask = m
        else:
            mask[..., idx] = m
    return mask, float(mask.mean())


def repair_impulses(image: np.ndarray, mask: np.ndarray, density: float) -> np.ndarray:
    """Replace only the flagged pixels by a median (5x5 when dense)."""
    size = 5 if density > 0.05 else 3
    out = image.copy()
    for idx, ch in enumerate(_channels(image)):
        med = median_filter(ch, size=size)
        m = mask if image.ndim == 2 else mask[..., idx]
        if image.ndim == 2:
            out = np.where(m, med, ch)
        else:
            out[..., idx] = np.where(m, med, ch)
    return out


def estimate_noise_sigma(image: np.ndarray) -> float:
    """Donoho MAD estimate on the diagonal Haar sub-band (no PyWavelets needed)."""
    vals = []
    for ch in _channels(image):
        h, w = (ch.shape[0] // 2) * 2, (ch.shape[1] // 2) * 2
        c = ch[:h, :w]
        hh = (c[0::2, 0::2] - c[0::2, 1::2] - c[1::2, 0::2] + c[1::2, 1::2]) / 2.0
        vals.append(np.median(np.abs(hh)) / 0.6745)
    return float(np.mean(vals))


def _grad_energy(gray: np.ndarray) -> float:
    gx = sobel(gray, axis=1)
    gy = sobel(gray, axis=0)
    return float(np.mean(gx**2 + gy**2)) + 1e-12


def blur_features(image: np.ndarray) -> np.ndarray:
    """Log gradient-energy ratios after re-blurring at several scales.

    A sharp image loses much gradient energy when re-blurred; an already blurred
    one loses little. Scale-ratio profile is largely image-content independent.
    """
    gray = image if image.ndim == 2 else image.mean(axis=-1)
    e0 = _grad_energy(gray)
    feats = [np.log(_grad_energy(gaussian_filter(gray, s)) / e0) for s in (0.6, 1.0, 1.6, 2.5, 4.0)]
    feats.append(np.log(e0))
    return np.array(feats)


class BlurSigmaModel:
    """Maps blur_features -> Gaussian sigma. Fit on (image, true sigma) pairs."""

    def __init__(self):
        self.model = GradientBoostingRegressor(
            n_estimators=150, max_depth=2, learning_rate=0.08, subsample=0.9, random_state=0
        )

    def fit(self, feats: np.ndarray, sigmas: np.ndarray) -> "BlurSigmaModel":
        self.model.fit(feats, sigmas)
        return self

    def predict(self, image: np.ndarray) -> float:
        return float(max(0.0, self.model.predict(blur_features(image)[None])[0]))


def analyse(image: np.ndarray) -> dict:
    """Impulse + Gaussian-noise diagnosis (blur is judged after denoising)."""
    mask, density = detect_impulse(image)
    has_impulse = density >= IMPULSE_DENSITY_MIN
    work = repair_impulses(image, mask, density) if has_impulse else image

    sigma_n = estimate_noise_sigma(work)
    has_noise = sigma_n >= NOISE_SIGMA_MIN
    return dict(
        has_impulse=bool(has_impulse),
        impulse_density=density,
        impulse_mask=mask,
        has_noise=bool(has_noise),
        noise_sigma=sigma_n,
        _impulse_free=work,
    )
