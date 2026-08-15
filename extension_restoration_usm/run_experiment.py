"""End-to-end runner for the restoration + modified-USM domain extension.

Phases
------
1. Collect clean chest X-rays and UC Merced remote-sensing scenes (if needed).
2. Synthesize salt-and-pepper, Gaussian noise, and Gaussian blur.
3. Run Pipeline A (sharpen only) and Pipeline B (restore then sharpen).
4. Compute PSNR, SSIM, PLCC, SROCC.
5. Write 5-panel visual figures, the comparison table, and the analysis.
6. Small t-sweep to test whether t = 0.6, λ = 0 remains suitable.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(REPO_ROOT))

from analyze import comparison_table, write_analysis, write_csv  # noqa: E402
from collect_images import main as collect_main  # noqa: E402
from config import (  # noqa: E402
    DATA_DIR,
    DEGRADATIONS,
    FIG_DIR,
    LAM,
    OUT_DIR,
    PANEL_DIR,
    T,
    T_SWEEP,
    TABLE_DIR,
)
from degradations import load_float, main as synthesize_main, save_float  # noqa: E402
from metrics_eval import correlation_block, pair_metrics  # noqa: E402
from pipelines import pipeline_a, pipeline_b  # noqa: E402
from visualize import save_five_panel, save_heatmap  # noqa: E402


def ensure_data() -> list[dict]:
    collect_main()
    synthesize_main()
    manifest = json.loads((DATA_DIR / "manifest.json").read_text(encoding="utf-8"))
    return manifest


def run_pipelines(manifest: list[dict]) -> tuple[list[dict], dict]:
    """Returns per-image rows and a cache of arrays used for visual panels."""
    rows = []
    cache = {}
    n = len(manifest)
    for i, rec in enumerate(manifest, start=1):
        domain = rec["domain"]
        deg = rec["degradation"]
        print(f"[{i:3d}/{n}] {domain:9s} {deg:15s} {rec['image']}_l{rec['level']}")

        clean = load_float(DATA_DIR / rec["clean"])
        degraded = load_float(DATA_DIR / rec["degraded"])

        sharp_only = pipeline_a(degraded, t=T, lam=LAM)
        restored, restore_sharp = pipeline_b(degraded, deg, rec, t=T, lam=LAM)

        m_deg = pair_metrics(clean, degraded)
        m_rest = pair_metrics(clean, restored)
        m_a = pair_metrics(clean, sharp_only)
        m_b = pair_metrics(clean, restore_sharp)

        rows.append(
            dict(
                domain=domain,
                degradation=deg,
                image=rec["image"],
                level=rec["level"],
                deg_psnr=m_deg["psnr"],
                deg_ssim=m_deg["ssim"],
                rest_psnr=m_rest["psnr"],
                rest_ssim=m_rest["ssim"],
                a_psnr=m_a["psnr"],
                a_ssim=m_a["ssim"],
                a_lapvar=m_a["lapvar"],
                a_tenengrad=m_a["tenengrad"],
                b_psnr=m_b["psnr"],
                b_ssim=m_b["ssim"],
                b_lapvar=m_b["lapvar"],
                b_tenengrad=m_b["tenengrad"],
            )
        )

        key = (domain, deg, rec["image"], rec["level"])
        cache[key] = dict(
            clean=clean,
            degraded=degraded,
            restored=restored,
            sharp_only=sharp_only,
            restore_sharp=restore_sharp,
        )

        # Persist a mid-level example per domain × degradation × image.
        if rec["level"] == 2:
            tag = f"{domain}_{deg}_{rec['image']}_l{rec['level']}"
            save_float(OUT_DIR / "images" / f"{tag}_A.png", sharp_only)
            save_float(OUT_DIR / "images" / f"{tag}_B.png", restore_sharp)
            save_float(OUT_DIR / "images" / f"{tag}_restored.png", restored)

    return rows, cache


def attach_correlations(rows: list[dict]) -> list[dict]:
    """PLCC/SROCC are defined on a *set* of images, not a single image.

    Compute them per (domain, degradation, pipeline) over all images/levels,
    then copy the block values onto every row of that group so the comparison
    table can average them without mixing groups.
    """
    groups = defaultdict(list)
    for row in rows:
        groups[(row["domain"], row["degradation"])].append(row)

    corr_rows = []
    for (domain, deg), group in groups.items():
        a_corr = correlation_block(
            np.array([r["a_lapvar"] for r in group]),
            np.array([r["a_ssim"] for r in group]),
        )
        b_corr = correlation_block(
            np.array([r["b_lapvar"] for r in group]),
            np.array([r["b_ssim"] for r in group]),
        )
        for r in group:
            r["a_plcc"] = a_corr["plcc"]
            r["a_srocc"] = a_corr["srocc"]
            r["b_plcc"] = b_corr["plcc"]
            r["b_srocc"] = b_corr["srocc"]
        corr_rows.append(
            dict(domain=domain, degradation=deg, pipeline="A (sharpen only)", **a_corr)
        )
        corr_rows.append(
            dict(domain=domain, degradation=deg, pipeline="B (restore + sharpen)", **b_corr)
        )
    return corr_rows


def write_panels(cache: dict, rows: list[dict]) -> None:
    """One 5-panel figure per domain × degradation, using a representative mid-level image."""
    PANEL_DIR.mkdir(parents=True, exist_ok=True)
    chosen = {}
    for row in rows:
        if row["level"] != 2:
            continue
        key = (row["domain"], row["degradation"])
        # Prefer the first image name in sorted order for stability.
        prev = chosen.get(key)
        if prev is None or row["image"] < prev:
            chosen[key] = row["image"]

    for (domain, deg), image in sorted(chosen.items()):
        arrays = cache[(domain, deg, image, 2)]
        title = f"{domain.capitalize()}  |  {deg.replace('_', ' ')}  |  {image}  |  level 2"
        dest = PANEL_DIR / f"{domain}_{deg}_{image}_l2.png"
        save_five_panel(
            arrays["clean"],
            arrays["degraded"],
            arrays["restored"],
            arrays["sharp_only"],
            arrays["restore_sharp"],
            title=title,
            dest=dest,
        )
        print(f"panel {dest.name}")


def run_t_sweep(manifest: list[dict]) -> list[dict]:
    """t ∈ {0.4, 0.6, 0.8} at λ = 0, mid severity, first image of each domain × degradation."""
    picked = {}
    for rec in manifest:
        if rec["level"] != 2:
            continue
        key = (rec["domain"], rec["degradation"])
        if key not in picked or rec["image"] < picked[key]["image"]:
            picked[key] = rec

    sweep = []
    for rec in picked.values():
        clean = load_float(DATA_DIR / rec["clean"])
        degraded = load_float(DATA_DIR / rec["degraded"])
        for t in T_SWEEP:
            sharp_only = pipeline_a(degraded, t=t, lam=LAM)
            restored, restore_sharp = pipeline_b(
                degraded, rec["degradation"], rec, t=t, lam=LAM
            )
            m_a = pair_metrics(clean, sharp_only)
            m_b = pair_metrics(clean, restore_sharp)
            sweep.append(
                dict(
                    domain=rec["domain"],
                    degradation=rec["degradation"],
                    image=rec["image"],
                    t=t,
                    lam=LAM,
                    a_ssim=m_a["ssim"],
                    b_ssim=m_b["ssim"],
                    a_psnr=m_a["psnr"],
                    b_psnr=m_b["psnr"],
                )
            )
            print(
                f"sweep {rec['domain']:9s} {rec['degradation']:15s} "
                f"t={t:.1f}  A SSIM {m_a['ssim']:.4f}  B SSIM {m_b['ssim']:.4f}"
            )
    return sweep


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    PANEL_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "images").mkdir(parents=True, exist_ok=True)

    print("=== Phase 1–3: collect + synthesize domain images ===")
    manifest = ensure_data()

    print("=== Phase 4: Pipeline A vs Pipeline B ===")
    rows, cache = run_pipelines(manifest)
    corr_rows = attach_correlations(rows)

    print("=== Phase 5: tables, panels, analysis ===")
    write_csv(TABLE_DIR / "per_image.csv", rows)
    table = comparison_table(rows)
    write_csv(TABLE_DIR / "comparison.csv", table)
    write_csv(TABLE_DIR / "plcc_srocc.csv", corr_rows)
    save_heatmap(table, FIG_DIR / "ssim_improvement_heatmap.png")
    write_panels(cache, rows)

    print("=== Phase 6: t-sweep at λ = 0 ===")
    sweep_rows = run_t_sweep(manifest)
    write_csv(TABLE_DIR / "t_sweep.csv", sweep_rows)

    write_analysis(table, corr_rows, sweep_rows, OUT_DIR / "ANALYSIS.md")
    print(f"\nDone. Results in {OUT_DIR}")


if __name__ == "__main__":
    main()
