"""Import public-domain (CC0) artwork into the motif library as bold 3-tone ink masks.

Only objects whose museum record states isPublicDomain = true are accepted; the licence and
source URL are re-checked from the API at import time and written to the element JSON
(LICENSES.md is generated from those fields by tools/library_sheets.py).

    python tools/import_public_domain.py <download_dir>

The original images are downloaded to <download_dir> (keep it outside the repo); only the
derived ink masks enter styles/references/library/.
"""
import json
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps

LIB = Path(__file__).resolve().parent.parent / "styles" / "references" / "library"
API = "https://collectionapi.metmuseum.org/public/collection/v1/objects/{}"
UA = {"User-Agent": "Mozilla/5.0 (clothing-store asset importer)"}

# met object id, element id, name, motif, styles, crop box (fractions l,t,r,b), mode, line thickening, rotate (deg CCW)
SOURCES = [
    (400112, "moth-engraved", "Moth study (after a CC0 18th-c. watercolour)", "moth",
     ["vamp-goth", "grunge", "archive", "cottagecore", "emo", "y2k"], (0.12, 0.33, 0.93, 0.78), "silhouette", 0, -45),
    (400116, "moth-engraved-2", "Hawk-moth study (after a CC0 18th-c. watercolour)", "moth",
     ["vamp-goth", "grunge", "archive", "emo"], (0.1, 0.18, 0.92, 0.82), "silhouette", 0, -32),
    (361543, "moth-plate", "Hawk-moth (after a CC0 engraved plate)", "moth",
     ["vamp-goth", "grunge", "archive", "emo"], (0.2, 0.05, 0.8, 0.5), "silhouette", 0, 0),
    (770198, "dragonfly-brooch", "Dragonfly (after a CC0 brooch)", "dragonfly",
     ["cottagecore", "y2k", "soft-girl", "gen-z"], (0.08, 0.15, 0.92, 0.85), "silhouette", 0, 0),
    (4653, "lace-border", "Lace border band (after a CC0 lace panel)", "lace",
     ["vamp-goth", "soft-girl", "cottagecore"], (0.05, 0.62, 0.95, 0.92), "silhouette_dark", 0, 0),
    (336169, "acanthus-scroll", "Acanthus scroll (after a CC0 15th-c. ornament engraving)", "filigree",
     ["vamp-goth", "archive", "preppy", "baddie"], (0.18, 0.2, 0.8, 0.93), "inverse", 1, 0),
]


def fetch_json(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_file(url, dest):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        dest.write_bytes(r.read())


def to_tones(img, mode, thicken):
    """Posterise to the library mask code: 255 = main ink, 170 = shadow tone, 85 = highlight, 0 = empty."""
    g = ImageOps.autocontrast(img.convert("L"))
    if mode == "silhouette":
        # subject vs light paper: darkness or colour saturation marks the subject
        sat = img.convert("HSV").split()[1]
        subject = Image.eval(Image.merge("RGB", (g, sat, sat)).convert("L"), lambda p: p)
        mask = Image.eval(g, lambda p: 255 if p < 205 else 0)
        mask = Image.composite(Image.new("L", g.size, 255), mask, sat.point(lambda p: 255 if p > 60 else 0))
        mask = mask.filter(ImageFilter.MedianFilter(7)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
        tone = g.point(lambda p: 170 if p < 90 else (85 if p > 170 else 255))
        return Image.composite(tone, Image.new("L", g.size, 0), mask)
    if mode == "silhouette_dark":  # light object on a dark backdrop
        mask = g.point(lambda p: 255 if p > 95 else 0).filter(ImageFilter.MedianFilter(7))
        mask = mask.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
        tone = g.point(lambda p: 170 if p < 150 else (85 if p > 215 else 255))
        return Image.composite(tone, Image.new("L", g.size, 0), mask)
    if mode == "inverse":  # light ornament on dark hatching: the light shapes become ink
        leaves = g.filter(ImageFilter.GaussianBlur(1.6)).point(lambda p: 255 if p > 128 else 0).filter(ImageFilter.MedianFilter(5))
        for _ in range(thicken):
            leaves = leaves.filter(ImageFilter.MaxFilter(3))
        return leaves
    # engraving: blur merges the hatching into tonal areas, then posterise into a bold stencil
    soft = ImageOps.autocontrast(g.filter(ImageFilter.GaussianBlur(2.2)))
    out = soft.point(lambda p: 255 if p < 95 else (170 if p < 150 else 0)).filter(ImageFilter.MedianFilter(5))
    for _ in range(thicken):
        out = out.filter(ImageFilter.MaxFilter(3))
    return out


def main():
    dl = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("pd_downloads")
    dl.mkdir(parents=True, exist_ok=True)
    LIB.mkdir(parents=True, exist_ok=True)
    for oid, eid, name, motif, styles, crop, mode, thicken, turn in SOURCES:
        rec = fetch_json(API.format(oid))
        if rec.get("isPublicDomain") is not True:
            print(f"SKIP {oid}: museum record does not state public domain")
            continue
        src = dl / f"met-{oid}.jpg"
        if not src.exists():
            fetch_file(rec["primaryImageSmall"], src)
        img = Image.open(src).convert("RGB")
        w, h = img.size
        img = img.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h)))
        img = img.resize((256, int(256 * img.height / img.width)), Image.LANCZOS)
        mask = to_tones(img, mode, thicken)
        if turn:
            mask = mask.rotate(turn, resample=Image.NEAREST, expand=True)
        box = mask.getbbox()
        if box:
            mask = mask.crop(box)
        mask.save(LIB / f"{eid}.png")
        el = {"id": eid, "name": name, "motif": motif, "styles": styles, "mood": ["vintage", "engraved"],
              "size": "large", "families": ["print"], "symmetric": False, "band": False, "source": "public-domain",
              "mask": f"{eid}.png",
              "license": {"licence": "CC0 1.0 (The Met Open Access, isPublicDomain = true)",
                          "source_url": rec.get("objectURL"), "image_url": rec.get("primaryImage") or rec.get("primaryImageSmall"),
                          "title": rec.get("title"), "artist": rec.get("artistDisplayName"), "date": rec.get("objectDate"),
                          "checked": "2026-11-16 via collectionapi.metmuseum.org"}}
        (LIB / f"{eid}.json").write_text(json.dumps(el, indent=1), encoding="utf-8")
        print(f"imported {eid} from Met {oid} ({rec.get('title')})")


if __name__ == "__main__":
    main()
