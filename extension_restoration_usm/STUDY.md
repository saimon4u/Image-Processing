# Study of the three degradations and the chosen restorations

This note covers items 4 and 5 of the experiment brief. It is deliberately limited to the three degradations used in both domains: salt-and-pepper (impulse) noise, additive Gaussian noise, and Gaussian blur. These are TID2013 types #6, #1, and #8.

The parent paper (Aarthy & Keerthi, 2025) applies modified unsharp masking to *blurred* natural images. Unsharp masking extracts a high-frequency residual and adds it back. Anything in that residual that is *not* a true edge — impulse spikes, Gaussian grain, ringing — is amplified. That is the reason a restoration step is inserted before sharpening in this extension.

The paper's reported operating point `t = 0.6`, `λ = 0` is used as the starting sharpening configuration in both domains.

---

## 1. Salt-and-pepper / impulse noise

### How it affects the image

Impulse noise replaces a random subset of pixels with the extreme intensities of the range (salt = 1, pepper = 0). It is not additive: the original value at a corrupted pixel is lost. On a chest radiograph this looks like bright and dark specks on lung fields and ribs; on a UC Merced remote-sensing scene it looks like isolated dead/hot pixels, which do occur in real sensors but are usually already calibrated out.

### Edges and fine details

True edges are mostly intact at low density because most pixels are untouched. At higher density, specks sit on top of edges and fine texture, so a gradient or Laplacian can no longer tell a rib boundary from a salt pixel. That is fatal for unsharp masking: the residual `image − smooth(image)` treats impulses as the highest-contrast "edges" in the picture.

### Why sharpening a salt-and-pepper image is a poor idea

The modified USM step is

```
sharpened = image + k · (image − GaussianSmooth(image))
```

with `k ≈ 2.85` at `t = 0.6`, `λ = 0`. An isolated 0 or 1 pixel is a huge local deviation from the Gaussian-smoothed neighbourhood, so it is multiplied by `k` and driven even further into clipping. The result is *more* specks, often with a dark/bright halo from the smoother. Medical structures (vessels, nodule margins) and satellite linear features (roads, field boundaries) are then competing with amplified impulses.

### Restoration choice: median filter

A median filter replaces each pixel with the median of a `w×w` window (Tukey, 1977; Gonzalez & Woods, *Digital Image Processing*). For impulse noise this is the textbook method:

- Impulses are outliers. The median of a window that is still majority-clean equals a clean neighbour, so the spike is removed rather than averaged in.
- A mean or Gaussian filter *spreads* each impulse into a blob, which then looks like a real blob-edge to the sharpener.
- Adaptive median filters (Hwang & Haddad, 1995) help at very high densities; at the densities used here (2–10%) a fixed 3×3 or 5×5 median is sufficient and does not over-smooth uncorrupted pixels as aggressively as a large adaptive window.

**Not chosen:** Gaussian smoothing (blurs edges that we later want to sharpen), non-local means (designed for additive Gaussian noise, not replacement impulses).

---

## 2. Additive Gaussian noise

### How it affects the image

Every pixel is perturbed by independent draws from `N(0, σ²)`. Unlike impulse noise, no pixel is completely destroyed, but *every* pixel is wrong. On X-rays this resembles quantum/electronic noise in low-dose acquisitions; on optical satellite images it resembles sensor/read noise and compression grain.

### Edges and fine details

Fine texture (lung parenchyma, crop rows, urban fabric) is the first casualty: the noise floor rises until weak edges fall below it. Strong edges (diaphragm, coastline) remain detectable but their gradient estimates become noisy, so edge maps look hairy.

### Why sharpening a Gaussian-noisy image is a poor idea

Unsharp masking is a high-frequency boost. Additive white Gaussian noise is already broadband; boosting the residual amplifies grain in smooth regions (heart shadow, open water, desert) and produces the "speckled edges" the parent paper's introduction warns about. A large `k` makes this worse, which is exactly why a mathematically bounded `k` is not enough *by itself* when the input is noisy rather than merely soft.

### Restoration choice: non-local means (NLM)

Non-local means (Buades, Coll & Morel, 2005) estimates each pixel as a weighted average of *similar patches* anywhere in a search window, not just of spatial neighbours. It is derived under an additive white Gaussian noise model and is edge-preserving: a rib or a shoreline patch matches other rib/shoreline patches, so the edge is averaged along itself rather than across it.

**Why not a Gaussian filter?** A Gaussian denoiser *is* a blur. Running it and then unsharp-masking largely undoes the denoise, and the leftover is a softer, still somewhat noisy image. That fights the goal of the pipeline.

**Why not BM3D?** BM3D (Dabov et al., 2007) is often slightly better on AWGN, but it is heavier, has more hyperparameters, and is not in the already-pinned `scikit-image` stack. NLM is the standard edge-preserving AWGN baseline and is enough to test the restoration-before-sharpening hypothesis.

The NLM strength `h` is set from a robust noise-scale estimate (`skimage.restoration.estimate_sigma`) so the same code works at all three σ levels.

---

## 3. Gaussian blur

### How it affects the image

