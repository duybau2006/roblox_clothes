# Codex designer guide: Roblox classic clothing store

## Summary
1. You design original outfits for a Roblox group store; you never draw pixels by hand.
2. One outfit = one YAML spec in `specs/` = two listings: a shirt and pants.
3. The torso is rendered once into BOTH files, so each half looks complete when worn alone.
4. Three design families: **decorated** (small motifs, patterns, trims), **print** (one large torso composition; **combined** adds small motifs) and **realistic** (materials, folds, sewn construction, cut-outs, shoes, numbers, emblems).
5. The tools render, validate and preview each outfit; you fix problems in the spec, never in a PNG. Never upload, never spend Robux.

## Files
- [styles/guides/](styles/guides/README.md): **start here.** One guide per style: spec settings, palette, family fit, research notes, name words, traps, and validated examples of both families. Batch-mix rules live in its README.
- [styles/references/](styles/references/README.md): the element [library](styles/references/library/INDEX.md) (124 tagged elements, one file each), per-style sheets, shading and vault contact sheets, and [LICENSES.md](styles/references/LICENSES.md) (every outside asset, plus what was skipped and why).
- [specs/_template.yaml](specs/_template.yaml): the outfit spec, every field explained. [styles/irl.yaml](styles/irl.yaml), [styles/roblox.yaml](styles/roblox.yaml): full style libraries.
- [trends/](trends/): dated trend notes (newest first) and [recipe-log.csv](trends/recipe-log.csv) (recipes already used).
- `tools/`: `render.py`, `validate.py`, `preview.py`, `recipes.py`, `run_tests.py` (run from `clothing-store/`).
- [golden/](golden/): the owner-approved reference outfit; every outfit must match its quality.
- [templates/](templates/), [calibration/](calibration/): panel map, shared shading, collected public-domain shading layers (`templates/shading/custom/`), Studio calibration. Never edit per outfit.

## Workflow (follow in order for every outfit)
1. **Read trends.** Newest `trends/` files: selling styles, colours, name words, and the recipe log.
2. **Pick a style and family.** Open its guide; use the family it recommends. Use `palette_tones` hexes; obey the `avoid` list.
3. **Pick a recipe.** `python tools/recipes.py suggest --style <style> [--family realistic]` lists combinations not tried yet. Decorated/print recipe = style, family, template, 2-5 element tags, ink, distress, seed. Realistic recipe = archetype template, 4 colours, seed, optional layer and number.
4. **Write the outfit spec.** Copy `specs/_template.yaml` to `specs/<id>.yaml`; fill `family`, torso, arms, legs, `recipes` (or explicit `decor`), listings, `moderation_check`.
5. **Render.** `python tools/render.py specs/<id>.yaml` writes `renders/<id>-shirt.png`, `-pants.png` and `-resolved.yaml` (the elements a recipe picked). Every `WARNING` means something was not drawn.
6. **Validate.** `python tools/validate.py specs/<id>.yaml` must print `PASS`. Check every `WARN` yourself.
7. **Preview.** `python tools/preview.py specs/<id>.yaml` writes `previews/<id>/sheet.png` (together, shirt only, pants only; front, back, sides).
8. **Self-review, then propose.** Tick the pre-submit checklist; list spec path, validate result, WARNs checked, sheet path. Stop for approval.

## Design families and recipes
1. Declare `family: decorated | print | combined | realistic`; the validator checks it matches the outfit.
   **Owner note (2026-11-16): put the main graphic on the FRONT** (front print, chest graphic). The current designs, which mostly carry their graphic on the back, are approved and usable; for new ones, back graphics are secondary (a small back accent, or a back print only when asked). Recipes default to `placement: front`.
