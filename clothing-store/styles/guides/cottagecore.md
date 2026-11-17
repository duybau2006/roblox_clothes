# Cottagecore / vintage

**Audience:** fem. **Trend evidence:** 7 catalog hits; "cottage core" and "vintage" are trend name words. **Library:** `cottagecore-vintage` (roblox.yaml), `cottagecore` (irl.yaml).

## The look
Sage, cream and dusty rose knits with long gingham or check skirts and brown boots.

## Spec settings
- Torso: knit sweater (`base_pattern: knit`), crew collar; `hem: rib` cream; `hem_line` 100-108.
- Arms: `long`, `ribbed cuffs`.
- Legs: `type: skirt`, `base_pattern: plaid` (reads as gingham), `skirt_length` 80-96 for long skirts; `legwear: bare` is fine with long skirts, or cream socks.
- Shoes: brown boots.

## Palette
Sage `#9CAF88`, cream `#F3EBDD`, dusty rose `#C99A9E`, mustard `#D9A93F`, brown `#6B4A2B`.

## Garment menu
- Tops: sage, cream or mustard knit sweater.
- Bottoms: long cream/rose check skirt, long sage skirt (solid).
- Shoes: brown boots (`["#6B4A2B", "#3B2A1E"]`).

## Name words
Trend words: `cottage core`, `vintage`, `cute`, `aesthetic`, `girl`. Names get long quickly: use one or two style words.
Example: "Sage Sweater Long Skirt Cottage Core Outfit Top".

## Moderation traps
- No leaf shapes that read as drug plants; no see-through linen.
- Dark brown tights read as a skin tone to the validator: use bare legs, cream socks or black tights.

## Families and research (notes and links only)
- **Family fit:** Decorated. Ditsy florals and lace; a soft all-over faded floral print also works.
- **Motifs seen in current clothing:** Small flowers, mushrooms, strawberries, cherries, bows, gingham, lace collars.
- **Composition and inks:** Scattered small motifs or all-over faded florals. Inks: dusty rose, cream, sage.
- **Fabric and distress:** Mineral wash or heathered naturals; no distress.
- **Sources:** [Bustle: cottagecore 2025](https://www.bustle.com/style/spicy-cottagecore-outfits-spring-2025), [Business of Fashion: coquette explained](https://businessoffashion.com/articles/marketing-pr/coquette-trend-explained/)

## Decorated family (see [references/cottagecore](../references/cottagecore/sheet.png))
`flower` `scatter` (size 2.6, spacing 13) on knits, `cherry` / `bow` accents, `lace_neck` collar, skirt `lace_hem`; gingham (`plaid`), `knit`.
Use motifs from `tools/motifs.py` or library elements (`element: <id>`, see [library](../references/library/INDEX.md)); colours must be in the outfit palette.

## Owner artwork (53 imported elements fit this style)
Cut from the owner's generated sheets; use them like any library element (`element: <id>`), recoloured to one ink by default, or `original: true` to keep their colours (they then count toward the palette).

- Hero graphics (back / front print, about 90-110 px): `g03-rose-leaves`, `g09-bow-wreath-birds`, `g09-garden-gate`, `g09-lace-heart-flowers`, `g09-lily-bouquet`, `g09-toadstools`.
- Small motifs (chest, sleeve, 12-30 px): `g02-lily-glint`, `g03-velvet-bow`, `g07-blossom-branch`, `g07-candles-greenery`, `g07-fawn-bow`, `g07-gingham-bow`, `g07-lace-bow`, `g07-lace-heart-roses`, `g07-lily-of-valley`, `g07-pearl-heart-bow`, `g07-pinecones-bow`, `g07-pink-rose`, `g07-snow-cherries`, `g09-butterfly` and 17 more.
- Borders (`layout: border`, tiles round the hem / cuff): `g03-lace-border`, `g03-lace-border-2`, `g03-rose-vine-border`, `g07-gingham-ruffle-border`, `g07-lace-bow-border`, `g07-lace-bow-border-2`, `g09-bow-flower-border`, `g09-eyelet-border`, `g09-eyelet-border-2`, `g09-flower-vine-border`, `g09-gingham-ruffle-border`, `g09-rose-vine-border`.
- Fabric swatches (`base_pattern: swatch`): `g07-gingham-swatch`, `g09-gingham-sage`, `g09-gingham-sage-2`, `g09-patchwork-swatch`.
- Reference outfit: [examples/owner-cottagecore.yaml](examples/owner-cottagecore.yaml). All of them: [library/INDEX.md](../references/library/INDEX.md), sheet `../references/cottagecore/library.png`.

## Realistic family
- Archetypes: off-shoulder blouse + midi skirt (see tests/specs/test-off-shoulder.yaml), knit_stripes in sage / cream.
- Materials: cotton, knit.
- Shading is the default stack `own-shade-all` like every outfit.
- Reference: [examples/realistic-pleated-skirt-bows.yaml](examples/realistic-pleated-skirt-bows.yaml). Vary `shading.seed` across a batch; shading is always the default stack `own-shade-all`.

## Not drawable yet (flag, don't fake)
Aprons, puff sleeves, overalls.

## Example
[examples/cottagecore.yaml](examples/cottagecore.yaml) · preview [examples/previews/guide-cottagecore/sheet.png](examples/previews/guide-cottagecore/sheet.png).

## Variations for a batch
1. Cream knit + long sage check skirt.
2. Mustard knit + long cream skirt.
3. Dusty rose knit + long cream/sage check skirt.
4. Sage knit + light jeans (casual).
