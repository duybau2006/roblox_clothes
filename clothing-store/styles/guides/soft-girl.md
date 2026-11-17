# Soft girl / coquette / cute pastel

**Audience:** fem. **Trend evidence:** soft girl 9 + kawaii 8 + skirts 8 catalog hits; "cute" and "girl" are trend name words. **Library:** `soft-girl`, `kawaii` (roblox.yaml), `coquette` (irl.yaml).

## The look
Pastel knits, pleated skirts, white knee socks, sneakers or flats.

## Spec settings
- Torso: pastel knit sweater (`base_pattern: knit`) or plain hoodie; `hem: rib`; `hem_line` 100-108.
- Arms: `long`, `ribbed cuffs` in white.
- Legs: `type: skirt`, `pleats`, `skirt_length` 40-52; `legwear: socks` white with `sock_top` 70-76, or white tights.
- Shoes: pastel sneakers.

## Palette
Pink `#F7B6D2`, lilac `#C8A2C8`, baby blue `#A7C7E7`, cream `#F3EBDD`, white `#FFFFFF`.

## Garment menu
- Tops: pink, lilac or cream knit sweater; pastel hoodie.
- Bottoms: pastel pleated skirt (solid or small plaid), light jeans.
- Legwear: white knee socks, white tights.

## Name words
Trend words: `cute`, `girl`, `aesthetic`, `y2k`, `trendy`, `preppy` (blend).
Example: "Pink Sweater Pleated Skirt Cute Girl Outfit Top".

## Moderation traps
- Skirt at least 32 rows with bare legs or socks (24 with tights); no very short skirts.
- No skin-tone fabric or sheer cardigans; no licensed mascots (Hello Kitty and similar).

## Families and research (notes and links only)
- **Family fit:** Decorated. Bows, hearts and lace read better small; a print is fine as an all-over faded heart/bow pattern.
- **Motifs seen in current clothing:** Bows, hearts, gingham, cherries, ditsy florals, lace, soft pastels.
- **Composition and inks:** Chest bow + scattered hearts, or all-over faded small motifs. Inks: white or a deeper pastel.
- **Fabric and distress:** Clean pastels or mineral wash pastels; no distress.
- **Sources:** [Business of Fashion: coquette explained](https://businessoffashion.com/articles/marketing-pr/coquette-trend-explained/), [Gymshark: the baby tee trend](https://www.gymshark.com/blog/article/the-baby-tee-trend)

## Decorated family (see [references/soft-girl](../references/soft-girl/sheet.png))
`bow` on `chest`, `heart` `scatter` (size 2.5), `flower` / `cherry` scatter on skirts, `lace` on skirt `lace_hem` or `lace_neck`; gingham (`plaid` with pastel + white).
Use motifs from `tools/motifs.py` or library elements (`element: <id>`, see [library](../references/library/INDEX.md)); colours must be in the outfit palette.

## Owner artwork (89 imported elements fit this style)
Cut from the owner's generated sheets; use them like any library element (`element: <id>`), recoloured to one ink by default, or `original: true` to keep their colours (they then count toward the palette).

- Hero graphics (back / front print, about 90-110 px): `g02-feather-wings`, `g03-angel-wings`, `g03-rose-leaves`, `g07-winged-bow`, `g09-bow-wreath-birds`, `g09-lace-heart-flowers`, `g09-lily-bouquet`, `g09-toadstools`.
- Small motifs (chest, sleeve, 12-30 px): `g01-heart-scribble`, `g02-dotted-butterfly` (print size only), `g02-glitter-butterfly`, `g02-heart-trio`, `g02-lily-glint`, `g02-orbit-heart`, `g02-rhinestone-butterfly` (print size only), `g02-rhinestone-heart` (print size only), `g02-sparkle-4`, `g02-sparkle-4b`, `g02-sparkle-cluster` (print size only), `g03-heart-locket`, `g03-velvet-bow`, `g05-cherry-hearts-bow` and 47 more.
- Borders (`layout: border`, tiles round the hem / cuff): `g02-rhinestone-heart-row`, `g02-sparkle-row`, `g03-lace-border`, `g03-lace-border-2`, `g03-rose-vine-border`, `g07-gingham-ruffle-border`, `g07-lace-bow-border`, `g07-lace-bow-border-2`, `g09-bow-flower-border`, `g09-eyelet-border`, `g09-eyelet-border-2`, `g09-flower-vine-border`, `g09-gingham-ruffle-border`, `g09-rose-vine-border`.
- Fabric swatches (`base_pattern: swatch`): `g07-cable-knit-swatch`, `g07-candy-stripe-swatch`, `g07-gingham-swatch`, `g07-plaid-swatch`, `g07-snowflake-swatch`, `g09-patchwork-swatch`.
- Reference outfit: [examples/owner-soft-girl.yaml](examples/owner-soft-girl.yaml). All of them: [library/INDEX.md](../references/library/INDEX.md), sheet `../references/soft-girl/library.png`.

## Realistic family
- Archetypes: pleated_skirt_bows, off-shoulder blouse (`cut: {style: off_shoulder}`).
- Materials: cotton, satin.
- Bows come from the library as small decor on top of the realistic garment.
- Reference: [examples/realistic-pleated-skirt-bows.yaml](examples/realistic-pleated-skirt-bows.yaml). Vary `shading.seed` across a batch; shading is always the default stack `own-shade-all`.

## Not drawable yet (flag, don't fake)
Puff sleeves, cardigan buttons, leg warmers.

## Example
[examples/soft-girl.yaml](examples/soft-girl.yaml) · preview [examples/previews/guide-soft-girl/sheet.png](examples/previews/guide-soft-girl/sheet.png).

## Variations for a batch
1. Lilac knit + white pleated skirt + white socks.
2. Baby blue hoodie + pink plaid skirt + white tights.
3. Cream knit + baby pink pleated skirt.
4. Pink hoodie + light-wash jeans.