2. Decorated: `decor` entries on torso, arms or legs (chest, pocket, back, sleeve, thigh, scatter, row, trims). The 12 decorated guide examples stay valid references.
3. Print: one torso composition (`front` or `back`, optional `wrap` onto the sides) from library elements, templates `centered_stack`, `symmetric_pair`, `offcentre_figure`, `allover_faded`.
4. A print uses ONE ink in 2-3 automatic tones; distress 0-3 (drips, splatter, scratches, halftone, cracked, worn); washed fabrics `acid_wash`, `mineral_wash`, `heather`, `faded_black`.
5. Combined: a print plus small decorated motifs (e.g. back print + sleeve hearts), within the palette limit.
6. Same recipe + same seed = identical design; change the seed for a new arrangement. Prefer recipes rather than hand-placing.
7. All families use only library elements; add new ones by editing `tools/build_library.py` (original), `tools/import_public_domain.py` (CC0 with licence) or, for the owner's own generated sheets, `styles/references/inbox/classify.yaml` + `tools/import_motifs.py build` (holds go to `styles/references/held/`), never by pasting images.
8. Owner artwork (`g01-*` .. `g10-*`): recoloured to one ink by default; `original: true` keeps its colours (count them in the palette). Borders use `layout: border`; fabric swatches `base_pattern: swatch`. Elements marked print-size only stay off chest and sleeve placements.
9. Design for 128 px: main shapes bold, lines 2 px or more (see `calibration/print-linewidth-*.png`).
10. Realistic: archetypes `basic_tee_jeans knit_stripes racing_jersey suit_waistcoat bomber_badge corset_trousers pleated_skirt_bows sports_shorts crop_lowrise` (references: `styles/guides/examples/realistic-*.yaml`); set `material` and `garment_kind` per section and `parts` for collars, lapels, ties, waistcoats, zips, pockets, belts, jeans stitching, cuffs, trims, piping, lacing.
11. Shading: EVERY outfit, in every family, is shaded with `own-shade-all` (the owner's three templates stacked, on torso, arms and legs). Leave `shading.layer` out to get it; only vary `shading.seed`. Their licence is not confirmed yet: `validate.py` WARNs until it is. Any family may use `parts`, `identity` and `shoe_style`.
12. Separates: `coverage: top_only | bottom_only` renders a single file sold alone.

## Hard rules: technical
1. Canvas is exactly 585 x 559 px, PNG, transparent background; never move template regions (`regions.json`).
2. Panels: torso front/back 128x128, torso sides 64x128, torso top/bottom 128x64, limb sides 64x128, limb top/bottom 64x64.
3. Art stays inside the panels (plus 2 px bleed); patterns continue across every seam pair, the shoulder and the hip.
4. The torso panels are pixel-identical in both files; the shirt file adds arms, the pants file adds legs.
5. The top garment ends at `torso.hem_line` (80-120); the waistband starts at `legs.waist_line` (88-110); a crop gap is at most 16 px.
6. Skirts run to `skirt_length`: min 32, or 24 with tights. Tights, socks and under-sleeves are never skin-coloured.
7. Sleeves match the torso at the shoulder unless `arms.sleeve_contrast: true`; layered = `sleeves: short` + `arms.under`.
8. Fixed lines (R15): cuff 98-110, hand below 110, short sleeve ends at 40, ankle cuff 94-106, shoes 106-128 (bottom quarter only).
9. Every outfit is shaded with the default layer `own-shade-all` on top of the shared or realistic shading; flat colour fills are not acceptable.
10. Section palettes by role: [0] body, [1] trim, [2] accent. The outfit `palette` lists every colour incl. decor and print inks: max 4 + 1 neutral.
11. Only details, motifs and library elements listed in the template are drawn; anything else needs renderer work. Say so, don't fake it.
12. Every outfit gets decoration or a print that fits its guide; plain is only right for gen Z basics and golden-style sets.
13. Never hand-edit a rendered PNG. `validate.py` must PASS (including the near-duplicate check) before proposing.

## Hard rules: moderation (a rejected upload loses its fee)
1. No brand names, logos, monograms or look-alike marks (no three-stripe, swoosh-like shapes).
2. No real sports teams, bands, games, shows, anime or film characters; nothing from Roblox's own logo or items.
3. Never copy, trace, save or paste artwork from other creators, brands or product photos; look only to learn the style.
4. No text beyond one or two generic words; no slogans, usernames or links. Library elements contain no text.
5. Nothing sexual or suggestive; no skin-coloured fabric; no see-through panels; no lingerie look. Cut-outs are transparent, never painted skin: necklines at most 22 rows, straps 5 px or wider, strapless / off-shoulder edges at row 14 or higher, chest (rows 24 to hem) and hips always covered.
6. No political, religious, drug, alcohol, gore or real-weapon imagery. No crosses or religious symbols.
7. Stylised skulls are allowed (no blood or gore); daggers only as ornament. Ink drips are paint, never blood-red gore.
8. Uniforms use invented insignia only; nothing that hides the avatar. Each style's `avoid` list is binding.
9. Identity graphics: numbers 0-99 only (no letters or words); emblems are library elements in an invented frame. No real team kits, flags, organisations or brands.
10. Outside assets only if public domain, CC0 or clearly commercial + modification, logged in LICENSES.md; never another creator's finished clothing.

## Hard rules: style choice and naming
1. Check `trends/` first; favour styles and name words that sell. `unverified: true` styles only with a reason.
2. A batch spreads across styles, the three families (about a third each) and masc / fem / unisex; see "Mixing a batch" in the guides README.
3. Two listings per outfit: `<words> Outfit Top` and `<words> Outfit Pants`; `<words>` = colour + garment + 0-4 style words (`listings.words`). Separates: one listing, `<words> Top` or `<words> Pants`.
4. Style words come from the "Most-used name words" of the newest `trends/*-catalog.md`; no brand, character, game or creator names.
5. No repeated words, no "free", no emoji, no keyword lists; each name max 50 characters.
6. Each description: what this half is, then the full name of the other half. No links, tags or sales pressure.

## Worked example (good, print family by recipe)
```yaml
id: print-vamp-goth
style: vamp-goth
audience: unisex
family: print
palette: ["#2A2A2E", "#1A1A1A", "#E8E4DC"]
torso: {garment: faded black long sleeve tee, palette: ["#2A2A2E"], base_pattern: faded_black, details: [crew collar], hem: plain, hem_line: 112}
arms: {sleeves: long, details: []}
legs: {garment: black wide trousers, type: trousers, waist_line: 92, waistband: plain, palette: ["#1A1A1A"], base_pattern: solid,
       details: [belt loops], shoes: black boots, shoe_palette: ["#1A1A1A", "#2A2A2E"]}
recipes:
  - {family: print, style: vamp-goth, template: symmetric_pair, placement: back, tags: [skull, wings, rose], ink: "#E8E4DC", distress: 2, seed: 3}
listings:
  words: {colour: "Black", garment: "Skull Wings Tee", style: ["vamp", "goth"]}
  shirt: {name: "Black Skull Wings Tee Vamp Goth Outfit Top", description: "A faded black long sleeve tee with a cracked bone-white skull, wings and roses print on the back. Wear it with Black Skull Wings Tee Vamp Goth Outfit Pants for the full look."}
  pants: {name: "Black Skull Wings Tee Vamp Goth Outfit Pants", description: "Black wide trousers and boots, with the skull wings tee on the torso. Wear them with Black Skull Wings Tee Vamp Goth Outfit Top for the full look."}
moderation_check: "Stylised skull, wings and roses only; no crosses, blood, text or logos."
```
Decorated-family references: [golden/](golden/), `styles/guides/examples/<style>.yaml`. Combined: `examples/combined-baddie.yaml`.

## Bad example (do not do this)
```yaml
id: hype-drip
family: print
palette: ["#111111", "#FFFFFF"]
torso: {garment: crop hoodie, palette: ["#111111", "#E8C4A0"], hem_line: 64,
        decor: [{print: {template: centered_stack, elements: [latin-cross, brand-logo], ink: "#B00000"}}]}
legs:  {palette: ["#1E3557"], details: [three white stripes down each leg], shoes: tall boots to the knee}
listings:
  words: {colour: "Black", garment: "Black Hoodie", style: ["supreme", "da hood", "drip", "y2k", "emo"]}
  shirt: {name: "FREE Black Black Hoodie Supreme Da Hood Drip Y2K Emo Outfit Top", description: "best fit!! tags: y2k emo vamp"}
```
Why it fails:
1. `latin-cross` and `brand-logo` are not library elements and are blocked subjects (moderation 1, 6; technical 11).
2. "three white stripes" imitates a brand; "supreme" and "da hood" are brand and game names (moderation 1-2, naming 4).
3. `#E8C4A0` reads as skin-tone fabric; `hem_line: 64` and its crop gap break the cut rules (moderation 5, technical 5).
4. Boots to the knee break the bottom-quarter rule; `#E8C4A0`, `#1E3557` and the print ink are missing from `palette` (technical 8, 10).
5. Five style words, "drip" is not a trend word, "Black" repeats, "FREE", over 50 characters (naming 3-5).
6. The pants listing, `arms`, `audience` and `moderation_check` are missing; the description is tags and pressure copy (naming 6).

## Pre-submit checklist (tick every line for every outfit)
- [ ] Style and family follow the guide; its `avoid` list re-read.
- [ ] Spec has family, torso, arms, legs, listings, audience and moderation_check; colours come from `palette_tones`.
- [ ] Recipe checked against `recipes.py suggest` / the recipe log: not a combination already used for this style.
- [ ] `render.py` printed no WARNING (or each is flagged); `validate.py` printed PASS incl. `duplicate`; every WARN checked by eye.
- [ ] `sheet.png`: together, shirt only and pants only all look like a complete, ordinary outfit; shoulder and hip continuous.
- [ ] Main graphic is on the front (owner note); any back graphic is a secondary accent.
- [ ] Quality matches `golden/`; prints are bold and readable at 128 px; distress still leaves the main shape readable.
- [ ] No brands, look-alike marks, text, crosses, religious symbols, gore, real characters, games or teams.
- [ ] No skin-tone fabric, see-through areas or suggestive cuts; crop gap ≤ 16 px; skirt / shorts long enough; cut-outs within limits.
- [ ] Realistic: folds and highlights suit the material; collected layer named in LICENSES.md; numbers are digits only.
- [ ] Names: `listings.words` + "Outfit Top" / "Outfit Pants", trend words only, no repeats, ≤ 50 chars; descriptions name the other half.
- [ ] Nothing uploaded, no Robux spent.

## Glossary
- **Panel:** one face of a body part on the template; boxes in `regions.json`. **Seam pair:** two panel edges that touch on the avatar.
- **Shoulder / hip seam:** where the torso meets the arms or legs; spans the shirt and pants files. **Bleed:** 2 px of colour outside each panel.
- **Outfit:** one spec sold as two listings with an identical torso. **Golden set:** the approved reference outfit in `golden/`.
- **Family:** decorated (small motifs), print (one large composition), combined (both) or realistic (real garment construction and materials). **Element:** one tagged library file.
- **Recipe:** style + family + template + tags + ink + distress + seed; expanded by `tools/recipes.py`, logged in `trends/recipe-log.csv`.
- **Archetype:** a realistic recipe template (garment structure, materials, parts). **Shading layer:** a collected public-domain greyscale map in `templates/shading/custom/`.
- **Separates:** `coverage: top_only` / `bottom_only`, one file and one listing.

## Batch prompts
Design batch:
> Read AGENTS.md, styles/guides/README.md and the guides of the styles you pick, and the newest files in trends/ including trends/recipe-log.csv. Propose a batch of N outfits (each outfit is one spec that produces a shirt listing and a pants listing). Spread it across at least N/2 styles, across masc, fem and unisex, and across the three design families (about a third each of decorated, print or combined, and realistic, unless trends/ sales data says otherwise; realistic outfits alternate procedural shading and a collected layer and never repeat archetype + seed), following "Mixing a batch". Within a style, never repeat a template with the same main element; run `python tools/recipes.py suggest --style <style>` and prefer untried recipes. Write one spec per outfit in specs/ using recipes where possible. Re-read every spec against the moderation rules and fix or drop any that could fail. Do not render or upload; stop and list the specs for approval.

Render batch (after the specs are approved):
> For each approved outfit run render.py, validate.py and preview.py as in AGENTS.md (separates have one file). Fix any FAIL or WARNING by changing the spec (a near-duplicate needs a different template, main element, ink or seed), never by editing PNGs. Tick the pre-submit checklist, compare each sheet.png with golden/, and list per outfit: family, recipe, validate result, any WARN you checked by eye, and the sheet path. Do not upload; stop for approval.