Convolution with a Gaussian PSF attenuates high spatial frequencies. Edges become ramps; small structures (interstitial markings, small fields, ships) lose contrast and can disappear once their scale is below `σ`.

### Edges and fine details

This is the degradation unsharp masking was invented for. The residual `image − smooth(image)` still contains a (weakened) edge, and adding it back steepens ramps. At mild blur that can look good. At stronger blur the residual is a wide, low-amplitude ridge, and scaling it by `k` produces overshoot / halo rather than a recovered thin edge.

### Why sharpening a blurred image can still be poor (especially in these domains)

- **Halos** around high-contrast boundaries: the mediastinum on a chest X-ray, a bright rooftop against dark water in a harbour scene. In diagnosis and in mapping, a halo is a false structure.
- **Cannot invent lost frequencies.** Once a 2-pixel vessel or a 3-pixel road has been integrated away by a large Gaussian, USM cannot uniquely put it back; it can only paint a wider edge.
- **Noise in the blurred image** (even mild) is still high-frequency relative to the remaining edges and gets boosted.

### Restoration choice: Wiener deconvolution

Wiener deconvolution (Wiener, 1949; Gonzalez & Woods) inverts the known (or estimated) PSF in the Fourier domain with a regularised inverse

```
W(f) = H*(f) / (|H(f)|² + K)
```

where `H` is the Gaussian blur OTF and `K` is a noise-to-signal parameter. Because this experiment *synthesises* the blur, the PSF is known (non-blind). That is the statistically correct restoration for Gaussian blur plus mild noise, and it actually attempts to restore attenuated frequencies instead of only steepening ramps.

FFT deconvolution treats the image as periodic. Without padding, that wraps opposite borders into each other and leaves bright/dark bands; the following USM step then amplifies those bands into the halos that made Pipeline B lose to the paper on blur. The implementation therefore **reflect-pads by ~4σ** (the Gaussian kernel support) before Wiener and crops back afterwards.

**Why not Richardson–Lucy?** RL is the Poisson / photon-count ML iteration. Chest X-rays and 8-bit RGB remote-sensing products here are treated as Gaussian-blurred intensity images, not Poisson photon counts.

**Why not USM alone as the "restoration"?** That would make Pipeline A and Pipeline B identical for blur. Wiener is a genuine alternative model; USM is then a *subsequent* edge-emphasis step, which is exactly the hypothesis being tested: restore, then sharpen.

In a deployed system the PSF would be estimated (e.g. from knife-edge or metadata). The experiment records the true `σ` in a manifest so the comparison is of methods, not of kernel-estimation error.

---

## 4. Domain-specific reasons the same three degradations matter

| | Chest X-ray | UC Merced optical RS |
|---|---|---|
| What edges mean | Anatomy: ribs, vessels, diaphragm, device lines | Geography: coast, fields, roads, built-up texture |
| Cost of amplified noise | Can mimic microcalcification / nodule / pneumothorax line | Can mimic small buildings, ships, burn scars |
| Cost of halo / overshoot | False contour next to the heart or a fracture | False shoreline / field boundary in a classification map |
| Typical native look | Smooth gray fields, few saturated pixels | Textured, colourful, many small high-contrast objects |

So the *same* restoration+sharpening pipeline can help both domains and still show a **domain-dependent** gain: satellite scenes have more high-frequency texture, so residual noise after a weak denoise is more visible once sharpened; X-rays have large smooth regions, so impulse amplification and halos around the mediastinum are the more obvious failure modes.

---

## 5. Pipeline summary

```
Pipeline A (paper baseline, applied to degraded inputs)
    Degraded  →  Modified USM(t=0.6, λ=0, full k)  →  Output

Pipeline B (this extension)
    Degraded  →  Restoration  →  Modified USM(t=0.6, λ=0, k_eff = γ·k)  →  Output
```

The comparison of A vs B, on both domains, for all three degradations, is the core experiment.

---

## 6. Why the first Pipeline B lost on blur — and the fix

On the first run, Pipeline B *lost* to the paper on both medical and satellite blur (ΔSSIM −0.10 and −0.07) even though it won on both noise types. Two stacked bugs, not a domain effect:

1. **Wiener border wrap-around.** Restoration-only SSIM was already below sharpening-only, and the 5-panel figures showed ringing at the frame. Reflect padding removes that; padded Wiener-only then *beats* the paper on blur.
2. **Full paper `k` after restoration.** Even on noise, restoration-only SSIM was far above restore-then-full-USM (e.g. medical Gaussian 0.80 vs 0.44). The paper's `k ≈ 2.85` at `t = 0.6` was calibrated to add edges to a *degraded* image. After median / NLM / Wiener the residual `image − smooth(image)` is already larger, so the same `k` double-counts edge energy and reintroduces grain and halos.

Pipeline B therefore uses a restoration-aware gain `k_eff = γ · k(t, λ)` with `γ = 0.12` after denoising and `γ = 0.20` after deblur. The coefficient-bound formula is unchanged; only the amount applied after a restored residual is reduced. Pipeline A still uses the paper's full `k`.
