"""Mathematical framework from Aarthy & Srutha Keerthi (2025).

Implements:
  - Gregory coefficients Lambda_n from the generating function
        G(xi) = xi / log(1 + xi) = 1 + sum_{n>=1} Lambda_n * xi^n      (Eq. 9)
  - u_n = (1 - t^n) / (1 - t)                                          (below Eq. 14)
  - Sharp coefficient bounds |a2|, |a3| for the class ST_Sigma(Lambda, t, lambda)
    derived in Theorem 1, Eqs. (32) and (34).
"""
from __future__ import annotations

from functools import lru_cache

import sympy as sp


@lru_cache(maxsize=1)
def _gregory_series(n_terms: int = 10):
    xi = sp.symbols("xi")
    g = xi / sp.log(1 + xi)
    series = sp.series(g, xi, 0, n_terms + 1).removeO()
    poly = sp.Poly(series, xi)
    coeffs = {}
    for n in range(1, n_terms + 1):
        coeffs[n] = poly.coeff_monomial(xi**n)
    return coeffs


def gregory_coefficients(n_max: int = 6):
    """Return {n: Lambda_n} for n = 1..n_max as exact rationals (Eq. 9)."""
    coeffs = _gregory_series(max(n_max, 6))
    return {n: coeffs[n] for n in range(1, n_max + 1)}


def u_n(n: int, t: float) -> float:
    """u_n = (1 - t^n) / (1 - t), the quantity used throughout Theorem 1."""
    if t == 1:
        return float(n)
    return (1 - t**n) / (1 - t)


def a2_bound(t: float, lam: float) -> float:
    """Sharp bound |a2| <= sqrt(3 / |2*{...}|)  (Eq. 32)."""
    u2 = u_n(2, t)
    u3 = u_n(3, t)
    inner = (
        3 * u2**2
        - 3 * u3
        - 6 * u2 * (1 + lam)
        + 9 * (1 + 2 * lam)
        + 7 * (2 * (1 + lam) - u2) ** 2
    )
    denom = abs(2 * inner)
    return (3 / denom) ** 0.5


def a3_bound(t: float, lam: float) -> float:
    """Sharp bound |a3| <= 1/(4[2(1+lam)-u2]^2) + 1/(2[3(1+2lam)-u3])  (Eq. 34)."""
    u2 = u_n(2, t)
    u3 = u_n(3, t)
    term1 = 1 / (4 * (2 * (1 + lam) - u2) ** 2)
    term2 = 1 / (2 * (3 * (1 + 2 * lam) - u3))
    return term1 + term2
