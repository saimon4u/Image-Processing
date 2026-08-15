"""Download public-domain clean images for the two domains.

Medical   : frontal chest radiographs (PA/AP X-ray), grayscale.
Satellite : optical remote-sensing scenes from the UC Merced Land Use set
            (USGS National Map urban imagery, 0.3 m RGB).

Attribution is written to data/SOURCES.md.
"""
from __future__ import annotations

import io
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from PIL import Image

from config import DATA_DIR, MAX_SIDE, N_CLEAN_IMAGES, ROOT

USER_AGENT = (
    "ImageProcessingResearch/1.0 "
    "(academic restoration-sharpening experiment; local coursework)"
)

# Frontal chest X-rays only (PA/AP). GitHub first — Wikimedia rate-limits bulk fetch.
MEDICAL_URLS = [
    (
        "cxr_github_01.jpeg",
        "https://raw.githubusercontent.com/ieee8023/covid-chestxray-dataset/master/images/auntminnie-a-2020_01_28_23_51_6665_2020_01_28_Vietnam_coronavirus.jpeg",
        "ieee8023/covid-chestxray-dataset, frontal CXR",
    ),
    (
        "cxr_github_02.jpeg",
        "https://raw.githubusercontent.com/ieee8023/covid-chestxray-dataset/master/images/nejmoa2001191_f1-PA.jpeg",
        "ieee8023/covid-chestxray-dataset, PA CXR",
    ),
    (
        "cxr_github_03.jpeg",
        "https://raw.githubusercontent.com/ieee8023/covid-chestxray-dataset/master/images/lancet-case2a.jpg",
        "ieee8023/covid-chestxray-dataset, frontal CXR",
    ),
    (
        "cxr_github_04.jpg",
        "https://raw.githubusercontent.com/ieee8023/covid-chestxray-dataset/master/images/ryct.2020200028.fig1a.jpeg",
        "ieee8023/covid-chestxray-dataset, frontal CXR",
    ),
    (
        "cxr_github_05.jpg",
        "https://raw.githubusercontent.com/ieee8023/covid-chestxray-dataset/master/images/covid-19-pneumonia-7-PA.jpg",
        "ieee8023/covid-chestxray-dataset, PA CXR",
    ),
    (
        "cxr_github_06.jpeg",
        "https://raw.githubusercontent.com/ieee8023/covid-chestxray-dataset/master/images/nejmoa2001191_f3-PA.jpeg",
        "ieee8023/covid-chestxray-dataset, PA CXR",
    ),
    (
        "cxr_github_07.png",
        "https://raw.githubusercontent.com/ieee8023/covid-chestxray-dataset/master/images/chlamydia-pneumonia-PA.png",
        "ieee8023/covid-chestxray-dataset, PA CXR",
    ),
    (
        "cxr_github_08.jpg",
        "https://raw.githubusercontent.com/ieee8023/covid-chestxray-dataset/master/images/covid-19-pneumonia-30-PA.jpg",
        "ieee8023/covid-chestxray-dataset, PA CXR",
    ),
]

# One remote-sensing dataset, one image type: 0.3 m optical RGB from USGS National Map.
UCMERCED_ZIP = (
    "https://huggingface.co/datasets/torchgeo/ucmerced/resolve/"
    "7c5ef3454d9b1cccfa7ccde0c01fc8f00a45909a/UCMerced_LandUse.zip"
)
UCMERCED_MEMBERS = [
    ("ucmerced_agricultural.png", "UCMerced_LandUse/Images/agricultural/agricultural00.tif",
     "UC Merced Land Use / USGS National Map, agricultural"),
    ("ucmerced_beach.png", "UCMerced_LandUse/Images/beach/beach00.tif",
     "UC Merced Land Use / USGS National Map, beach"),
    ("ucmerced_buildings.png", "UCMerced_LandUse/Images/buildings/buildings00.tif",
     "UC Merced Land Use / USGS National Map, buildings"),
    ("ucmerced_forest.png", "UCMerced_LandUse/Images/forest/forest00.tif",
     "UC Merced Land Use / USGS National Map, forest"),
    ("ucmerced_harbor.png", "UCMerced_LandUse/Images/harbor/harbor00.tif",
     "UC Merced Land Use / USGS National Map, harbor"),
    ("ucmerced_river.png", "UCMerced_LandUse/Images/river/river00.tif",
     "UC Merced Land Use / USGS National Map, river"),
]

