# Restoration + Modified Unsharp Masking Extension

This folder is the **domain-extension experiment** of the Aarthy & Keerthi (2025) modified unsharp masking method. The original paper sharpens already-blurred natural images from CSIQ / LIVE / TID2013 / KADID-10k. This extension asks a different question:

> If the input is degraded by salt-and-pepper noise, Gaussian noise, or Gaussian blur, does a restoration step *before* the paper's sharpener improve results — and does that benefit depend on the application domain?

The two domains are:

| Domain | Image type (kept consistent) |
|---|---|
| Medical | Frontal **chest X-ray** (grayscale radiograph) |
| Satellite | Optical remote-sensing RGB from **UC Merced** (USGS National Map, 0.3 m) |

The three degradations, used in both domains, match TID2013 categories #1, #6, and #8:

- additive Gaussian noise
- impulse / salt-and-pepper noise
- Gaussian blur

## Layout

```
extension_restoration_usm/
  STUDY.md                 literature-backed study of the 3 degradations
  collect_images.py        download public-domain clean images
  degradations.py          synthesize the 3 degradations (+ clean copies)
  restoration.py           median / NLM / Wiener
  sharpening_ext.py        practical modified USM (paper's k, input-side edges)
  metrics_eval.py          PSNR, SSIM, PLCC, SROCC, sharpness
  pipelines.py             Pipeline A vs Pipeline B
  visualize.py             5-panel visual analysis figures
  analyze.py               comparison table + answers to the analysis questions
  run_experiment.py        end-to-end runner
  data/{medical,satellite}/{clean,salt_pepper,gaussian_noise,blur}/
  output/{figures,panels,tables}/
```

## Pipelines

The paper's Fig. 2 extracts the edge mask from the **clean reference**. That is appropriate for their IQA-benchmark evaluation, but it would leak ground-truth edges into both pipelines here and hide the effect of restoration. For this extension the sharpener is therefore applied in the **practical / blind** form used at test time:

```
edge      = input − GaussianSmooth(input)
sharpened = input + k(t, λ) · edge
k         = |a2| + |a3|     (same combination as the parent implementation)
```

with the paper's reported operating point `t = 0.6`, `λ = 0`.

| Pipeline | Flow |
|---|---|
| **A** (baseline) | Degraded → Modified USM |
| **B** (proposed) | Degraded → Restoration → Modified USM with `k_eff = γ · k` |

Restoration is matched to the degradation (see `STUDY.md`):

| Degradation | Restoration |
|---|---|
| Salt-and-pepper | Median filter |
| Gaussian noise | Non-local means |
| Gaussian blur | Wiener deconvolution (known PSF, reflect-padded) + reduced `k` (`γ = 0.20`) |

After restoration the residual is already larger than on a degraded input, so Pipeline B applies a fraction `γ` of the paper's `k` (`γ = 0.12` after denoising, `γ = 0.20` after deblur). Pipeline A still uses the paper's full `k`.

## Dataset structure

```
Medical/
    clean/
    salt_pepper/
    gaussian_noise/
    blur/
Satellite/
    clean/
    salt_pepper/
    gaussian_noise/
    blur/
```

Clean images are collected; the three degradations are then synthesized at three severity levels so that every degraded image has a paired reference. That pairing is what makes PSNR / SSIM (and the MOS-proxy used for PLCC / SROCC) well-defined.

TID2013 is a general IQA set, not medical or satellite imagery. Phase 1 therefore **validates the methodology** by applying the same three TID2013-style distortions to the collected domain images (equivalent distortion types #1, #6, #8), rather than treating TID2013 itself as the medical/satellite test set.

## How to run

From the repository root, with the existing venv:

```bash
source venv/bin/activate
python extension_restoration_usm/run_experiment.py
```

This will, in order:

1. Download clean chest X-rays and UC Merced scenes (if `data/*/clean` is empty)
2. Synthesize salt-and-pepper, Gaussian noise, and Gaussian blur
3. Run Pipeline A and Pipeline B
4. Write metrics, comparison tables, 5-panel figures, and the analysis write-up

## Metrics

- **PSNR, SSIM** against the clean reference (full-reference; possible here because we keep paired clean images)
- **PLCC, SROCC** as in the paper (Eqs. 36–37): no-reference sharpness of the output vs. SSIM-to-clean as a MOS proxy
- Visual 5-panel strips: Clean → Degraded → Restored → Sharpening-only → Restoration+Sharpening
