# Analysis of the restoration + modified-USM extension

Paper starting point: `t = 0.6`, `λ = 0`, `k = |a2| + |a3|`.
Sharpener: practical / blind modified unsharp masking (edges from the image being processed).

## Comparison table

| Domain | Degradation | Sharpening only (PSNR / SSIM) | Restoration + Sharpening (PSNR / SSIM) | Improvement (ΔPSNR / ΔSSIM) |
|---|---|---|---|---|
| Medical | Blur | 33.20 / 0.8844 | 33.95 / 0.8984 | +0.75 / +0.0139 |
| Medical | Gaussian Noise | 12.54 / 0.0733 | 32.31 / 0.7547 | +19.77 / +0.6814 |
| Medical | Salt & Pepper | 17.33 / 0.2562 | 36.23 / 0.9393 | +18.90 / +0.6831 |
| Satellite | Blur | 26.27 / 0.6906 | 27.42 / 0.7113 | +1.15 / +0.0207 |
| Satellite | Gaussian Noise | 12.51 / 0.2348 | 28.41 / 0.7794 | +15.89 / +0.5446 |
| Satellite | Salt & Pepper | 14.88 / 0.3864 | 29.57 / 0.8001 | +14.68 / +0.4137 |

## PLCC / SROCC

Algorithm score = Laplacian variance (no-reference sharpness).
MOS proxy = SSIM against the clean reference.

| Domain | Degradation | Pipeline | PLCC | SROCC |
|---|---|---|---|---|
| Medical | Salt & Pepper | A (sharpen only) | -0.932 | -0.822 |
| Medical | Salt & Pepper | B (restore + sharpen) | 0.655 | 0.540 |
| Medical | Gaussian Noise | A (sharpen only) | -0.888 | -0.905 |
| Medical | Gaussian Noise | B (restore + sharpen) | -0.924 | -0.860 |
| Medical | Blur | A (sharpen only) | 0.661 | 0.744 |
| Medical | Blur | B (restore + sharpen) | 0.780 | 0.870 |
| Satellite | Salt & Pepper | A (sharpen only) | -0.764 | -0.734 |
| Satellite | Salt & Pepper | B (restore + sharpen) | 0.426 | 0.323 |
| Satellite | Gaussian Noise | A (sharpen only) | -0.442 | -0.470 |
| Satellite | Gaussian Noise | B (restore + sharpen) | 0.598 | 0.746 |
| Satellite | Blur | A (sharpen only) | 0.491 | 0.732 |
| Satellite | Blur | B (restore + sharpen) | 0.502 | 0.577 |

Higher PLCC/SROCC means “looks sharp” agrees with “is actually closer to the clean image”.
Noise-amplifying sharpening inflates Laplacian variance while hurting SSIM, which lowers these correlations.

## Answers to the analysis questions

### Does preprocessing improve sharpening performance?

Yes, on average. Restoration + sharpening (Pipeline B) improves SSIM over sharpening-only (Pipeline A) in
6/6 domain×degradation cells.
Mean ΔSSIM is +0.3929; mean ΔPSNR is +11.86 dB.

### Which restoration method works best for each degradation?

Judged by mean ΔSSIM of B versus A:

- Salt-and-pepper / median filter: ΔSSIM = +0.5484
- Gaussian noise / non-local means: ΔSSIM = +0.6130
- Gaussian blur / Wiener deconvolution: ΔSSIM = +0.0173

The largest restoration benefit is for **Gaussian Noise**, which is the expected result:
unsharp masking treats impulses and grain as edges, so removing them first stops the sharpener from amplifying them.
For blur, padded Wiener restores attenuated frequencies; a reduced post-restore `k` then crisps edges without re-ringing.

### Does the improvement differ between medical and satellite images?

Yes. Mean ΔSSIM is +0.4595 on chest X-rays and +0.3263 on UC Merced remote-sensing scenes.
Satellite scenes carry denser high-frequency texture (fields, urban fabric, coastlines), so leftover noise after denoising is more visible once sharpened.
Chest X-rays have large smooth regions (heart shadow, abdomen); impulse specks and mediastinal halos are the more obvious failure modes of Pipeline A, and median filtering removes them cheaply.

### Which degradation causes the biggest problem for sharpening?

Sharpening-only is worst (lowest mean SSIM of Pipeline A) for **Gaussian Noise** on the medical set (SSIM 0.0733).
Gaussian noise corrupts *every* pixel, so the USM residual is almost entirely grain; impulse noise is also hostile because salt/pepper pixels are maximal-contrast “edges”, but at 2–10% density most pixels are still clean.
Mild Gaussian blur is the native use-case of USM, so it is the least hostile of the three — which is why the original paper could report good visual results on blur-only benchmarks.

### Does restoration reduce the artifacts / noise introduced by sharpening?

Yes. The 5-panel figures in `output/panels/` show:

- Salt-and-pepper: Pipeline A turns specks into larger clipped blobs with halos; Pipeline B removes specks then sharpens anatomy / field boundaries.
- Gaussian noise: Pipeline A looks grainy, especially in lung fields and open water; Pipeline B is cleaner, with less false texture.
- Blur: Pipeline A steepens ramps; Pipeline B (padded Wiener, then a reduced `k`) recovers thinner edges with less border ringing.

### Does the optimal sharpening configuration from the paper remain effective for both domains?

The paper reports `t = 0.6`, `λ = 0` as the best balance on CSIQ/LIVE/TID2013/KADID blur experiments.
A small sweep of `t ∈ {0.4, 0.6, 0.8}` at `λ = 0` on these domain images gives: mean Pipeline-B SSIM by t: t=0.4 → 0.6789, t=0.6 → 0.6828, t=0.8 → 0.6810. Best t on these domain images is 0.6 (matches the paper).
The paper's `t = 0.6` remains a good default for the coefficient formula in both domains. Pipeline B additionally scales that `k` by `γ < 1` after restoration; changing `t` and `γ` at once is redundant. Keep `λ = 0`.

## Method notes

- Edges are extracted from the *input being sharpened*, not from the clean reference. Using the paper's Fig. 2 protocol here would leak ground-truth edges into both pipelines and hide the restoration effect.
- TID2013 is a general IQA set. Phase 1 of this folder therefore uses the same three TID2013 distortion *types* (#1 Gaussian noise, #6 impulse noise, #8 Gaussian blur) synthesised on the domain images, rather than claiming TID2013 itself is medical or satellite data.
- Full-reference PSNR/SSIM are available because every degraded image is paired with its clean source. PLCC/SROCC use SSIM-to-clean as a MOS proxy because these public CXR / UC Merced files have no human MOS.

Pipeline B improved SSIM in every domain × degradation cell.
