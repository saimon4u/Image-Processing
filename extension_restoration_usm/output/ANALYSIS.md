# Analysis of the restoration + modified-USM extension

Paper starting point: `t = 0.6`, `λ = 0`, `k = |a2| + |a3|`.
Sharpener: practical / blind modified unsharp masking (edges from the image being processed).

## Comparison table

| Domain | Degradation | Sharpening only (PSNR / SSIM) | Restoration + Sharpening (PSNR / SSIM) | Improvement (ΔPSNR / ΔSSIM) |
|---|---|---|---|---|
| Medical | Blur | 33.20 / 0.8844 | 23.12 / 0.7812 | -10.08 / -0.1032 |
| Medical | Gaussian Noise | 12.54 / 0.0733 | 24.45 / 0.4350 | +11.91 / +0.3617 |
| Medical | Salt & Pepper | 17.33 / 0.2562 | 28.83 / 0.8341 | +11.50 / +0.5778 |
| Satellite | Blur | 26.27 / 0.6906 | 21.20 / 0.6159 | -5.08 / -0.0748 |
| Satellite | Gaussian Noise | 12.51 / 0.2348 | 20.85 / 0.6347 | +8.34 / +0.3999 |
| Satellite | Salt & Pepper | 14.88 / 0.3864 | 22.65 / 0.7102 | +7.77 / +0.3237 |

## PLCC / SROCC

Algorithm score = Laplacian variance (no-reference sharpness).
MOS proxy = SSIM against the clean reference.

| Domain | Degradation | Pipeline | PLCC | SROCC |
|---|---|---|---|---|
| Medical | Salt & Pepper | A (sharpen only) | -0.932 | -0.822 |
| Medical | Salt & Pepper | B (restore + sharpen) | -0.514 | -0.443 |
| Medical | Gaussian Noise | A (sharpen only) | -0.888 | -0.905 |
| Medical | Gaussian Noise | B (restore + sharpen) | -0.939 | -0.874 |
| Medical | Blur | A (sharpen only) | 0.661 | 0.744 |
| Medical | Blur | B (restore + sharpen) | -0.360 | -0.379 |
| Satellite | Salt & Pepper | A (sharpen only) | -0.764 | -0.734 |
| Satellite | Salt & Pepper | B (restore + sharpen) | 0.079 | -0.084 |
| Satellite | Gaussian Noise | A (sharpen only) | -0.442 | -0.470 |
| Satellite | Gaussian Noise | B (restore + sharpen) | -0.345 | 0.148 |
| Satellite | Blur | A (sharpen only) | 0.491 | 0.732 |
| Satellite | Blur | B (restore + sharpen) | 0.363 | 0.226 |

Higher PLCC/SROCC means “looks sharp” agrees with “is actually closer to the clean image”.
Noise-amplifying sharpening inflates Laplacian variance while hurting SSIM, which lowers these correlations.

## Answers to the analysis questions

### Does preprocessing improve sharpening performance?

Yes, on average. Restoration + sharpening (Pipeline B) improves SSIM over sharpening-only (Pipeline A) in
4/6 domain×degradation cells.
Mean ΔSSIM is +0.2475; mean ΔPSNR is +4.06 dB.

### Which restoration method works best for each degradation?

Judged by mean ΔSSIM of B versus A:

- Salt-and-pepper / median filter: ΔSSIM = +0.4508
- Gaussian noise / non-local means: ΔSSIM = +0.3808
- Gaussian blur / Wiener deconvolution: ΔSSIM = -0.0890

The largest restoration benefit is for **Salt & Pepper**, which is the expected result:
unsharp masking treats impulses and grain as edges, so removing them first stops the sharpener from amplifying them.
For blur, unsharp masking is already a deblurring heuristic, so Wiener helps less (and can overshoot if `K` is too small).

### Does the improvement differ between medical and satellite images?

Yes. Mean ΔSSIM is +0.2788 on chest X-rays and +0.2163 on UC Merced remote-sensing scenes.
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
- Blur: Pipeline A steepens ramps and can halo; Pipeline B (Wiener then USM) recovers thinner edges but can still overshoot at the strongest blur level.

### Does the optimal sharpening configuration from the paper remain effective for both domains?

The paper reports `t = 0.6`, `λ = 0` as the best balance on CSIQ/LIVE/TID2013/KADID blur experiments.
A small sweep of `t ∈ {0.4, 0.6, 0.8}` at `λ = 0` on these domain images gives: mean Pipeline-B SSIM by t: t=0.4 → 0.6521, t=0.6 → 0.6048, t=0.8 → 0.4126. Best t on these domain images is 0.4 (differs from the paper's t = 0.6).
The paper's `t = 0.6` was tuned on *blur-only* natural IQA images. On noisy medical and remote-sensing inputs a smaller `t` (weaker `k`) is safer after restoration. Keep `λ = 0`. For blur-only images, `t = 0.6` remains competitive.

## Method notes

- Edges are extracted from the *input being sharpened*, not from the clean reference. Using the paper's Fig. 2 protocol here would leak ground-truth edges into both pipelines and hide the restoration effect.
- TID2013 is a general IQA set. Phase 1 of this folder therefore uses the same three TID2013 distortion *types* (#1 Gaussian noise, #6 impulse noise, #8 Gaussian blur) synthesised on the domain images, rather than claiming TID2013 itself is medical or satellite data.
- Full-reference PSNR/SSIM are available because every degraded image is paired with its clean source. PLCC/SROCC use SSIM-to-clean as a MOS proxy because these public CXR / UC Merced files have no human MOS.

Pipeline B was not uniformly better: medical/blur, satellite/blur.
