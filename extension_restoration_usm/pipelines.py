"""Pipeline A (sharpen only) vs Pipeline B (restore then lightly sharpen)."""
from __future__ import annotations

from config import K_SCALE_AFTER_RESTORE
from restoration import restore
from sharpening_ext import modified_usm


def pipeline_a(degraded, t: float, lam: float):
    """Degraded → Modified USM (paper strength, k_scale = 1)."""
    return modified_usm(degraded, t=t, lam=lam, k_scale=1.0)


def pipeline_b(degraded, degradation: str, record: dict, t: float, lam: float):
    """Degraded → Restoration → Modified USM with restoration-aware k.

    Returns (restored, sharpened).
    """
    restored = restore(degraded, degradation, record)
    k_scale = K_SCALE_AFTER_RESTORE[degradation]
    sharpened = modified_usm(restored, t=t, lam=lam, k_scale=k_scale)
    return restored, sharpened
