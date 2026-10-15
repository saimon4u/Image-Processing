# Blind auto-restoration results

2226 degraded images (tiles from 114 source X-ray / satellite images, 7 scenarios). The pipeline never saw the clean image or the degradation parameters.

## 1. Detection accuracy (which filter is needed?)

| Degradation | Accuracy | Recall (present) | False alarm (absent) |
|---|---|---|---|
| Salt-and-pepper | 100.0% | 100.0% | 0.0% |
| Gaussian noise | 98.1% | 100.0% | 4.4% |
| Blur | 87.6% | 96.5% | 24.2% |

Exact combination correct (all three decisions right): **85.7%**

Blur sigma estimate MAE (blurred images): 0.49 px; noise sigma MAE (noisy images): 0.003

## 2. Quality vs clean original (mean over all degraded images)

| Method | PSNR (dB) | SSIM | PSNR gain vs degraded | SSIM gain vs degraded | MSE reduction |
|---|---|---|---|---|---|
| degraded | 20.32 | 0.3318 | +0.00 dB (+0.0%) | +0.0000 (+0.0%) | 0.0% |
| usm_only | 16.00 | 0.2507 | -4.32 dB (-21.3%) | -0.0811 (-24.4%) | -327.1% |
| fixed_chain | 26.05 | 0.6426 | +5.73 dB (+28.2%) | +0.3108 (+93.7%) | 42.5% |
| auto | 29.62 | 0.7701 | +9.30 dB (+45.8%) | +0.4383 (+132.1%) | 67.2% |
| oracle | 30.04 | 0.7724 | +9.73 dB (+47.9%) | +0.4406 (+132.8%) | 78.2% |

## Improvement by scenario (auto pipeline)

| scenario | n | PSNR degraded | PSNR auto | gain dB | SSIM degraded | SSIM auto | SSIM improvement | usm_only SSIM | fixed_chain SSIM |
|---|---|---|---|---|---|---|---|---|---|
| clean | 0 | nan | nan | +nan | nan | nan | +nan% | nan | nan |
| sp | 318 | 18.05 | 33.35 | +15.30 | 0.3317 | 0.9078 | +173.7% | 0.2948 | 0.7156 |
| gn | 318 | 23.32 | 30.70 | +7.38 | 0.4191 | 0.7944 | +89.5% | 0.1501 | 0.5905 |
| blur | 318 | 29.32 | 29.58 | +0.26 | 0.7646 | 0.8070 | +5.5% | 0.8245 | 0.7596 |
| blur+gn | 318 | 21.48 | 27.81 | +6.33 | 0.2630 | 0.6799 | +158.5% | 0.0748 | 0.5678 |
| blur+sp | 318 | 17.36 | 28.34 | +10.98 | 0.2121 | 0.7556 | +256.2% | 0.2284 | 0.7602 |
| gn+sp | 318 | 16.57 | 30.03 | +13.46 | 0.2113 | 0.7806 | +269.4% | 0.1233 | 0.5637 |
| blur+gn+sp | 318 | 16.14 | 27.54 | +11.40 | 0.1206 | 0.6658 | +451.9% | 0.0589 | 0.5409 |

## Improvement by domain (auto pipeline)

| domain | n | PSNR degraded | PSNR auto | gain dB | SSIM degraded | SSIM auto | SSIM improvement | usm_only SSIM | fixed_chain SSIM |
|---|---|---|---|---|---|---|---|---|---|
| medical | 1260 | 21.05 | 31.39 | +10.34 | 0.2955 | 0.7952 | +169.1% | 0.2141 | 0.6875 |
| satellite | 966 | 19.37 | 27.31 | +7.95 | 0.3792 | 0.7375 | +94.5% | 0.2984 | 0.5841 |

## Do-no-harm check: already-clean inputs

318 clean images. Left completely untouched: 0.0%. Mean SSIM vs original after auto pipeline: 0.9639 (fixed chain: 0.7186, USM only: 0.6943).


Images where auto restoration made PSNR *worse* than the degraded input: 101/2226 (4.5%).
