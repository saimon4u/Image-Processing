"""Download a larger clean set: more frontal chest X-rays + UC Merced scenes.

Writes to data_extra/{medical,satellite}/clean (the original 12-image set in
data/ is left untouched). UC Merced is read straight out of the remote zip via
HTTP range requests, so the whole archive is not downloaded.
"""
from __future__ import annotations

import csv
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
EXTRA = ROOT / "data_extra"
UA = {"User-Agent": "Mozilla/5.0"}
CXR_BASE = "https://raw.githubusercontent.com/ieee8023/covid-chestxray-dataset/master/"
UCM_ZIP = ("https://huggingface.co/datasets/torchgeo/ucmerced/resolve/"
           "7c5ef3454d9b1cccfa7ccde0c01fc8f00a45909a/UCMerced_LandUse.zip")
N_CXR = 40
PER_CLASS = 3


def get(url: str) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()


def collect_cxr():
    dest = EXTRA / "medical" / "clean"
    dest.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(io.StringIO(get(CXR_BASE + "metadata.csv").decode("utf-8", "ignore"))))
    n = len(list(dest.glob("*.png")))
    for r in rows:
        if n >= N_CXR:
            break
        if r.get("view") not in ("PA", "AP") or not r.get("filename", "").lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        out = dest / f"cxr_{n:03d}.png"
        try:
            img = Image.open(io.BytesIO(get(CXR_BASE + "images/" + r["filename"]))).convert("L")
        except Exception as e:  # noqa: BLE001
            print("skip", r["filename"], e)
            continue
        if min(img.size) < 400:
            continue
        s = 512 / max(img.size)
        if s < 1:
            img = img.resize((round(img.width * s), round(img.height * s)), Image.Resampling.LANCZOS)
        img.save(out)
        n += 1
        print(f"cxr {n}/{N_CXR} {r['filename']}")


class RangeFile(io.RawIOBase):
    """Seekable file over HTTP range requests (just enough for zipfile)."""

    def __init__(self, url):
        self.url, self.pos = url, 0
        req = urllib.request.Request(url, headers={**UA, "Range": "bytes=0-0"})
        resp = urllib.request.urlopen(req, timeout=60)
        self.size = int(resp.headers["Content-Range"].split("/")[1])

    def seekable(self): return True
    def readable(self): return True
    def tell(self): return self.pos

    def seek(self, off, whence=0):
        self.pos = off if whence == 0 else self.pos + off if whence == 1 else self.size + off
        return self.pos

    def read(self, n=-1):
        if n < 0:
            n = self.size - self.pos
        n = min(n, self.size - self.pos)
        if n <= 0:
            return b""
        req = urllib.request.Request(self.url, headers={**UA, "Range": f"bytes={self.pos}-{self.pos + n - 1}"})
        data = urllib.request.urlopen(req, timeout=120).read()
        self.pos += len(data)
        return data

    def readinto(self, b):
        d = self.read(len(b))
        b[: len(d)] = d
        return len(d)


def collect_satellite():
    dest = EXTRA / "satellite" / "clean"
    dest.mkdir(parents=True, exist_ok=True)
    zf = zipfile.ZipFile(io.BufferedReader(RangeFile(UCM_ZIP), 1 << 20))
    by_class: dict[str, list[str]] = {}
    for name in zf.namelist():
        if name.lower().endswith(".tif"):
            by_class.setdefault(name.split("/")[-2], []).append(name)
    for cls, names in sorted(by_class.items()):
        for name in sorted(names)[: PER_CLASS]:
            out = dest / f"ucm_{Path(name).stem}.png"
            if out.exists():
                continue
            Image.open(io.BytesIO(zf.read(name))).convert("RGB").save(out)
            print("sat", out.name)


if __name__ == "__main__":
    which = sys.argv[1:] or ["cxr", "sat"]
    if "cxr" in which:
        collect_cxr()
    if "sat" in which:
        collect_satellite()
