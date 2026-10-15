"""Blind auto-restoration experiment on chest X-ray and satellite images.

For every clean tile, 8 degradation scenarios (clean, each of the three, and
their mixtures) are synthesised. The auto pipeline sees ONLY the degraded image
and must (1) detect what is wrong, (2) pick the filters, (3) restore.

Compared per image against the clean original:
  degraded | Pipeline A (USM only) | fixed chain (no detection) |
  auto (blind) | oracle (true degradation known)

The blur-sigma estimator is calibrated leave-one-source-image-out, so the tile
being tested never contributes to the model that judges it.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent))

import restoration  # noqa: E402
from auto_detect import BLUR_SIGMA_MIN, BlurSigmaModel, blur_features  # noqa: E402
from auto_pipeline import auto_restore, fixed_chain, pre_blur_stage  # noqa: E402
from config import DATA_DIR, K_SCALE_AFTER_RESTORE, LAM, OUT_DIR, T  # noqa: E402
from degradations import gaussian_blur, gaussian_noise, load_float, salt_pepper, save_float  # noqa: E402
from metrics_eval import pair_metrics  # noqa: E402
from pipelines import pipeline_a  # noqa: E402
from sharpening_ext import modified_usm  # noqa: E402

TILE = 256
SCENARIOS = {
    "clean": (0, 0, 0),
    "sp": (0, 0, 1),
    "gn": (0, 1, 0),
    "blur": (1, 0, 0),
    "blur+gn": (1, 1, 0),
    "blur+sp": (1, 0, 1),
    "gn+sp": (0, 1, 1),
    "blur+gn+sp": (1, 1, 1),
}
MAX_TILES_PER_IMAGE = 2
DRAWS_PER_SCENARIO = 2
CALIB_DRAWS = 10
OUT = OUT_DIR / "auto"
EXAMPLES: set = set()


def load_tiles() -> list[dict]:
    tiles = []
    for domain in ("medical", "satellite"):
        paths = sorted((DATA_DIR / domain / "clean").glob("*.png")) + sorted((ROOT / "data_extra" / domain / "clean").glob("*.png"))
        for path in paths:
            img = load_float(path)
            h, w = img.shape[:2]
            if h < TILE or w < TILE:
                continue
            found = 0
            for y in range(0, h - TILE + 1, TILE):
                for x in range(0, w - TILE + 1, TILE):
                    tile = img[y : y + TILE, x : x + TILE]
                    if tile.std() < 0.04 or found >= MAX_TILES_PER_IMAGE:
                        continue
                    found += 1
                    tiles.append(dict(domain=domain, source=path.stem, name=f"{path.stem}_{y}_{x}", clean=tile))
    return tiles


def degrade(clean, kinds, rng):
    """Blur -> Gaussian noise -> impulse (sensor noise comes after optics)."""
    use_blur, use_gn, use_sp = kinds
    p = dict(blur_sigma=0.0, noise_sigma=0.0, sp_amount=0.0)
    img = clean
    if use_blur:
        p["blur_sigma"] = float(rng.uniform(1.2, 4.0))
        img = gaussian_blur(img, p["blur_sigma"])
    if use_gn:
        p["noise_sigma"] = float(rng.uniform(0.03, 0.12))
        img = gaussian_noise(img, p["noise_sigma"], rng)
    if use_sp:
        p["sp_amount"] = float(rng.uniform(0.02, 0.10))
        img = salt_pepper(img, p["sp_amount"], rng)
    return img, p


def oracle(degraded, p):
    out = degraded
    if p["sp_amount"] > 0:
        out = restoration.restore_salt_pepper(out, p["sp_amount"])
    if p["noise_sigma"] > 0:
        out = restoration.restore_gaussian_noise(out, p["noise_sigma"])
    if p["blur_sigma"] > 0:
        out = restoration.restore_blur(out, p["blur_sigma"])
        k = K_SCALE_AFTER_RESTORE["blur"]
    elif p["sp_amount"] > 0 or p["noise_sigma"] > 0:
        k = K_SCALE_AFTER_RESTORE["gaussian_noise"]
    else:
        return out
    return modified_usm(out, t=T, lam=LAM, k_scale=k)


def calibration_set(tiles):
    """Blur features of denoised, blurred training samples with known sigma."""
    rng = np.random.default_rng(1234)
    rows = []
    for t in tiles:
        for _ in range(CALIB_DRAWS):
            kinds = (int(rng.random() < 0.8), int(rng.random() < 0.5), int(rng.random() < 0.3))
            deg, p = degrade(t["clean"], kinds, rng)
            if kinds[0] == 0:
                p["blur_sigma"] = 0.0
            work, _, _ = pre_blur_stage(deg)
            rows.append((t["source"], blur_features(work), p["blur_sigma"]))
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "images").mkdir(exist_ok=True)
    tiles = load_tiles()
    print(f"{len(tiles)} tiles from {len({t['source'] for t in tiles})} source images")

    print("calibrating blur estimator ...")
    calib = calibration_set(tiles)
    models = {}
    for src in {t["source"] for t in tiles}:
        tr = [r for r in calib if r[0] != src]
        models[src] = BlurSigmaModel().fit(np.stack([r[1] for r in tr]), np.array([r[2] for r in tr]))

    EXAMPLES.update(next(t["name"] for t in tiles if t["domain"] == dom) for dom in ("medical", "satellite"))
    rng = np.random.default_rng(2025)
    rows = []
    n_total = len(tiles) * len(SCENARIOS) * DRAWS_PER_SCENARIO
    i = 0
    for t in tiles:
        for sname, kinds in SCENARIOS.items():
            for d in range(DRAWS_PER_SCENARIO):
                i += 1
                clean = t["clean"]
                deg, p = degrade(clean, kinds, rng)
                restored, plan = auto_restore(deg, models[t["source"]])
                outs = {
                    "degraded": deg,
                    "usm_only": pipeline_a(deg, T, LAM),
                    "fixed_chain": fixed_chain(deg),
                    "auto": restored,
                    "oracle": oracle(deg, p),
                }
                row = dict(
                    domain=t["domain"], source=t["source"], tile=t["name"], scenario=sname, draw=d,
                    true_blur=p["blur_sigma"], true_noise=p["noise_sigma"], true_sp=p["sp_amount"],
                    det_impulse=int(plan["has_impulse"]), det_noise=int(plan["has_noise"]), det_blur=int(plan["has_blur"]),
                    est_sp=plan["impulse_density"], est_noise=plan["noise_sigma"], est_blur=plan["blur_sigma"],
                    applied="+".join(plan["applied"]),
                )
                for k, img in outs.items():
                    m = pair_metrics(clean, img)
                    row[f"{k}_psnr"] = m["psnr"]
                    row[f"{k}_ssim"] = m["ssim"]
                rows.append(row)
                if d == 0 and t["name"] in EXAMPLES:
                    base = OUT / "images" / f"{t['name']}_{sname}"
                    for k, img in {"clean": clean, **outs}.items():
                        save_float(Path(f"{base}_{k}.png"), img)
                if i % 40 == 0:
                    print(f"  {i}/{n_total}")

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "auto_per_image.csv", index=False)
    write_report(df)


def pct(new, old):
    return 100.0 * (new - old) / old


def write_report(full: pd.DataFrame):
    lines = ["# Blind auto-restoration results\n"]
    clean = full[full.scenario == "clean"]
    df = full[full.scenario != "clean"].reset_index(drop=True)
    n = len(df)
    lines.append(f"{n} degraded images (tiles from {df.source.nunique()} source X-ray / satellite images, "
                 f"{df.scenario.nunique()} scenarios). The pipeline never saw the clean image or the degradation parameters.\n")

    # ---- detection ----
    true_sp, true_gn, true_bl = df.true_sp > 0, df.true_noise > 0, df.true_blur > 0
    lines.append("## 1. Detection accuracy (which filter is needed?)\n")
    lines.append("| Degradation | Accuracy | Recall (present) | False alarm (absent) |\n|---|---|---|---|")
    for name, truth, det in [("Salt-and-pepper", true_sp, df.det_impulse == 1),
                             ("Gaussian noise", true_gn, df.det_noise == 1),
                             ("Blur", true_bl, df.det_blur == 1)]:
        acc = (truth == det).mean() * 100
        rec = det[truth].mean() * 100
        fa = det[~truth].mean() * 100
        lines.append(f"| {name} | {acc:.1f}% | {rec:.1f}% | {fa:.1f}% |")
    all_ok = ((true_sp == (df.det_impulse == 1)) & (true_gn == (df.det_noise == 1)) & (true_bl == (df.det_blur == 1))).mean() * 100
    lines.append(f"\nExact combination correct (all three decisions right): **{all_ok:.1f}%**\n")
    b = df[true_bl & (df.det_blur == 1)]
    lines.append(f"Blur sigma estimate MAE (blurred images): {np.abs(b.est_blur - b.true_blur).mean():.2f} px; "
                 f"noise sigma MAE (noisy images): {np.abs(df[true_gn].est_noise - df[true_gn].true_noise).mean():.3f}\n")

    # ---- improvement ----
    methods = ["degraded", "usm_only", "fixed_chain", "auto", "oracle"]
    lines.append("## 2. Quality vs clean original (mean over all degraded images)\n")
    lines.append("| Method | PSNR (dB) | SSIM | PSNR gain vs degraded | SSIM gain vs degraded | MSE reduction |\n|---|---|---|---|---|---|")
    for m in methods:
        p, s = df[f"{m}_psnr"].mean(), df[f"{m}_ssim"].mean()
        dp = p - df.degraded_psnr.mean()
        mse = (1 - 10 ** (-(df[f"{m}_psnr"] - df.degraded_psnr) / 10)).mean() * 100
        lines.append(f"| {m} | {p:.2f} | {s:.4f} | {dp:+.2f} dB ({pct(p, df.degraded_psnr.mean()):+.1f}%) | "
                     f"{s - df.degraded_ssim.mean():+.4f} ({pct(s, df.degraded_ssim.mean()):+.1f}%) | {mse:.1f}% |")

    for key, title in [("scenario", "scenario"), ("domain", "domain")]:
        lines.append(f"\n## Improvement by {title} (auto pipeline)\n")
        lines.append(f"| {title} | n | PSNR degraded | PSNR auto | gain dB | SSIM degraded | SSIM auto | SSIM improvement | usm_only SSIM | fixed_chain SSIM |\n|---|---|---|---|---|---|---|---|---|---|")
        order = [s for s in SCENARIOS if s != "clean"] if key == "scenario" else sorted(df[key].unique())
        for g in order:
            sub = df[df[key] == g]
            lines.append(
                f"| {g} | {len(sub)} | {sub.degraded_psnr.mean():.2f} | {sub.auto_psnr.mean():.2f} | "
                f"{sub.auto_psnr.mean() - sub.degraded_psnr.mean():+.2f} | {sub.degraded_ssim.mean():.4f} | "
                f"{sub.auto_ssim.mean():.4f} | {pct(sub.auto_ssim.mean(), sub.degraded_ssim.mean()):+.1f}% | "
                f"{sub.usm_only_ssim.mean():.4f} | {sub.fixed_chain_ssim.mean():.4f} |")

    lines.append("\n## Do-no-harm check: already-clean inputs\n")
    lines.append(f"{len(clean)} clean images. Left completely untouched: {100 * (clean.applied.isna()).mean():.1f}%. "
                 f"Mean SSIM vs original after auto pipeline: {clean.auto_ssim.mean():.4f} "
                 f"(fixed chain: {clean.fixed_chain_ssim.mean():.4f}, USM only: {clean.usm_only_ssim.mean():.4f}).\n")
    bad = df[df.auto_psnr < df.degraded_psnr]
    lines.append(f"\nImages where auto restoration made PSNR *worse* than the degraded input: {len(bad)}/{n} "
                 f"({100 * len(bad) / n:.1f}%).\n")
    (OUT / "AUTO_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    if "--report-only" in sys.argv:
        write_report(pd.read_csv(OUT / "auto_per_image.csv"))
    else:
        main()
