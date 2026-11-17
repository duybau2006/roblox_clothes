# Baddie / swag street

**Audience:** mostly fem. **Trend evidence:** #4 style, 27 catalog hits; "baddie" and "swag" are trend name words. **Library:** `baddie-street` (roblox.yaml).

## The look
Fitted crop tops in white or black, high-rise jeans, sneakers; confident and clean.

## Spec settings
- Torso: fitted crop tee; `hem: plain`; `hem_line` 84-90 with `legs.waist_line` 96-100 (gap max 16).
- Arms: `short`.
- Legs: `type: trousers`, black or mid-wash `denim`, `waistband: plain`, `belt loops`, `button` (silver accent).
- Shoes: black-and-white sneakers.

## Palette
Black `#111111`, white `#FFFFFF`, silver `#C0C0C0`, hot accent `#E0115F`; denim `#2A2A2A` or `#4A6FA5`.

## Garment menu
- Tops: white or black crop tee, hot-pink crop tee.
- Bottoms: black straight jeans, mid-wash jeans.
- Shoes: black/white sneakers.

## Name words
Trend words: `baddie`, `swag`, `y2k`, `black`, `white`, `trendy`, `aesthetic`.
Example: "White Crop Tee Jeans Baddie Swag Outfit Top".

## Moderation traps
- No tattoos drawn on skin-tone arms (common in competitors, often removed).
- No gang, money or weapon motifs; no game names ("da hood", "dh").
- Crop gap max 16 px; no bra-like tops.

## Families and research (notes and links only)
- **Family fit:** Both. Combined works best: a silver back print plus small pink chest and sleeve motifs.
- **Motifs seen in current clothing:** Winged hearts, butterflies, flames, chains, gems, crowns; rhinestone and chrome looks.
- **Composition and inks:** Centred stack on the back or a single chest graphic. Inks: silver, chrome grey, hot pink.
- **Fabric and distress:** Clean black or white fabric; little distress (0-1). Recipe: `centered_stack`, tags [heart, wings, chain].
- **Sources:** [Hot Topic: winged skulls baby tee](https://www.hottopic.com/product/social-collision-winged-skulls-rhinestones-girls-baby-t-shirt-plus-size/31675310.html), [Urban Outfitters: angel wings baby tee](https://www.urbanoutfitters.com/shop/angel-wings-rhinestone-graphic-baby-tee), [Gymshark: the baby tee trend](https://www.gymshark.com/blog/article/the-baby-tee-trend)

## Decorated family (see [references/baddie](../references/baddie/sheet.png))
Bold single `chest` graphic (`butterfly`, `heart`, `flame`), `chain` `necklace` with a `pendant`, legs `hip_chain`; `leopard` pattern.
Use motifs from `tools/motifs.py` or library elements (`element: <id>`, see [library](../references/library/INDEX.md)); colours must be in the outfit palette.

## Owner artwork (69 imported elements fit this style)
Cut from the owner's generated sheets; use them like any library element (`element: <id>`), recoloured to one ink by default, or `original: true` to keep their colours (they then count toward the palette).

- Hero graphics (back / front print, about 90-110 px): `g02-feather-wings`, `g02-gothic-butterfly`, `g02-rose-thorn-tribal`, `g02-thorn-heart-wings`, `g04-barbed-heart`, `g04-spiky-star-drip`, `g05-gem-heart-tribal`, `g05-rhinestone-orbit-star`.
- Small motifs (chest, sleeve, 12-30 px): `g01-crown-scribble`, `g01-devil-horns`, `g01-heart-small`, `g01-orbit-star`, `g01-sparkle-pair`, `g01-tribal-flame`, `g02-chrome-star`, `g02-dotted-butterfly` (print size only), `g02-flame-heart`, `g02-glitter-butterfly`, `g02-heart-trio`, `g02-lily-glint`, `g02-orbit-heart`, `g02-orbit-star` and 31 more.
- Borders (`layout: border`, tiles round the hem / cuff): `g02-filigree-sparkle-border`, `g02-flame-border`, `g02-rhinestone-heart-row`, `g02-sparkle-row`, `g02-thorn-heart-row`, `g02-tribal-butterfly-border`, `g02-tribal-heart-border`, `g02-tribal-spike-border`, `g04-chain-border`, `g04-heart-chain-row`, `g05-chrome-tribal-flame`, `g05-tribal-butterfly`, `g05-tribal-sparkle-border`.
- Fabric swatches (`base_pattern: swatch`): `g02-leopard-strip`, `g02-leopard-swatch`, `g05-leopard-swatch`.
- Reference outfit: [examples/owner-baddie.yaml](examples/owner-baddie.yaml). All of them: [library/INDEX.md](../references/library/INDEX.md), sheet `../references/baddie/library.png`.

## Realistic family
- Archetypes: crop_lowrise, corset_trousers in satin, halter separates.
- Materials: satin, leather, light denim.
- Cut-outs are always transparent and ordinary clothing; sell separates with `coverage: top_only` / `bottom_only`.
- Reference: [examples/realistic-crop-lowrise.yaml](examples/realistic-crop-lowrise.yaml). Vary `shading.seed` across a batch; shading is always the default stack `own-shade-all`.

## Not drawable yet (flag, don't fake)
Leg warmers. (Tank straps and shorts: realistic family.)

## Example
Print family: [examples/combined-baddie.yaml](examples/combined-baddie.yaml) · preview [examples/previews/combined-baddie/sheet.png](examples/previews/combined-baddie/sheet.png).  
Decorated family: [examples/baddie.yaml](examples/baddie.yaml) · preview [examples/previews/guide-baddie/sheet.png](examples/previews/guide-baddie/sheet.png).

## Variations for a batch
1. Black crop tee + mid-wash jeans.
2. Hot pink crop tee + black jeans.
3. White crop zip hoodie + black jeans.
4. Black crop tee + white solid trousers.
