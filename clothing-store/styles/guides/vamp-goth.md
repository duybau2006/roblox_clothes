# Vamp / goth / vkei

**Audience:** mostly fem, some unisex. **Trend evidence:** #2 style, 37 catalog hits; "vamp", "goth" and "vkei" are trend name words. **Library:** `vamp-goth-vkei` (roblox.yaml).

## The look
Black with blood-wine red, knit or lace-look tops, plaid pleated skirts with opaque tights, platform boots.

## Spec settings
- Torso: black knit sweater or black zip hoodie; `hem: rib`; `hem_line` 100-108.
- Arms: `long` with `ribbed cuffs`; wine red rib trim.
- Legs: `type: skirt`, `base_pattern: plaid` black/wine, `pleats`, `skirt_length` 40-56, `legwear: tights` black; or black flared-look jeans (`denim`, black).
- Shoes: black boots.

## Palette
Black `#111111`, wine `#5C0A1E`, off-white `#E8E8E8`, muted purple `#5B4B8A`, grey `#8A8A8A`.

## Garment menu
- Tops: black knit sweater, black hoodie with wine trim.
- Bottoms: black/wine pleated plaid skirt + black tights, black jeans.
- Shoes: black platform boots.

## Name words
Trend words: `vamp`, `goth`, `vkei`, `black`, `emo`, `y2k`, `aesthetic`, `girl`.
Example: "Black Sweater Plaid Skirt Vamp Goth Outfit Top".

## Moderation traps
- No crosses (upright or inverted), no blood, no religious symbols.
- Lace and sheer looks are always drawn opaque; tights are never skin-coloured.
- No real visual-kei band names.

## Families and research (notes and links only)
- **Family fit:** Print first (large back prints sell the look); decorated for skirts, lace and small bats.
- **Motifs seen in current clothing:** Skulls with roses, wings, thorns, bats, moths, filigree, candles and gothic arches; tattoo-flash linework.
- **Composition and inks:** Large back print, minimal front. Symmetric pairs (wings around a skull or heart) and centred stacks. Inks: bone white, silver grey, deep wine.
- **Fabric and distress:** Faded black or washed black; distressed, parchment-like texture (level 1-2). Recipe: `symmetric_pair`, tags [skull, wings, rose], `placement: back`.
- **Sources:** [Sullen: gothic collection](https://sullenclothing.com/collections/gothic), [TeePublic: gothic heart designs](https://www.teepublic.com/t-shirts/gothic-heart), [Jiffy: 2025 Halloween tee trends](https://www.jiffy.com/blog/5-halloween-t-shirt-design-trends-for-2025), [2026 graphic tee trends](https://ootd.bearblog.dev/graphic-tee-trends-shaping-2026s-fashion-scene/)

## Decorated family (see [references/vamp-goth](../references/vamp-goth/sheet.png))
`bat` on `chest` (`pair: true`), `web` / `rose` / `moon` on `back`, `lace` on `lace_cuff` and skirt `lace_hem`, `lace_neck` for a collar.
Use motifs from `tools/motifs.py` or library elements (`element: <id>`, see [library](../references/library/INDEX.md)); colours must be in the outfit palette.

## Owner artwork (46 imported elements fit this style)
Cut from the owner's generated sheets; use them like any library element (`element: <id>`), recoloured to one ink by default, or `original: true` to keep their colours (they then count toward the palette).

- Hero graphics (back / front print, about 90-110 px): `g02-feather-wings`, `g02-gothic-butterfly`, `g02-rose-thorn-tribal`, `g02-thorn-heart-wings`, `g03-angel-wings`, `g03-candelabra`, `g03-chandelier`, `g03-crescent-moon`, `g03-gothic-window-roses`, `g03-raven-rose`, `g03-rose-leaves`, `g04-barbed-heart`, `g04-feather-wings`, `g06-skull-crest`.
- Small motifs (chest, sleeve, 12-30 px): `g01-compass-sparkle`, `g02-fleur-chrome`, `g03-bat`, `g03-bat-small`, `g03-compass-star`, `g03-filigree-corner`, `g03-fleur`, `g03-heart-locket`, `g03-moth`, `g03-spider-web` (print size only), `g03-thorn-branch`, `g03-velvet-bow`, `g06-fleur`, `g06-lion-knocker` and 3 more.
- Borders (`layout: border`, tiles round the hem / cuff): `g02-filigree-sparkle-border`, `g02-thorn-heart-row`, `g03-baroque-border`, `g03-lace-border`, `g03-lace-border-2`, `g03-rose-vine-border`, `g03-thorn-vine`, `g04-barbed-wire`, `g04-chain-border`, `g04-pyramid-studs`, `g04-spike-row`, `g06-barbed-wire`, `g06-torn-lace-edge`.
- Fabric swatches (`base_pattern: swatch`): `g03-plaid-swatch`, `g03-plaid-swatch-2`.
- Reference outfit: [examples/owner-vamp-goth.yaml](examples/owner-vamp-goth.yaml). All of them: [library/INDEX.md](../references/library/INDEX.md), sheet `../references/vamp-goth/library.png`.

## Realistic family
- Archetypes: corset_trousers, suit_waistcoat (black / burgundy).
- Materials: leather corset-style tops, satin, black cotton.
- Leather and satin get narrow bright highlights; keep straps 5 px or wider and the chest covered. No lingerie look.
- Reference: [examples/realistic-corset-trousers.yaml](examples/realistic-corset-trousers.yaml). Vary `shading.seed` across a batch; shading is always the default stack `own-shade-all`.

## Not drawable yet (flag, don't fake)
Ruffles, flared legs. (Corset-style lacing: realistic family.)

## Example
Print family: [examples/print-vamp-goth.yaml](examples/print-vamp-goth.yaml) · preview [examples/previews/print-vamp-goth/sheet.png](examples/previews/print-vamp-goth/sheet.png).  
Decorated family: [examples/vamp-goth.yaml](examples/vamp-goth.yaml) · preview [examples/previews/guide-vamp-goth/sheet.png](examples/previews/guide-vamp-goth/sheet.png).

## Variations for a batch
1. Wine knit sweater + black pleated skirt + black tights.
2. Black hoodie with wine trim + black jeans (unisex).
3. Purple/black plaid skirt + black knit + black tights.
4. Off-white knit with black trim + black plaid skirt.
