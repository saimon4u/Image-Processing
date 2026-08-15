"""Pipeline A (sharpen only) vs Pipeline B (restore then sharpen)."""
from __future__ import annotations

from restoration import restore
from sharpening_ext import modified_usm


def pipeline_a(degraded, t: float, lam: float):
    """Degraded → Modified USM."""
    return modified_usm(degraded, t=t, lam=lam)


def pipeline_b(degraded, degradation: str, record: dict, t: float, lam: float):
    """Degraded → Restoration → Modified USM.

    Returns (restored, sharpened).
    """
    restored = restore(degraded, degradation, record)
    sharpened = modified_usm(restored, t=t, lam=lam)
    return restored, sharpened
