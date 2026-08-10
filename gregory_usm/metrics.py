"""Evaluation metrics used in Sect. 5: PLCC (Eq. 36) and SROCC (Eq. 37)."""
from __future__ import annotations

import numpy as np


def plcc(alpha: np.ndarray, beta: np.ndarray) -> float:
    """Pearson linear correlation coefficient (Eq. 36).

    alpha: algorithm scores, beta: subjective (MOS) scores.
    """
    alpha = np.asarray(alpha, dtype=np.float64)
    beta = np.asarray(beta, dtype=np.float64)
    alpha_bar = alpha.mean()
    beta_bar = beta.mean()
    num = np.sum((alpha - alpha_bar) * (beta - beta_bar))
    den = np.sqrt(np.sum((alpha - alpha_bar) ** 2) * np.sum((beta - beta_bar) ** 2))
    return float(num / den)


def _rank(x: np.ndarray) -> np.ndarray:
    """Average ranks (1-indexed), matching ties as in Spearman's rho."""
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty_like(order, dtype=np.float64)
    sorted_x = x[order]
    n = len(x)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and sorted_x[j + 1] == sorted_x[i]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0
        ranks[order[i : j + 1]] = avg_rank
        i = j + 1
    return ranks


def srocc(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman's rank ordered correlation coefficient (Eq. 37)."""
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    n = len(x)
    gx = _rank(x)
    gy = _rank(y)
    d2 = np.sum((gx - gy) ** 2)
    return float(1 - (6 * d2) / (n * (n**2 - 1)))
