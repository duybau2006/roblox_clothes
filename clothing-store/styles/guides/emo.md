# Emo / scene

**Audience:** unisex. **Trend evidence:** #3 style, 33 catalog hits; "emo" is the 3rd most-used name word. **Library:** `emo-scene` (roblox.yaml).

## The look
Black base with one loud accent (hot pink, purple or neon green), striped sleeves, skinny black jeans.

## Spec settings
- Torso: black hoodie or zip hoodie (`hood`, `zip`, `drawstrings`) or black tee; `hem: rib`; `hem_line` 108-112.
- Arms: striped sleeves = `sleeve_contrast: true` + `base_pattern: stripes` (width 4) in black + accent; or layered (`sleeves: short` + `arms.under` striped).
- Legs: `type: trousers`, black `denim`, `waistband: plain`, `belt loops`, `button`; or a black/accent plaid skirt with black tights.
- Shoes: black and white sneakers.

## Palette
Black `#111111`, hot pink `#FF1493`, purple `#7B2CBF`, neon green `#39FF14`, off-white `#EDEDED`.

## Garment menu
- Tops: black zip hoodie, black tee over striped long sleeve.
- Sleeves: black/accent stripes.
- Bottoms: black skinny jeans, black/pink plaid skirt + black tights.

## Name words
Trend words: `emo`, `y2k`, `black`, `grunge`, `goth`, `aesthetic`, `cute`.
Example: "Black Zip Hoodie Jeans Emo Y2K Outfit Top".

## Moderation traps
- No self-harm references, no skulls with gore, no band names or logos.
- Stripes stay plain horizontal bands: no three-stripe arrangements.

## Families and research (notes and links only)
- **Family fit:** Both. Print for a loud heart/skull graphic; decorated for striped sleeves, studs and chains.
- **Motifs seen in current clothing:** Broken and barbed hearts, stars, skulls, bats, lightning, chains, checkerboard; pink, purple or green ink on black.
- **Composition and inks:** Off-centre figure with an ornament (heart + dagger, skull + stars) or centred stack. Inks: hot pink, purple, neon green, white.
- **Fabric and distress:** Black or faded black; drips and halftone fades (drips 1-2, halftone 1-2). Recipe: `offcentre_figure`, tags [heart, dagger, star].
- **Sources:** [TeePublic: gothic heart designs](https://www.teepublic.com/t-shirts/gothic-heart), [RIPT: barbed wire tattoo-flash tee](https://riptapparel.com/hello-barbedwire/), [Hot Topic: winged skulls baby tee](https://www.hottopic.com/product/social-collision-winged-skulls-rhinestones-girls-baby-t-shirt-plus-size/31675310.html), [Adobe Express: t-shirt trends 2025](https://www.adobe.com/uk/express/learn/blog/t-shirt-trends-2025)

## Decorated family (see [references/emo](../references/emo/sheet.png))
`star` on `back` (`pair: true`), `heart` / `lightning` on `pocket`, `stud` as a `row`, `chain` on legs `hip_chain`, `rip` on `knees`; `stripes`, `checker`, `leopard` patterns.
Use motifs from `tools/motifs.py` or library elements (`element: <id>`, see [library](../references/library/INDEX.md)); colours must be in the outfit palette.

## Owner artwork (86 imported elements fit this style)
Cut from the owner's generated sheets; use them like any library element (`element: <id>`), recoloured to one ink by default, or `original: true` to keep their colours (they then count toward the palette).

- Hero graphics (back / front print, about 90-110 px): `g02-gothic-butterfly`, `g03-angel-wings`, `g03-crescent-moon`, `g03-raven-rose`, `g03-rose-leaves`, `g04-barbed-heart`, `g04-feather-wings`, `g04-spiky-star-drip`, `g06-skull-crest`.
- Small motifs (chest, sleeve, 12-30 px): `g01-crown-scribble`, `g01-devil-horns`, `g01-heart-scribble`, `g01-heart-small`, `g01-sparkle-pair`, `g01-star-outline` (print size only), `g01-star-solid`, `g01-stitch-x`, `g01-tribal-flame`, `g02-flame-heart`, `g03-bat`, `g03-bat-small`, `g03-heart-locket`, `g03-moth` and 21 more.
- Borders (`layout: border`, tiles round the hem / cuff): `g01-checker-border`, `g01-flame-row`, `g02-thorn-heart-row`, `g02-tribal-heart-border`, `g02-tribal-spike-border`, `g03-lace-border-2`, `g03-thorn-vine`, `g04-bar-stripe-border`, `g04-barbed-wire`, `g04-barbed-wire-2`, `g04-chain-border`, `g04-checker-border`, `g04-heart-chain-row`, `g04-heart-scribble-row` and 12 more.
- Fabric swatches (`base_pattern: swatch`): `g01-checker-tile`, `g01-star-tile`, `g02-leopard-swatch`, `g03-plaid-swatch`, `g06-checker-patch`, `g06-plaid-patch`, `g06-stripe-swatch`.
- Garment parts (realistic family): `g06-stitched-patch`.
- Textures and distress (print overlays): `g06-claw-rips`, `g06-claw-scratch`, `g06-paint-blot`, `g06-paint-drip-stroke`, `g06-scratch-marks`, `g06-slash-rips`, `g06-torn-hole`, `g10-ink-splatter`.
- Reference outfit: [examples/owner-emo.yaml](examples/owner-emo.yaml). All of them: [library/INDEX.md](../references/library/INDEX.md), sheet `../references/emo/library.png`.

## Realistic family
- Archetypes: basic_tee_jeans in black / dark denim, racing_jersey with a stencil number.
- Materials: black cotton, dark denim.
- Stencil numbers (digits only) give the band-tee energy without words or band names.
- Reference: [examples/realistic-basic-tee-jeans.yaml](examples/realistic-basic-tee-jeans.yaml). Vary `shading.seed` across a batch; shading is always the default stack `own-shade-all`.

## Not drawable yet (flag, don't fake)
Arm warmers, studded belts as a separate piece.

## Example
Print family: [examples/print-emo.yaml](examples/print-emo.yaml) · preview [examples/previews/print-emo/sheet.png](examples/previews/print-emo/sheet.png).  
Decorated family: [examples/emo.yaml](examples/emo.yaml) · preview [examples/previews/guide-emo/sheet.png](examples/previews/guide-emo/sheet.png) · layered version [tests/specs/test-layered-sleeves.yaml](../../tests/specs/test-layered-sleeves.yaml).

## Variations for a batch
1. Black hoodie + purple/black striped sleeves + black jeans.
2. Black tee over neon-green striped long sleeve + black jeans.
3. Black zip hoodie + black/pink plaid skirt + black tights (fem).
4. Grey hoodie + black/pink striped sleeves + black jeans.
