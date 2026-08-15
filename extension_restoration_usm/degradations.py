"""Synthesize the three experiment degradations from clean images.

Every degraded file is paired with its clean counterpart of the same stem.
A JSON manifest records the exact degradation parameters so restoration
(e.g. Wiener PSF) can use the known kernel.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

from config import (
    BLUR_SIGMAS,
    DATA_DIR,
    DEGRADATIONS,
    DOMAINS,
    GAUSSIAN_NOISE_SIGMAS,
    RNG_SEED,
    ROOT,
    SALT_PEPPER_AMOUNTS,
)


def _stable_id(stem: str) -> int:
    return int(hashlib.md5(stem.encode("utf-8")).hexdigest()[:8], 16) % 1000


def load_float(path: Path) -> np.ndarray:
    arr = np.asarray(Image.open(path), dtype=np.float64)
    if arr.max() > 1.0:
        arr = arr / 255.0
    return np.clip(arr, 0.0, 1.0)


def save_float(path: Path, image: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    u8 = np.clip(np.round(image * 255.0), 0, 255).astype(np.uint8)
    Image.fromarray(u8).save(path)


def salt_pepper(image: np.ndarray, amount: float, rng: np.random.Generator) -> np.ndarray:
    out = image.copy()
    hw = image.shape[:2]
    mask = rng.random(hw)
    salt = mask < amount / 2.0
    pepper = (mask >= amount / 2.0) & (mask < amount)
    if image.ndim == 3:
        out[salt] = 1.0
        out[pepper] = 0.0
    else:
        out[salt] = 1.0
        out[pepper] = 0.0
    return out


def gaussian_noise(image: np.ndarray, sigma: float, rng: np.random.Generator) -> np.ndarray:
    noise = rng.normal(0.0, sigma, size=image.shape)
    return np.clip(image + noise, 0.0, 1.0)


def gaussian_blur(image: np.ndarray, sigma: float) -> np.ndarray:
    if image.ndim == 3:
        blurred = np.stack(
            [gaussian_filter(image[..., c], sigma=sigma) for c in range(image.shape[2])],
            axis=-1,
        )
    else:
        blurred = gaussian_filter(image, sigma=sigma)
    return np.clip(blurred, 0.0, 1.0)


def synthesize_domain(domain: str) -> list[dict]:
    clean_dir = DATA_DIR / domain / "clean"
    clean_paths = sorted(clean_dir.glob("*.png"))
    if not clean_paths:
        raise SystemExit(f"No clean images in {clean_dir}. Run collect_images.py first.")

    records: list[dict] = []
    for clean_path in clean_paths:
        clean = load_float(clean_path)
        stem = clean_path.stem

        for level, amount in enumerate(SALT_PEPPER_AMOUNTS, start=1):
            rng = np.random.default_rng(RNG_SEED + level * 100 + _stable_id(stem))
            degraded = salt_pepper(clean, amount, rng)
            out = DATA_DIR / domain / "salt_pepper" / f"{stem}_l{level}.png"
            save_float(out, degraded)
            records.append(
                dict(
                    domain=domain,
                    degradation="salt_pepper",
                    image=stem,
                    level=level,
                    amount=amount,
                    clean=str(clean_path.relative_to(DATA_DIR)),
                    degraded=str(out.relative_to(DATA_DIR)),
                )
            )

        for level, sigma in enumerate(GAUSSIAN_NOISE_SIGMAS, start=1):
            rng = np.random.default_rng(RNG_SEED + 1000 + level * 100 + _stable_id(stem))
            degraded = gaussian_noise(clean, sigma, rng)
            out = DATA_DIR / domain / "gaussian_noise" / f"{stem}_l{level}.png"
            save_float(out, degraded)
            records.append(
                dict(
                    domain=domain,
                    degradation="gaussian_noise",
                    image=stem,
                    level=level,
                    sigma=sigma,
                    clean=str(clean_path.relative_to(DATA_DIR)),
                    degraded=str(out.relative_to(DATA_DIR)),
                )
            )

        for level, sigma in enumerate(BLUR_SIGMAS, start=1):
            degraded = gaussian_blur(clean, sigma)
            out = DATA_DIR / domain / "blur" / f"{stem}_l{level}.png"
            save_float(out, degraded)
            records.append(
                dict(
                    domain=domain,
                    degradation="blur",
                    image=stem,
                    level=level,
                    sigma=sigma,
                    clean=str(clean_path.relative_to(DATA_DIR)),
                    degraded=str(out.relative_to(DATA_DIR)),
                )
            )

    return records


def main() -> None:
    all_records: list[dict] = []
    for domain in DOMAINS:
        print(f"[{domain}] synthesizing {', '.join(DEGRADATIONS)}")
        all_records.extend(synthesize_domain(domain))
    manifest = DATA_DIR / "manifest.json"
    manifest.write_text(json.dumps(all_records, indent=2), encoding="utf-8")
    print(f"Wrote {len(all_records)} degraded images. Manifest: {manifest}")


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    main()
