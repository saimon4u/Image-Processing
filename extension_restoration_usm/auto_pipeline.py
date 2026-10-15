"""Blind auto-restoration: detect degradations, apply only the matching filters.

    image -> detect -> [impulse repair] -> [NLM denoise] -> [Wiener deblur] -> light modified USM

Filters are applied in reverse physical order (impulse, noise, blur). If nothing
is detected the image is returned untouched, so clean inputs are not harmed.
"""
from __future__ import annotations

import numpy as np

from auto_detect import BLUR_SIGMA_MIN, BlurSigmaModel, analyse, estimate_noise_sigma
import restoration
from config import K_SCALE_AFTER_RESTORE, LAM, T
from sharpening_ext import modified_usm

# Deblur with 80% of the estimated radius: over-estimating the PSF hurts more than
# under-estimating it (chosen by leave-one-source-out sweep over {1.0, 0.8, 0.65}).
BLUR_SHRINK = 0.8


def pre_blur_stage(image: np.ndarray) -> tuple[np.ndarray, dict, list]:
    """Impulse repair + Gaussian denoise; the image the blur estimator looks at."""
    plan = analyse(image)
    work = plan.pop("_impulse_free")
    plan.pop("impulse_mask")
    applied = []
    if plan["has_impulse"]:
        applied.append("median_impulse")
    if plan["has_noise"]:
        work = restoration.restore_gaussian_noise(work, plan["noise_sigma"])
        applied.append("nlm")
    return work, plan, applied


def auto_restore(image: np.ndarray, blur_model: BlurSigmaModel) -> tuple[np.ndarray, dict]:
    work, plan, applied = pre_blur_stage(image)

    sigma_b = blur_model.predict(work)
    plan["blur_sigma"] = sigma_b
    plan["has_blur"] = sigma_b >= BLUR_SIGMA_MIN
    if plan["has_blur"]:
        # slightly more regularised when noise was present (residual noise gets amplified)
        old = restoration.WIENER_BALANCE
        restoration.WIENER_BALANCE = 0.10 if plan["has_noise"] else old
        try:
            work = restoration.restore_blur(work, sigma_b * BLUR_SHRINK)
        finally:
            restoration.WIENER_BALANCE = old
        applied.append("wiener")

    plan["restored_pre_usm"] = work
    if applied:
        k_scale = K_SCALE_AFTER_RESTORE["blur"] if plan["has_blur"] else K_SCALE_AFTER_RESTORE["gaussian_noise"]
        work = modified_usm(work, t=T, lam=LAM, k_scale=k_scale)
        applied.append("usm")

    plan["applied"] = applied
    return np.clip(work, 0.0, 1.0), plan


def fixed_chain(image: np.ndarray, blur_sigma: float = 2.5) -> np.ndarray:
    """Non-adaptive baseline: always median -> NLM -> Wiener -> USM (no detection)."""
    out = restoration.restore_salt_pepper(image, 0.05)
    out = restoration.restore_gaussian_noise(out, max(estimate_noise_sigma(out), 0.02))
    out = restoration.restore_blur(out, blur_sigma)
    return modified_usm(out, t=T, lam=LAM, k_scale=0.2)
