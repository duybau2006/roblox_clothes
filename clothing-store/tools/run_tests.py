"""Run every pipeline test. Exit code 1 if any test does not behave as expected.

    python tools/run_tests.py            (renders into tests/renders/, previews into tests/previews/)

1. Good outfits (specs/, tests/specs/ and styles/guides/examples/): render, validate (must PASS), preview.
2. Bad outfits: each case is a good spec plus overrides; it must FAIL on the named check(s).
3. Broken images: a good render is damaged on purpose; validate must FAIL on the named check.
"""
import copy
import subprocess
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clothing import ROOT                       # noqa: E402
from render import render                       # noqa: E402
from validate import validate_outfit            # noqa: E402

T = ROOT / "tests"
RENDERS, BADDIR = T / "renders", T / "renders-bad"

BAD = [  # (case id, base spec, overrides as {"section.key": value}, checks that must FAIL)
    ("bad-crop-gap", "test-crop-top", {"torso.hem_line": 80, "legs.waist_line": 104}, ["cut"]),
    ("bad-hem-too-high", "test-crop-top", {"torso.hem_line": 70}, ["cut"]),
    ("bad-skirt-too-short", "test-skirt", {"legs.skirt_length": 20, "legs.legwear": "bare"}, ["cut"]),
    ("bad-skin-tights", "test-skirt", {"legs.legwear": "tights", "legs.legwear_palette": ["#E0B48C"],
                                       "palette": ["#F3EBDD", "#1C2A4A", "#8B1E2D", "#FFFFFF", "#E0B48C"]}, ["cut"]),
    ("bad-contrast-no-flag", "test-contrast-sleeves", {"arms.sleeve_contrast": False}, ["shoulder"]),
    ("bad-name-brand", "golden-grey-lounge", {"listings.words.style": ["supreme"]}, ["listings"]),
    ("bad-name-game", "golden-grey-lounge", {"listings.words.style": ["da hood"]}, ["listings"]),
    ("bad-name-repeat", "golden-grey-lounge", {"listings.words.garment": "Grey Hoodie"}, ["listings"]),
    ("bad-name-not-trend", "golden-grey-lounge", {"listings.words.style": ["streetwear"]}, ["listings"]),
    ("bad-name-5-style", "golden-grey-lounge", {"listings.words.style": ["y2k", "emo", "vamp", "goth", "cute"]}, ["listings"]),
    ("bad-palette", "golden-grey-lounge", {"legs.palette": ["#123456"]}, ["palette"]),
    ("bad-decor-motif", "golden-grey-lounge", {"torso.decor": [{"motif": "logo", "layout": "chest", "colour": "#ECECEC"}]}, ["decor"]),
    ("bad-decor-layout", "golden-grey-lounge", {"legs.decor": [{"motif": "star", "layout": "chest", "colour": "#ECECEC"}]}, ["decor"]),
    ("bad-decor-colour", "golden-grey-lounge", {"torso.decor": [{"motif": "star", "layout": "chest", "colour": "#00FF00"}]}, ["palette"]),
    ("bad-family-mismatch", "print-grunge", {"family": "decorated"}, ["family"]),
    ("bad-family-no-print", "golden-grey-lounge", {"family": "print"}, ["family"]),
    ("bad-family-missing", "golden-grey-lounge", {"family": ""}, ["family"]),
    ("bad-print-unknown-element", "print-layered-moth", {"torso.decor": [{"print": {
        "placement": "back", "template": "centered_stack", "elements": ["latin-cross"], "ink": "#E8E4DC"}}]}, ["decor"]),
    ("bad-print-on-legs", "golden-grey-lounge", {"legs.decor": [{"print": {
        "placement": "front", "template": "centered_stack", "elements": ["skull-classic"], "ink": "#ECECEC"}}]}, ["decor"]),
    ("bad-duplicate", "print-grunge", {"_with_original": True}, ["duplicate"]),
    # realistic family
    ("bad-realistic-no-material", "golden-grey-lounge", {"family": "realistic"}, ["family"]),
    ("bad-identity-word", "realistic-racing-jersey", {"identity.number": "KING"}, ["identity"]),
    ("bad-identity-100", "realistic-racing-jersey", {"identity.number": 100}, ["identity"]),
    ("bad-identity-text-field", "realistic-racing-jersey", {"identity.team_name": "Falcons"}, ["identity"]),
    ("bad-emblem-element", "realistic-bomber-badge", {"identity.emblem": {"frame": "shield", "element": "eagle-flag"}}, ["identity"]),
    ("bad-unlicensed-layer", "realistic-basic-tee-jeans", {"shading.layer": "pd-unknown-layer"}, ["shading"]),
    ("bad-layer-too-strong", "realistic-bomber-badge", {"shading.strength": 1.5}, ["shading"]),
    ("bad-neckline-deep", "realistic-corset-trousers", {"torso.cut": {"style": "tank", "neckline": "v", "depth": 34}}, ["cut"]),
    ("bad-strap-thin", "realistic-corset-trousers", {"torso.cut": {"style": "tank", "neckline": "square", "depth": 8, "strap_width": 3}}, ["cut"]),
    ("bad-strapless-low", "test-off-shoulder", {"torso.cut": {"style": "strapless", "top": 26}}, ["cut"]),
    ("bad-shorts-short", "realistic-sports-shorts", {"legs.shorts_length": 20}, ["cut"]),
    ("bad-unknown-part", "realistic-basic-tee-jeans", {"legs.parts": ["belt", "logo_patch"]}, ["realistic"]),
    ("bad-print-only-small", "owner-gen-z", {"torso.decor": [{"element": "g02-dotted-butterfly", "layout": "chest", "colour": "#2B2B2B", "size": 8}]}, ["decor"]),
    ("bad-owner-colours", "owner-gen-z", {"torso.decor": [{"element": "g05-cherry-hearts-bow", "layout": "chest", "original": True, "size": 9}]}, ["palette"]),
    ("bad-border-not-tile", "owner-gen-z", {"torso.decor": [{"element": "g01-star-solid", "layout": "border", "colour": "#2B2B2B"}]}, ["decor"]),
    ("bad-held-element", "owner-gen-z", {"torso.decor": [{"element": "winged-cross", "layout": "chest", "colour": "#2B2B2B"}]}, ["decor"]),
    ("bad-separate-name", "test-halter-top-only", {"listings.shirt.name": "Burgundy Halter Top Baddie Outfit Top"}, ["listings"]),
]


