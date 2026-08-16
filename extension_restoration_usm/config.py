"""Experiment configuration for the restoration + modified-USM extension.

Domains
-------
  Medical  : frontal chest radiographs (X-ray), kept grayscale.
  Satellite: optical remote-sensing RGB from UC Merced (USGS National Map).

Degradations (exactly three, matching TID2013 categories #1, #6, #8)
-------------------------------------------------------------------
  salt_pepper    : impulse noise
  gaussian_noise : additive white Gaussian noise
  blur           : Gaussian blur

Paper configuration used as the starting point (Aarthy & Keerthi, 2025):
  t = 0.6, lambda = 0.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent

DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "output"
FIG_DIR = OUT_DIR / "figures"
PANEL_DIR = OUT_DIR / "panels"
TABLE_DIR = OUT_DIR / "tables"

DOMAINS = ("medical", "satellite")
DEGRADATIONS = ("salt_pepper", "gaussian_noise", "blur")

# Paper-reported optimum (Sect. 4.1).
T = 0.6
LAM = 0.0
USM_SIGMA = 2.0  # Gaussian sigma inside the USM smoother (Eq. 35); paper does not state a value.

# Longest side after load. Keeps fine detail while keeping the run tractable.
MAX_SIDE = 512

# Three severity levels per degradation (TID2013 uses five; three is enough to
# see the trend without exploding the number of processed images).
SALT_PEPPER_AMOUNTS = (0.02, 0.05, 0.10)
GAUSSIAN_NOISE_SIGMAS = (0.04, 0.08, 0.12)  # std on the [0, 1] intensity range
BLUR_SIGMAS = (1.5, 2.5, 4.0)

# Parameter sweep to test whether t = 0.6, lambda = 0 remains suitable.
T_SWEEP = (0.4, 0.6, 0.8)
LAM_SWEEP = (0.0,)

RNG_SEED = 42
N_CLEAN_IMAGES = 6

# Restoration hyperparameters (justified in STUDY.md).
MEDIAN_SIZE_BY_AMOUNT = {0.02: 3, 0.05: 5, 0.10: 5}
NLM_PATCH_SIZE = 5
NLM_PATCH_DISTANCE = 6
NLM_H_SCALE = 0.8  # h = NLM_H_SCALE * estimated sigma
WIENER_BALANCE = 0.05  # noise-to-signal; smaller = more aggressive deblur

# After restoration the residual image-smooth(image) is already larger than on a
# degraded input, so the paper's full k (tuned for blurry IQA images) overshoots.
# Pipeline B therefore applies k_eff = γ · k(t, λ) with γ < 1.
# γ was chosen on a held-out-style sweep so that B stays close to restoration-only
# quality while still applying a light coefficient-bound crisp.
K_SCALE_AFTER_RESTORE = {
    "salt_pepper": 0.12,
    "gaussian_noise": 0.12,
    "blur": 0.20,
}
