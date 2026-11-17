# Y2K

**Audience:** mostly fem, some unisex. **Trend evidence:** #1 style, 54 catalog hits; "y2k" is the most-used name word (51). **Library:** `y2k` (irl.yaml), `y2k-crop-cargo` (roblox.yaml).

## The look
Early-2000s: cropped tops, low-to-mid rise jeans, baby pastels with silver, chunky sneakers.

## Spec settings
- Torso: crop tee or cropped zip hoodie; `hem_line` 84-92 with `legs.waist_line` up to 16 px lower (crop gap max 16). Full-length baby tees are fine too.
- Arms: `short` for baby tees, `long` + `ribbed cuffs` for hoodies.
- Legs: `type: trousers`, `base_pattern: denim` light or mid wash, `waistband: plain`, `belt loops`, `button`, `side pockets`.
- Patterns: `solid` tops; `stripes` (width 4) for baby tees.

## Palette
Baby pink `#F7B6D2`, lilac `#C8A2C8`, sky blue `#8FD3FF`, silver `#C9CED6`, white `#FFFFFF`; denim `#9DB5D6` / `#4A6FA5`.

## Garment menu
- Tops: cropped baby tee (crew collar), cropped zip hoodie (hood, zip, drawstrings).
- Bottoms: light-wash straight jeans, mid-wash jeans.
- Shoes: chunky white sneakers (`shoe_palette: ["#FFFFFF", "#C9CED6"]`).

## Name words
Trend words: `y2k`, `cute`, `aesthetic`, `trendy`, `jeans`, `girl`. `star` only when the outfit has star decorations.
Example: "Lilac Zip Hoodie Jeans Y2K Cute Outfit Top".

## Moderation traps
- Crop gap never more than 16 px; no skin-tone fabric in the gap.
- No bra-like crop tops, no rhinestone monograms, no butterfly logos that copy brands.
- Never use "da hood" / "dh" in names even though competitors do.

## Families and research (notes and links only)
- **Family fit:** Both. Decorated for scattered sparkles and pocket motifs; print for all-over faded butterflies or one centred butterfly / wings graphic.
- **Motifs seen in current clothing:** Butterflies, angel wings, stars, hearts and sparkle on fitted baby tees; rhinestone finishes; kitschy, playful graphics.
- **Composition and inks:** Centred chest graphic on baby tees, or all-over small motifs. Inks: white, silver, baby pink or lilac on pastel or white fabric.
- **Fabric and distress:** Mineral wash pastels; light distress (level 0-1, halftone fade). Recipe: `template: allover_faded` or `centered_stack`, tags [butterfly, star, sparkle].
- **Sources:** [Urban Outfitters: rhinestone butterfly baby tee](https://www.urbanoutfitters.com/shop/butterfly-rhinestone-graphic-baby-tee), [Urban Outfitters: angel wings baby tee](https://www.urbanoutfitters.com/shop/angel-wings-rhinestone-graphic-baby-tee), [Gymshark: the baby tee trend](https://www.gymshark.com/blog/article/the-baby-tee-trend), [Adobe Express: t-shirt trends 2025](https://www.adobe.com/uk/express/learn/blog/t-shirt-trends-2025), [Who What Wear: graphic tees summer 2026](https://www.whowhatwear.com/fashion/trends/graphic-t-shirts-women-summer-2026)

## Decorated family (see [references/y2k](../references/y2k/sheet.png))
butterfly on `pocket` or `back` (with `pair: true`), `sparkle` / `star` `scatter` on sleeves and jeans (size 3), `heart` or `flame` on `chest`; `leopard` pattern for tops.
Use motifs from `tools/motifs.py` or library elements (`element: <id>`, see [library](../references/library/INDEX.md)); colours must be in the outfit palette.

## Owner artwork (65 imported elements fit this style)
Cut from the owner's generated sheets; use them like any library element (`element: <id>`), recoloured to one ink by default, or `original: true` to keep their colours (they then count toward the palette).

- Hero graphics (back / front print, about 90-110 px): `g02-feather-wings`, `g02-gothic-butterfly`, `g02-rose-thorn-tribal`, `g02-thorn-heart-wings`, `g03-angel-wings`, `g03-crescent-moon`, `g05-gem-heart-tribal`, `g05-rhinestone-orbit-star`, `g07-winged-bow`.
- Small motifs (chest, sleeve, 12-30 px): `g01-compass-sparkle`, `g01-crown-scribble`, `g01-devil-horns`, `g01-double-slash`, `g01-heart-scribble`, `g01-orbit-star`, `g01-sparkle-pair`, `g01-star-outline` (print size only), `g01-tribal-flame`, `g02-chrome-star`, `g02-dotted-butterfly` (print size only), `g02-flame-heart`, `g02-fleur-chrome`, `g02-glitter-butterfly` and 25 more.
- Borders (`layout: border`, tiles round the hem / cuff): `g01-flame-row`, `g02-filigree-sparkle-border`, `g02-flame-border`, `g02-rhinestone-heart-row`, `g02-sparkle-row`, `g02-thorn-heart-row`, `g02-tribal-butterfly-border`, `g02-tribal-heart-border`, `g02-tribal-spike-border`, `g05-chrome-tribal-flame`, `g05-tribal-butterfly`, `g05-tribal-sparkle-border`.
- Fabric swatches (`base_pattern: swatch`): `g01-star-tile`, `g02-leopard-strip`, `g02-leopard-swatch`, `g05-leopard-swatch`.
- Textures and distress (print overlays): `g01-halftone-fade`.
- Reference outfit: [examples/owner-y2k.yaml](examples/owner-y2k.yaml). All of them: [library/INDEX.md](../references/library/INDEX.md), sheet `../references/y2k/library.png`.

## Realistic family
- Archetypes: crop_lowrise, halter top (`cut: {style: halter}`, `coverage: top_only`).
- Materials: satin or cotton baby tees, light denim.
- Low-rise + baby tee is the core y2k silhouette; keep the crop gap at most 16 px and use belts / jeans stitching rather than graphics.
- Reference: [examples/realistic-crop-lowrise.yaml](examples/realistic-crop-lowrise.yaml). Vary `shading.seed` across a batch; shading is always the default stack `own-shade-all`.

## Not drawable yet (flag, don't fake)
Flared legs, mini skirts over leggings, rhinestone text. (Cargo pockets: realistic family.)

## Example
Print family: [examples/print-y2k.yaml](examples/print-y2k.yaml) · preview [examples/previews/print-y2k/sheet.png](examples/previews/print-y2k/sheet.png).  
Decorated family: [examples/y2k.yaml](examples/y2k.yaml) · preview [examples/previews/guide-y2k/sheet.png](examples/previews/guide-y2k/sheet.png) · also [tests/specs/test-crop-top.yaml](../../tests/specs/test-crop-top.yaml).

## Variations for a batch
1. Pink baby tee crop + light-wash jeans.
2. Sky blue cropped zip hoodie + mid-wash jeans.
3. White baby tee with pink stripes (full length) + silver-grey joggers.
4. Lilac hoodie (full length) + white jeans-look trousers (solid white).
