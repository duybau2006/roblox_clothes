# Gen Z everyday / clean streetwear

**Audience:** unisex, the widest mass-market look. **Trend evidence:** plain basics (18 catalog hits) + streetwear hoodie sets (13). **Library:** `gen-z` (irl.yaml), `streetwear-hoodie-set`, `basics-plain` (roblox.yaml).
**Golden reference:** [golden/](../../golden/) (grey hoodie + joggers) is the quality bar for this style and for every other style.

## The look
Oversized, plain, soft-neutral pieces worn as a matching set, with clean white sneakers. Quality comes from construction (ribs, hems, folds), not from graphics.

## Spec settings
- Torso: tee, hoodie or zip hoodie; `hem: rib` or `plain`; `hem_line` 108-112 (full length).
- Arms: `sleeves: long` (hoodie) or `short` (tee); `ribbed cuffs` on hoodies.
- Legs: `type: trousers`; joggers (`waistband: elastic`, `cuffed ankles`, `side pockets`) or baggy jeans (`base_pattern: denim`, `waistband: plain`, `belt loops`, `button`).
- Patterns: `solid`; `denim` for jeans. No graphics.

## Palette
Off-white `#F5F5F2`, heather grey `#8E9199`, light wash `#9DB5D6`, soft sage `#B9C7A5`, black `#111111`. Shoes: white `#FFFFFF` / sole `#E4E4E4`.

## Garment menu
- Tops: plain hoodie (hood, drawstrings, kangaroo pocket), oversized tee (crew collar), zip hoodie (zip, hood).
- Bottoms: joggers, baggy light-wash jeans.
- Shoes: plain white or grey sneakers.

## Name words
Trend words: `trendy`, `aesthetic`, `hoodie`, `jeans`, `grey`, `white`, `black`.
Examples: "Grey Hoodie Jogger Aesthetic Outfit Top", "White Tee Baggy Jeans Trendy Outfit Pants".

## Moderation traps
- No chest marks, box labels or slogan text (this style is the most copied from real brands).
- No tech-fleece-style panel copies.

## Families and research (notes and links only)
- **Family fit:** Decorated. One small mark at most; use print only for a soft all-over faded pattern.
- **Motifs seen in current clothing:** Small stars, hearts, sparkles, daisies; clean basics carry the look.
- **Composition and inks:** Pocket motif plus an optional small back mark. Inks: one soft tone of the fabric colour.
- **Fabric and distress:** Heathered or mineral wash neutrals; no heavy distress.
- **Sources:** [Adobe Express: t-shirt trends 2025](https://www.adobe.com/uk/express/learn/blog/t-shirt-trends-2025), [Thrifted: vintage tee styles 2026](https://www.thrifted.com/blogs/the-edit/best-vintage-t-shirt-styles-in-2026), [2026 graphic tee trends](https://ootd.bearblog.dev/graphic-tee-trends-shaping-2026s-fashion-scene/)

## Decorated family (see [references/gen-z](../references/gen-z/sheet.png))
At most one small mark: `heart` / `star` / `sparkle` on `pocket` (size 5) and optionally one on `back`.
Use motifs from `tools/motifs.py` or library elements (`element: <id>`, see [library](../references/library/INDEX.md)); colours must be in the outfit palette.

## Owner artwork (44 imported elements fit this style)
Cut from the owner's generated sheets; use them like any library element (`element: <id>`), recoloured to one ink by default, or `original: true` to keep their colours (they then count toward the palette).

- Hero graphics (back / front print, about 90-110 px): `g01-number-07`, `g08-number-28`.
- Small motifs (chest, sleeve, 12-30 px): `g01-compass-sparkle`, `g01-crown-scribble`, `g01-double-slash`, `g01-heart-scribble`, `g01-heart-small`, `g01-orbit-star`, `g01-sparkle-pair`, `g01-star-outline` (print size only), `g01-star-solid`, `g01-stitch-x`, `g01-tribal-flame`, `g02-chrome-star`, `g02-orbit-star`, `g02-sparkle-4` and 8 more.
- Borders (`layout: border`, tiles round the hem / cuff): `g01-checker-border`, `g01-double-stripe-border`, `g01-flame-row`, `g01-stitch-dash-border`, `g04-checker-border`, `g04-heart-scribble-row`, `g04-star-row`, `g04-stripe-border`, `g06-checker-border`, `g08-checker-border`.
- Fabric swatches (`base_pattern: swatch`): `g01-checker-tile`, `g01-star-tile`, `g06-checker-patch`, `g08-rugby-stripe-swatch`.
- Garment parts (realistic family): `g01-stitched-patch`, `g01-zip-border`, `g08-raglan-yoke`, `g10-cargo-pocket`.
- Textures and distress (print overlays): `g01-grunge-texture`, `g01-halftone-fade`.
- Reference outfit: [examples/owner-gen-z.yaml](examples/owner-gen-z.yaml). All of them: [library/INDEX.md](../references/library/INDEX.md), sheet `../references/gen-z/library.png`.

## Realistic family
- Archetypes: basic_tee_jeans, crop_lowrise.
- Materials: cotton tee, denim jeans; nylon for track pieces.
- Plain basics are the point: let the folds, jeans stitching and sneakers carry it. Procedural shading reads cleanest on light tees.
- Reference: [examples/realistic-basic-tee-jeans.yaml](examples/realistic-basic-tee-jeans.yaml). Vary `shading.seed` across a batch; shading is always the default stack `own-shade-all`.

## Not drawable yet (flag, don't fake)
Graphic prints with text, puffer vests. (Cargo pockets: realistic family.)

## Example
[examples/gen-z.yaml](examples/gen-z.yaml) · preview [examples/previews/guide-gen-z/sheet.png](examples/previews/guide-gen-z/sheet.png) · and the golden outfit.

## Variations for a batch
1. Sage hoodie + sage joggers (monochrome set).
2. Black zip hoodie + light wash jeans.
3. Off-white tee + grey joggers.
4. Heather grey hoodie + black joggers.
