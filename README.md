# Modified Unsharp Masking via Gregory-Coefficient Bounds

Implementation of:

> B. Aarthy, B. Srutha Keerthi, "Enhancing Image Sharpness by Modified Unsharp
> Masking Using Coefficient Bounds Obtained for a Subclass of Analytic
> Functions", *Arabian Journal for Science and Engineering* (2025).
> https://doi.org/10.1007/s13369-025-10469-3

## Layout

- `gregory_usm/coefficients.py` — Gregory coefficients (Eq. 9, via `sympy` series
  expansion), `u_n = (1-t^n)/(1-t)`, and the sharp bounds `|a2|` (Eq. 32) and
  `|a3|` (Eq. 34) from Theorem 1.
- `gregory_usm/sharpening.py` — Gaussian smoothing (Eq. 35) and the modified
  unsharp masking pipeline (Fig. 2 / Sect. 4.3): `edge = original - smooth(original)`,
  `sharpened = blurred + k * edge`, `k = |a2| + |a3|`.
- `gregory_usm/metrics.py` — PLCC (Eq. 36) and SROCC (Eq. 37), implemented
  directly from the paper's formulas.
- `demo.py` — end-to-end run on a small image set, reproducing the paper's
  "blur at 5 severity levels" experimental setup (Figs. 7-9), with PSNR/SSIM
  sanity metrics and output images in `output/`.

## Implementation decisions where the paper is ambiguous

1. **Combining `|a2|` and `|a3|` into one sharpening factor.** Theorem 1
   yields two separate bounds, but Fig. 2 shows a single "Coefficient
   Bounds" block multiplying the edge image, and the text never gives the
   combination formula. **Decision (confirmed with you): `k = |a2| + |a3|`.**
   At the paper's reported optimum `t = 0.6, λ = 0`: `|a2| ≈ 0.804`,
   `|a3| ≈ 2.043`, so `k ≈ 2.847`.
2. **Gaussian smoothing `σ`.** Eq. 35 gives the kernel formula but the paper
   never states a numeric `σ` (MATLAB's `imgaussfilt` default was presumably
   used but isn't stated). Exposed as a parameter, default `σ = 2.0`.
3. **Which image is smoothed / where the edge comes from.** Sect. 4.1 and
   Fig. 2 are explicit that the *original (reference)* image is smoothed to
   produce the edge mask, which is then added to the *blurred (distorted)*
   image — i.e. this method assumes access to a clean reference, matching
   how it's evaluated against full-reference IQA datasets. This was
   implemented literally, not reinterpreted as blind/no-reference sharpening.

## Dataset note

CSIQ and LIVE are gated behind registration forms; TID2013 (~900 MB) and
KADID-10k (~GBs) are only distributed as single archives with no per-file
HTTP access, so a true partial download isn't possible for them. As a
stand-in, `data/reference/` contains 3 public-domain images from the Kodak
test suite, and `demo.py` synthesizes the same "Gaussian blur at 5 levels"
distortion category these benchmark datasets use for their blur subsets.
This validates the pipeline end-to-end but does **not** reproduce Table 1 /
Table 2 (PLCC/SROCC against real human MOS scores) — that requires the
actual datasets with their subjective-score files. `gregory_usm/metrics.py`
is ready to use once you have `(algorithm_score, mos_score)` pairs.

## Results (this demo set)

Fixed `k` improves SSIM in 14/15 blur×image combinations (better structural
recovery of edges/texture) but can reduce PSNR at *mild* blur levels, since
the correction strength doesn't adapt to blur severity — visible as edge
halos in `output/*_blur1_sharpened.png`. This matches the paper's own noted
oversharpening risk at parameter values tuned for stronger blur.

## Extension: restoration before sharpening

`extension_restoration_usm/` applies the same modified unsharp masking to **chest X-rays** and **UC Merced** remote-sensing scenes after three TID2013-style degradations (salt-and-pepper, Gaussian noise, Gaussian blur). Pipeline A sharpens the degraded image directly; Pipeline B restores first, then sharpens.

```bash
source venv/bin/activate
python extension_restoration_usm/run_experiment.py
```

See `extension_restoration_usm/README.md` and `extension_restoration_usm/output/ANALYSIS.md`.
