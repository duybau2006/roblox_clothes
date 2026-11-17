# Athleisure / sporty

**Audience:** mostly masc, unisex. **Trend evidence:** not a Roblox catalog leader (streetwear sets: 13), but a steady masc basic and an easy matching set. **Library:** `athleisure` (irl.yaml), `sports-kits` (roblox.yaml).

## The look
Zip track jackets and joggers in black, grey and one soft accent, with running shoes.

## Spec settings
- Torso: zip jacket (`zip`, crew collar) or hoodie; `hem: rib`; `hem_line` 108-112.
- Arms: `long`, `ribbed cuffs`. Colour-block sleeves only with `sleeve_contrast: true`.
- Legs: joggers, `waistband: elastic`, `drawstrings`, `side pockets`, `cuffed ankles`.
- Shoes: running shoes in the accent colour.

## Palette
Black `#151515`, heather grey `#A6A6A6`, sage `#9CAF88`, lilac `#C8A2C8`, white `#F2F2F2`.

## Garment menu
- Tops: black or grey zip track jacket, plain hoodie.
- Bottoms: heather grey or black joggers.
- Shoes: accent-colour running shoes (`["#9CAF88", "#F2F2F2"]`).

## Name words
Trend words: `trendy`, `aesthetic`, `black`, `grey`, `hoodie`.
Example: "Black Zip Jacket Joggers Trendy Outfit Top".

## Moderation traps
- Never three parallel stripes or side tape down the legs or sleeves; no swoosh-like curves.
- No real team colours with crests, no league logos or player numbers.

## Families and research (notes and links only)
- **Family fit:** Decorated. Small marks on chest and sleeve; avoid stripes down the side.
- **Motifs seen in current clothing:** Lightning, chevrons, waves, target rings, arrows, hexagons.
- **Composition and inks:** Pocket + sleeve placement; at most a mid-size chest mark. Inks: one accent colour.
- **Fabric and distress:** Heathered fabric; no distress.
- **Sources:** [Adobe Express: t-shirt trends 2025](https://www.adobe.com/uk/express/learn/blog/t-shirt-trends-2025)

## Decorated family (see [references/athleisure](../references/athleisure/sheet.png))
`lightning` or `star` on `pocket` and arms `sleeve`; `colour-block`; never side stripes.
Use motifs from `tools/motifs.py` or library elements (`element: <id>`, see [library](../references/library/INDEX.md)); colours must be in the outfit palette.

## Owner artwork (27 imported elements fit this style)
Cut from the owner's generated sheets; use them like any library element (`element: <id>`), recoloured to one ink by default, or `original: true` to keep their colours (they then count toward the palette).

- Hero graphics (back / front print, about 90-110 px): `g01-number-07`, `g08-number-28`.
- Small motifs (chest, sleeve, 12-30 px): `g01-double-slash`, `g08-chevron-navy`, `g08-chevron-wine`, `g08-laurel-ball`, `g08-laurel-bow`, `g08-laurel-rackets`, `g08-sparkle-4`, `g08-tennis-rackets`, `g08-three-stars`, `g08-track-lanes`.
- Borders (`layout: border`, tiles round the hem / cuff): `g01-checker-border`, `g01-double-stripe-border`, `g08-checker-border`, `g08-stripe-border-navy`, `g08-stripe-border-wine`.
- Fabric swatches (`base_pattern: swatch`): `g08-argyle-swatch`, `g08-rib-stripe`, `g08-rugby-stripe-swatch`.
- Garment parts (realistic family): `g01-zip-border`, `g08-piping-arc`, `g08-polo-collar`, `g08-raglan-yoke`, `g08-sleeve-panel`, `g08-sleeve-panel-wine`, `g10-cargo-pocket`.
- Reference outfit: [examples/owner-athleisure.yaml](examples/owner-athleisure.yaml). All of them: [library/INDEX.md](../references/library/INDEX.md), sheet `../references/athleisure/library.png`.

## Realistic family
- Archetypes: racing_jersey, sports_shorts.
- Materials: nylon, cotton.
- Numbers 0-99 in racing / block / varsity lettering, invented side panels and one-line piping. Never real team kits, sponsors or three-stripe looks.
- Reference: [examples/realistic-sports-shorts.yaml](examples/realistic-sports-shorts.yaml). Vary `shading.seed` across a batch; shading is always the default stack `own-shade-all`.

## Not drawable yet (flag, don't fake)
Quarter-zip collars, leggings. (Side piping and jersey numbers: realistic family.)

## Example
[examples/athleisure.yaml](examples/athleisure.yaml) · preview [examples/previews/guide-athleisure/sheet.png](examples/previews/guide-athleisure/sheet.png).

## Variations for a batch
1. Grey zip jacket + black joggers + lilac shoes (unisex).
2. Sage zip jacket + sage joggers (monochrome set).
3. Black hoodie + grey joggers + white shoes.
4. Black jacket with grey contrast sleeves (`sleeve_contrast: true`) + black joggers.
