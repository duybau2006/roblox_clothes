# Grunge

**Audience:** mostly masc, unisex. **Trend evidence:** dark grunge 23 catalog hits; "grunge" and "ripped" are trend name words. **Library:** `grunge` (irl.yaml), `dark-grunge-boy` (roblox.yaml).

## The look
90s worn-in: plaid flannel, dark washed jeans, boots, faded reds and mossy greens over black.

## Spec settings
- Torso: plaid flannel (`base_pattern: plaid`) or dark hoodie; `hem: plain`; `hem_line` 110-114.
- Arms: `long`, plain cuffs for flannel; layered look = `sleeves: short` + `arms.under` dark long sleeve.
- Legs: `type: trousers`, `base_pattern: denim` washed black or charcoal, `waistband: plain`, `belt loops`, `button`.
- Shoes: black or dark brown boots.

## Palette
Black `#141414`, charcoal `#3A3A3A`, faded red `#9B3B3B`, moss `#5E6B47`; denim `#2A2A2A`.

## Garment menu
- Tops: plaid flannel (crew collar), black hoodie (hood, drawstrings), layered tee over long sleeve.
- Bottoms: washed black jeans, charcoal jeans.
- Shoes: black boots (`["#141414", "#2A2A2A"]`).

## Name words
Trend words: `grunge`, `vintage`, `black`, `aesthetic`, `emo` (blend). `ripped` only when the outfit has `rip` decorations.
Example: "Red Flannel Jeans Grunge Vintage Outfit Top".

## Moderation traps
- No band names or band-style logos (the most common grunge takedown).
- Distressing never shows skin over the hips; no blood-red splatter.

## Families and research (notes and links only)
- **Family fit:** Print first (acid wash + cracked front print); decorated for rips, pins and patches on the legs.
- **Motifs seen in current clothing:** Skulls, barbed wire, flames, thorns, moths, roses; tattoo-flash and band-merch-style compositions (never real band names).
- **Composition and inks:** Bold centred front print or large back print on an oversized tee. Inks: off-white, faded red, washed grey.
- **Fabric and distress:** Acid wash or mineral wash fabric; heavy cracked ink and worn patches (level 2-3). Recipe: `centered_stack`, tags [skull, barbed-wire, flame].
- **Sources:** [RIPT: barbed wire tattoo-flash tee](https://riptapparel.com/hello-barbedwire/), [Sullen: streetwear graphic tees](https://sullenclothing.com/es/collections/streetwear-graphic-tees), [Fashion Week Online: distressed shirts](https://fashionweekonline.com/how-to-style-distressed-shirts-for-a-modern-streetwear-look), [You Apparel: 2025 oversized acid wash](https://www.youapparel.com/blog/t-shirt-trends-2025-oversized-acid-wash-double-sleeve-streetwear), [Gooten: mineral wash tees](https://www.gooten.com/blog/design-ideas-mineralwash-tshirts/)

## Decorated family (see [references/grunge](../references/grunge/sheet.png))
`rip` on legs `knees` (`both: true` adds a back-of-knee rip), `safety_pin` on legs `pin`, `chain` on legs `hip_chain`, `patch` on torso; `plaid`, `stripes`, `checker` patterns.
Use motifs from `tools/motifs.py` or library elements (`element: <id>`, see [library](../references/library/INDEX.md)); colours must be in the outfit palette.

## Owner artwork (83 imported elements fit this style)
Cut from the owner's generated sheets; use them like any library element (`element: <id>`), recoloured to one ink by default, or `original: true` to keep their colours (they then count toward the palette).

- Hero graphics (back / front print, about 90-110 px): `g01-number-07`, `g03-raven-rose`, `g04-barbed-heart`, `g04-feather-wings`, `g04-spiky-star-drip`, `g06-skull-crest`.
- Small motifs (chest, sleeve, 12-30 px): `g01-devil-horns`, `g01-star-outline` (print size only), `g01-star-solid`, `g01-stitch-x`, `g03-bat`, `g03-moth`, `g03-spider-web` (print size only), `g03-thorn-branch`, `g04-broken-heart`, `g04-chain-pin-heart`, `g04-lightning-slash`, `g04-plaster-x`, `g04-scratched-broken-heart`, `g04-split-heart-drip` and 12 more.
- Borders (`layout: border`, tiles round the hem / cuff): `g01-checker-border`, `g01-flame-row`, `g01-stitch-dash-border`, `g03-thorn-vine`, `g04-bar-stripe-border`, `g04-barbed-wire`, `g04-barbed-wire-2`, `g04-chain-border`, `g04-checker-border`, `g04-pyramid-studs`, `g04-spike-row`, `g04-star-row`, `g04-star-scratch-row`, `g04-stripe-border` and 10 more.
- Fabric swatches (`base_pattern: swatch`): `g01-checker-tile`, `g03-plaid-swatch`, `g03-plaid-swatch-2`, `g06-checker-patch`, `g06-plaid-patch`, `g06-stripe-swatch`, `g08-tartan-swatch`, `g10-distressed-swatch`.
- Garment parts (realistic family): `g01-stitched-patch`, `g06-stitched-patch`, `g10-grommet-patch`, `g10-patchwork-stack`, `g10-torn-patch`.
- Textures and distress (print overlays): `g01-grunge-texture`, `g01-halftone-fade`, `g06-claw-rips`, `g06-claw-scratch`, `g06-paint-blot`, `g06-paint-drip-stroke`, `g06-scratch-marks`, `g06-slash-rips`, `g06-smear`, `g06-torn-hole`, `g10-distress-smear`, `g10-ink-splatter`, `g10-torn-canvas`, `g10-torn-fabric`.
- Reference outfit: [examples/owner-grunge.yaml](examples/owner-grunge.yaml). All of them: [library/INDEX.md](../references/library/INDEX.md), sheet `../references/grunge/library.png`.

## Realistic family
- Archetypes: basic_tee_jeans (washed black + grey denim), knit_stripes in muted tones, bomber_badge.
- Materials: heavy knit, denim, cotton.
- Pair a muted stripe knit with dark denim and boots; collected layers add worn depth on mid tones.
- Reference: [examples/realistic-knit-stripes.yaml](examples/realistic-knit-stripes.yaml). Vary `shading.seed` across a batch; shading is always the default stack `own-shade-all`.

## Not drawable yet (flag, don't fake)
Open flannel over a tee, frayed hems. (Laced boots: `shoe_style: boot`.)

## Example
Print family: [examples/print-grunge.yaml](examples/print-grunge.yaml) · preview [examples/previews/print-grunge/sheet.png](examples/previews/print-grunge/sheet.png).  
Decorated family: [examples/grunge.yaml](examples/grunge.yaml) · preview [examples/previews/guide-grunge/sheet.png](examples/previews/guide-grunge/sheet.png).

## Variations for a batch
1. Green/navy plaid flannel + charcoal jeans.
2. Black hoodie + washed black jeans + boots.
3. Black short-sleeve tee over a faded-red long sleeve (layered) + black jeans.
4. Moss green hoodie + black jeans.
