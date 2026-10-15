"""Ablation: how much does the attenuated USM step add on top of detection + restoration?

Detection and restoration are run once per image (held-out split: blur model is
trained on even-indexed source images, evaluation on odd-indexed ones); the
USM gain k_eff = gamma * k is then swept, including gamma = 0 (restoration only)
and gamma = 1 (the paper's full k).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent))

from auto_detect import BlurSigmaModel  # noqa: E402
from auto_pipeline import auto_restore  # noqa: E402
from config import LAM, T  # noqa: E402
from metrics_eval import pair_metrics  # noqa: E402
from run_auto_experiment import SCENARIOS, calibration_set, degrade, load_tiles  # noqa: E402
from sharpening_ext import modified_usm  # noqa: E402

GAMMAS = (0.0, 0.05, 0.12, 0.2, 0.4, 1.0)


def main():
    tiles = load_tiles()
    srcs = sorted({t["source"] for t in tiles})
    train = set(srcs[::2])
    calib = calibration_set([t for t in tiles if t["source"] in train])
    model = BlurSigmaModel().fit(np.stack([r[1] for r in calib]), np.array([r[2] for r in calib]))
    rng = np.random.default_rng(99)
    rows = []
    for t in [t for t in tiles if t["source"] not in train]:
        for sname, kinds in SCENARIOS.items():
            if sname == "clean":
                continue
            deg, p = degrade(t["clean"], kinds, rng)
            _, plan = auto_restore(deg, model)
            base = plan["restored_pre_usm"]
            row = dict(domain=t["domain"], scenario=sname, clean_ten=pair_metrics(t["clean"], t["clean"])["tenengrad"], deg_ten=pair_metrics(t["clean"], deg)["tenengrad"], **{f"deg_{k}": v for k, v in pair_metrics(t["clean"], deg).items() if k in ("psnr", "ssim")})
            for g in GAMMAS:
                out = base if g == 0 else modified_usm(base, t=T, lam=LAM, k_scale=g)
                m = pair_metrics(t["clean"], out)
                row[f"g{g}_psnr"], row[f"g{g}_ssim"], row[f"g{g}_ten"] = m["psnr"], m["ssim"], m["tenengrad"]
            rows.append(row)
    df = pd.DataFrame(rows)
    out = ROOT / "output" / "auto"
    df.to_csv(out / "ablation_gamma.csv", index=False)
    lines = ["# gamma ablation (held-out sources, n=%d images)\n" % len(df),
             "| gamma | PSNR | SSIM | sharpness (Tenengrad) / original |", "|---|---|---|---|"]
    for g in GAMMAS:
        lines.append(f"| {g} | {df[f'g{g}_psnr'].mean():.2f} | {df[f'g{g}_ssim'].mean():.4f} | {(df[f'g{g}_ten'] / df.clean_ten).median():.3f} |")
    lines.append(f"| (degraded) | {df.deg_psnr.mean():.2f} | {df.deg_ssim.mean():.4f} | {(df.deg_ten / df.clean_ten).median():.3f} |")
    (out / "ABLATION_GAMMA.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