# Fallback: NASA Blue Marble true-color (MODIS) if the UC Merced zip is unavailable.
NASA_FALLBACK = [
    (
        "nasa_land_west.jpg",
        "https://eoimages.gsfc.nasa.gov/images/imagerecords/57000/57723/globe_west_2048.jpg",
        "NASA Blue Marble / MODIS true-color, Western Hemisphere",
    ),
    (
        "nasa_land_topo.jpg",
        "https://eoimages.gsfc.nasa.gov/images/imagerecords/57000/57752/land_shallow_topo_2048.jpg",
        "NASA Blue Marble / MODIS true-color with topography",
    ),
]


def _download(url: str, timeout: int = 180) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _download_to_file(url: str, dest: Path, timeout: int = 300) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp, dest.open("wb") as out:
        total = resp.headers.get("Content-Length")
        total_n = int(total) if total and total.isdigit() else None
        copied = 0
        while True:
            chunk = resp.read(1024 * 256)
            if not chunk:
                break
            out.write(chunk)
            copied += len(chunk)
            if total_n:
                pct = 100.0 * copied / total_n
                print(f"\r  downloading {copied / 1e6:.1f}/{total_n / 1e6:.1f} MB ({pct:.0f}%)", end="", flush=True)
            else:
                print(f"\r  downloading {copied / 1e6:.1f} MB", end="", flush=True)
        print()


def _resize_max_side(img: Image.Image, max_side: int) -> Image.Image:
    w, h = img.size
    longest = max(w, h)
    if longest <= max_side:
        return img
    scale = max_side / float(longest)
    new_size = (max(1, int(round(w * scale))), max(1, int(round(h * scale))))
    return img.resize(new_size, Image.Resampling.LANCZOS)


def _save_image(img: Image.Image, dest: Path, grayscale: bool) -> None:
    img = img.convert("L" if grayscale else "RGB")
    img = _resize_max_side(img, MAX_SIDE)
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, format="PNG")


def _save_bytes(raw: bytes, dest: Path, grayscale: bool) -> None:
    _save_image(Image.open(io.BytesIO(raw)), dest, grayscale)


def collect_medical() -> list[tuple[str, str]]:
    dest_dir = DATA_DIR / "medical" / "clean"
    dest_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(dest_dir.glob("*.png"))
    if len(existing) >= N_CLEAN_IMAGES:
        print(f"[medical] {len(existing)} clean images already present in {dest_dir}")
        return [(p.name, "already on disk") for p in existing[:N_CLEAN_IMAGES]]

    saved: list[tuple[str, str]] = [(p.name, "already on disk") for p in existing]
    print(f"[medical] downloading clean chest X-rays into {dest_dir}")
    for filename, url, credit in MEDICAL_URLS:
        if len(saved) >= N_CLEAN_IMAGES:
            break
        stem = Path(filename).stem
        dest = dest_dir / f"{stem}.png"
        if dest.exists():
            continue
        try:
            print(f"  fetching {url}")
            raw = _download(url)
            _save_bytes(raw, dest, grayscale=True)
            saved.append((dest.name, credit))
            print(f"  saved {dest.name} ({dest.stat().st_size} bytes)")
        except Exception as exc:
            print(f"  SKIP {filename}: {exc}")
    if len(saved) < 3:
        raise SystemExit(f"[medical] only collected {len(saved)} images; need at least 3.")
    return saved[:N_CLEAN_IMAGES]


