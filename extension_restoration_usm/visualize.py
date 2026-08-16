"""Five-panel visual analysis figures and a comparison heatmap."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import numpy as np

from config import FIG_DIR, PANEL_DIR


def _show(ax, image: np.ndarray, title: str) -> None:
    ax.set_title(title, fontsize=9)
    ax.axis("off")
    if image.ndim == 2:
        ax.imshow(image, cmap="gray", vmin=0.0, vmax=1.0)
    else:
        ax.imshow(np.clip(image, 0.0, 1.0), vmin=0.0, vmax=1.0)


def save_five_panel(
    clean: np.ndarray,
    degraded: np.ndarray,
    restored: np.ndarray,
    sharp_only: np.ndarray,
    restore_then_sharp: np.ndarray,
    title: str,
    dest: Path,
) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 5, figsize=(14, 3.2))
    _show(axes[0], clean, "Clean")
    _show(axes[1], degraded, "Degraded")
    _show(axes[2], restored, "Restored")
    _show(axes[3], sharp_only, "Sharpening only")
    _show(axes[4], restore_then_sharp, "Restore + sharpen")
    fig.suptitle(title, fontsize=11)
    fig.tight_layout()
    fig.savefig(dest, dpi=140, bbox_inches="tight")
    plt.close(fig)


def save_heatmap(table_rows: list[dict], dest: Path) -> None:
    """Heatmap of mean SSIM improvement (Pipeline B − Pipeline A)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    domains = ["medical", "satellite"]
    degradations = ["salt_pepper", "gaussian_noise", "blur"]
    labels = ["Salt & pepper", "Gaussian noise", "Gaussian blur"]
    grid = np.zeros((len(domains), len(degradations)))
    for i, domain in enumerate(domains):
        for j, deg in enumerate(degradations):
            match = [
                r for r in table_rows if r["domain"] == domain and r["degradation"] == deg
            ]
            grid[i, j] = match[0]["delta_ssim"] if match else 0.0

    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    span = max(0.05, float(np.max(np.abs(grid))))
    norm = TwoSlopeNorm(vmin=-span, vcenter=0.0, vmax=span)
    im = ax.imshow(grid, cmap="RdYlGn", norm=norm)
    ax.set_xticks(range(len(labels)), labels)
    ax.set_yticks(range(len(domains)), ["Medical (CXR)", "Satellite (UC Merced)"])
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            ax.text(j, i, f"{grid[i, j]:+.3f}", ha="center", va="center", fontsize=10)
    ax.set_title("SSIM improvement of restoration + sharpening over sharpening only")
    fig.colorbar(im, ax=ax, fraction=0.046, label="Δ SSIM (B − A)")
    fig.tight_layout()
    fig.savefig(dest, dpi=140, bbox_inches="tight")
    plt.close(fig)