def spec_paths():
    return [p for p in sorted((ROOT / "specs").glob("*.yaml")) if not p.name.startswith("_")] + \
           sorted((T / "specs").glob("*.yaml")) + sorted((ROOT / "styles" / "guides" / "examples").glob("*.yaml"))


def names_listing(spec):
    """Rebuild the two names from listings.words so name-rule cases test only what they change."""
    w = spec["listings"]["words"]
    words = " ".join([w["colour"], w["garment"], *[s.title() if s.islower() else s for s in w.get("style", [])]])
    spec["listings"]["shirt"]["name"] = f"{words} Outfit Top"
    spec["listings"]["pants"]["name"] = f"{words} Outfit Pants"
    spec["listings"]["shirt"]["description"] = f"Test top. Wear it with {words} Outfit Pants."
    spec["listings"]["pants"]["description"] = f"Test pants. Wear them with {words} Outfit Top."


def failed_checks(rep):
    return {name for name, tag in rep.results if tag == "FAIL"}


def main():
    ok = True
    good = {}
    print("== good outfits")
    for sp in spec_paths():
        _, warnings = render(sp, RENDERS)
        oid, rep = validate_outfit(sp, RENDERS)
        good[Path(sp).stem] = sp
        if (yaml.safe_load(Path(sp).read_text(encoding="utf-8")) or {}).get("uploaded"):
            passed = failed_checks(rep) == {"upload"}            # uploaded outfits must be refused, and only for that
            ok &= passed
            print(f"  {'ok  ' if passed else 'FAIL'} {oid} (uploaded: refused for re-queue)")
            continue
        passed = rep.ok and not [w for w in warnings if "not supported" in w]
        ok &= passed
        print(f"  {'ok  ' if passed else 'FAIL'} {oid}" + ("" if passed else "\n" + "\n".join(rep.lines + warnings)))
        subprocess.run([sys.executable, str(ROOT / "tools" / "preview.py"), str(sp), "--renders", str(RENDERS),
                        "--out", str(T / "previews" / oid)], check=True, capture_output=True)
    print("== bad outfits (must fail on the named check)")
    BADDIR.mkdir(parents=True, exist_ok=True)
    for case, base, overrides, expect in BAD:
        spec = copy.deepcopy(yaml.safe_load(Path(good[base]).read_text(encoding="utf-8")))
        spec["id"] = case
        for key, val in overrides.items():
            tgt = spec
            parts = key.split(".")
            for k in parts[:-1]:
                tgt = tgt.setdefault(k, {})
            tgt[parts[-1]] = val
        if overrides.get("_with_original"):          # put the original next to its copy
            spec.pop("_with_original", None)
            orig = BADDIR / f"{base}.yaml"
            orig.write_text(Path(good[base]).read_text(encoding="utf-8"), encoding="utf-8")
            render(orig, BADDIR)
        if any(k.startswith("listings.words") for k in overrides):
            names_listing(spec)
        sp = BADDIR / f"{case}.yaml"
        sp.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
        render(sp, BADDIR)
        _, rep = validate_outfit(sp, BADDIR)
        got = failed_checks(rep)
        passed = set(expect) <= got
        ok &= passed
        print(f"  {'ok  ' if passed else 'FAIL'} {case}: expected FAIL on {expect}, failed on {sorted(got) or 'nothing'}")
    print("== broken images (must fail on the named check)")
    base = good["golden-grey-lounge"]
    damage = [
        ("torso differs", "torso", lambda s, p: ImageDraw.Draw(p).rectangle([240, 90, 300, 140], fill=(200, 40, 40, 255))),
        ("guide colour", "shirt: guide", lambda s, p: ImageDraw.Draw(s).rectangle([20, 380, 60, 420], fill=(0, 162, 255, 255))),
        ("pixels outside", "shirt: outside", lambda s, p: ImageDraw.Draw(s).rectangle([0, 0, 20, 20], fill=(255, 0, 0, 255))),
        ("arm seam broken", "shirt: seams", lambda s, p: ImageDraw.Draw(s).rectangle([85, 355, 148, 482], fill=(20, 200, 40, 255))),
        ("hip broken", "hip", lambda s, p: ImageDraw.Draw(p).rectangle([217, 355, 280, 380], fill=(20, 200, 40, 255))),
        ("shoes too high", "pants: shoes", lambda s, p: ImageDraw.Draw(p).rectangle([217, 400, 280, 482], fill=(242, 242, 242, 255))),
        ("chest uncovered", "cut", lambda s, p: [ImageDraw.Draw(im).rectangle([250, 110, 340, 118], fill=(0, 0, 0, 0)) for im in (s, p)]),
    ]
    for name, check, fn in damage:
        d = T / "renders-broken"
        d.mkdir(exist_ok=True)
        s = Image.open(RENDERS / "golden-grey-lounge-shirt.png").convert("RGBA")
        p = Image.open(RENDERS / "golden-grey-lounge-pants.png").convert("RGBA")
        fn(s, p)
        s.save(d / "golden-grey-lounge-shirt.png"); p.save(d / "golden-grey-lounge-pants.png")
        _, rep = validate_outfit(base, d)
        got = failed_checks(rep)
        passed = check in got
        ok &= passed
        print(f"  {'ok  ' if passed else 'FAIL'} {name}: expected FAIL on '{check}', failed on {sorted(got) or 'nothing'}")
    (T / "renders-broken" / "golden-grey-lounge-shirt.png").unlink(missing_ok=True)
    (T / "renders-broken" / "golden-grey-lounge-pants.png").unlink(missing_ok=True)
    print("== recipes, determinism and library")
    import library
    from validate import Report, check_library
    vg = good["print-vamp-goth"]
    a_dir, b_dir = T / "det-a", T / "det-b"
    render(vg, a_dir); render(vg, b_dir)
    same = (a_dir / "print-vamp-goth-shirt.png").read_bytes() == (b_dir / "print-vamp-goth-shirt.png").read_bytes()
    ok &= same
    print(f"  {'ok  ' if same else 'FAIL'} same recipe + same seed gives identical pixels")
    spec = yaml.safe_load(Path(vg).read_text(encoding="utf-8"))
    spec["recipes"][0]["seed"] = 99
    sp2 = b_dir / "print-vamp-goth.yaml"
    sp2.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
    render(sp2, b_dir)
    i1 = Image.open(a_dir / "print-vamp-goth-shirt.png").convert("L")
    i2 = Image.open(b_dir / "print-vamp-goth-shirt.png").convert("L")
    diff = sum(abs(x - y) for x, y in zip(i1.get_flattened_data(), i2.get_flattened_data())) / (i1.width * i1.height)
    changed = diff > 0.5
    ok &= changed
    print(f"  {'ok  ' if changed else 'FAIL'} a new seed gives a new arrangement (mean change {diff:.2f})")
    rj = good["realistic-basic-tee-jeans"]
    render(rj, a_dir); render(rj, b_dir)
    same = (a_dir / "realistic-basic-tee-jeans-pants.png").read_bytes() == (b_dir / "realistic-basic-tee-jeans-pants.png").read_bytes()
    ok &= same
    print(f"  {'ok  ' if same else 'FAIL'} realistic shading: same seed gives identical pixels")
    spec = yaml.safe_load(Path(rj).read_text(encoding="utf-8"))
    spec["shading"]["seed"] = 42
    sp3 = b_dir / "realistic-basic-tee-jeans.yaml"
    sp3.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
    render(sp3, b_dir)
    i1 = Image.open(a_dir / "realistic-basic-tee-jeans-shirt.png").convert("L")
    i2 = Image.open(b_dir / "realistic-basic-tee-jeans-shirt.png").convert("L")
    diff = sum(abs(x - y) for x, y in zip(i1.get_flattened_data(), i2.get_flattened_data())) / (i1.width * i1.height)
    ok &= diff > 0.2
    print(f"  {'ok  ' if diff > 0.2 else 'FAIL'} realistic shading: a new seed moves the folds (mean change {diff:.2f})")
    import recipes
    bt = recipes.expand({"family": "decorated", "style": "emo", "template": "border_trim", "tags": ["checker", "barbed"],
                         "ink": "#FFFFFF", "seed": 1})
    okb = all(library.element(e["element"]).get("tile") and e["layout"] == "border" for _, e in bt)
    ok &= okb
    print(f"  {'ok  ' if okb else 'FAIL'} border_trim recipe picks owner border tiles")
    lib = library.load_library()
    for eid, el, what in (("latin-cross", {"id": "latin-cross", "name": "Latin cross", "motif": "cross", "source": "original"}, "blocked subject"),
                          ("pd-unlicensed", {"id": "pd-unlicensed", "name": "Old print", "motif": "ornament", "source": "public-domain"}, "missing licence")):
        lib[eid] = el
        r = Report()
        check_library(r)
        del lib[eid]
        caught = ("library", "FAIL") in r.results
        ok &= caught
        print(f"  {'ok  ' if caught else 'FAIL'} library rejects an element with a {what}")
    r = Report()
    check_library(r)
    clean = ("library", "PASS") in r.results
    ok &= clean
    print(f"  {'ok  ' if clean else 'FAIL'} real library: every element original or licensed, nothing blocked")
    print("ALL TESTS PASSED" if ok else "SOME TESTS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