def _extract_ucmerced(zip_path: Path, dest_dir: Path) -> list[tuple[str, str]]:
    saved: list[tuple[str, str]] = []
    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
        for dest_name, member, credit in UCMERCED_MEMBERS:
            dest = dest_dir / dest_name
            if dest.exists():
                saved.append((dest.name, credit))
                continue
            if member not in names:
                print(f"  missing in zip: {member}")
                continue
            raw = zf.read(member)
            _save_bytes(raw, dest, grayscale=False)
            saved.append((dest.name, credit))
            print(f"  extracted {dest.name}")
    return saved


def _nasa_fallback(dest_dir: Path) -> list[tuple[str, str]]:
    """Crop several land tiles from NASA Blue Marble true-color mosaics."""
    saved: list[tuple[str, str]] = []
    crops = [
        (0.15, 0.35, 0.45, 0.65),
        (0.40, 0.20, 0.70, 0.50),
        (0.55, 0.45, 0.85, 0.75),
    ]
    for filename, url, credit in NASA_FALLBACK:
        print(f"  fetching fallback {url}")
        raw = _download(url)
        img = Image.open(io.BytesIO(raw)).convert("RGB")
        w, h = img.size
        for i, (x0, y0, x1, y1) in enumerate(crops, start=1):
            if len(saved) >= N_CLEAN_IMAGES:
                break
            box = (int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h))
            crop = img.crop(box)
            dest = dest_dir / f"{Path(filename).stem}_tile{i}.png"
            _save_image(crop, dest, grayscale=False)
            saved.append((dest.name, credit + f" (crop {i})"))
            print(f"  saved {dest.name}")
    return saved


def collect_satellite() -> list[tuple[str, str]]:
    dest_dir = DATA_DIR / "satellite" / "clean"
    dest_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(dest_dir.glob("*.png"))
    if len(existing) >= N_CLEAN_IMAGES:
        print(f"[satellite] {len(existing)} clean images already present in {dest_dir}")
        return [(p.name, "already on disk") for p in existing[:N_CLEAN_IMAGES]]

    print(f"[satellite] downloading UC Merced Land Use scenes into {dest_dir}")
    try:
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = Path(tmp) / "UCMerced_LandUse.zip"
            _download_to_file(UCMERCED_ZIP, zip_path)
            saved = _extract_ucmerced(zip_path, dest_dir)
        if len(saved) >= 3:
            return saved[:N_CLEAN_IMAGES]
        print("[satellite] zip extract produced too few images; trying NASA fallback")
    except Exception as exc:
        print(f"[satellite] UC Merced download failed ({exc}); trying NASA fallback")

    saved = _nasa_fallback(dest_dir)
    if len(saved) < 3:
        raise SystemExit(f"[satellite] only collected {len(saved)} images; need at least 3.")
    return saved[:N_CLEAN_IMAGES]


def write_sources(medical: list[tuple[str, str]], satellite: list[tuple[str, str]]) -> None:
    path = DATA_DIR / "SOURCES.md"
    lines = [
        "# Image sources",
        "",
        "Clean images only. Degraded copies are synthesized by `degradations.py`.",
        "",
        "## Medical — frontal chest X-ray",
        "",
    ]
    for name, credit in medical:
        lines.append(f"- `{name}` — {credit}")
    lines += ["", "## Satellite / remote sensing — optical RGB (UC Merced / USGS National Map)", ""]
    for name, credit in satellite:
        lines.append(f"- `{name}` — {credit}")
    lines += [
        "",
        "## Attribution notes",
        "",
        "- Chest X-rays: Cohen et al., covid-chestxray-dataset (frontal PA/AP radiographs only).",
        "- UC Merced Land Use: Yang & Newsam (2010), extracted from USGS National Map urban imagery.",
        "- NASA Blue Marble is used only as a fallback if the UC Merced archive cannot be fetched.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {path}")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    medical = collect_medical()
    satellite = collect_satellite()
    write_sources(medical, satellite)
    print("Clean-image collection done.")


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    main()
