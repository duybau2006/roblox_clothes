# Seasonal: Christmas and winter

**Audience:** unisex, very wide in Nov-Dec. **Trend evidence:** 12 seasonal + 11 cozy catalog hits; "christmas" names were climbing in mid-November. **Library:** `seasonal`, `cozy-oversized-sweater` (roblox.yaml), `cozy-knit` (irl.yaml).
**Timing:** publish Christmas outfits by early December; switch to winter/Valentine's colours in January.

## The look
Red, green and white knits with matching cosy joggers or skirts.

## Spec settings
- Torso: knit sweater (`base_pattern: knit`), `hem: rib` white; `hem_line` 104-110. Horizontal `stripes` (width 4-8) in red/white for candy-stripe looks.
- Arms: `long`, `ribbed cuffs`.
- Legs: grey or red joggers (`waistband: elastic`, `cuffed ankles`, `side pockets`) or a red/green plaid skirt with white tights.
- Shoes: white sneakers or brown boots.

## Palette
Festive red `#B22222`, festive green `#1F5E3A`, snow white `#FFFFFF`, gold `#D4AF37`, heather grey `#8E9199`.

## Garment menu
- Tops: red, green or cream knit; red/white striped knit.
- Bottoms: grey joggers, red/green plaid pleated skirt + white tights.

## Name words
Trend words: `christmas`, `cute`, `sweater`, `aesthetic`, `vintage`. Don't use `sweater` as a style word when the garment word is already "Sweater".
Example: "Red Sweater Joggers Christmas Cute Outfit Top".

## Moderation traps
- No religious symbols and no licensed holiday characters.
- No alcohol (no mulled wine, beer or champagne motifs).

## Families and research (notes and links only)
- **Family fit:** Both. Decorated for knit sweaters with snow rows; print for a centred festive graphic.
- **Motifs seen in current clothing:** Stars, snowflakes, holly, candy canes, baubles, pine trees, bells, gingerbread.
- **Composition and inks:** Centred chest graphic or rows of small motifs. Inks: white, gold, red, green.
- **Fabric and distress:** Clean or heathered knits; light halftone at most.
- **Sources:** [Jiffy: 2025 Halloween tee trends](https://www.jiffy.com/blog/5-halloween-t-shirt-design-trends-for-2025), [Adobe Express: t-shirt trends 2025](https://www.adobe.com/uk/express/learn/blog/t-shirt-trends-2025)

## Decorated family (see [references/christmas](../references/christmas/sheet.png))
Gold `star` on `chest` (`pair: true`), `sparkle` as a snow `row`, `heart` accents; candy `stripes`, `cable` knit, tartan (`plaid`).
Use motifs from `tools/motifs.py` or library elements (`element: <id>`, see [library](../references/library/INDEX.md)); colours must be in the outfit palette.

## Owner artwork (41 imported elements fit this style)
Cut from the owner's generated sheets; use them like any library element (`element: <id>`), recoloured to one ink by default, or `original: true` to keep their colours (they then count toward the palette).

- Hero graphics (back / front print, about 90-110 px): `g03-candelabra`, `g07-winged-bow`.
- Small motifs (chest, sleeve, 12-30 px): `g07-bauble`, `g07-bunny-plush`, `g07-candles-greenery`, `g07-candy-cane-bow`, `g07-cocoa-mug`, `g07-earmuffs`, `g07-fawn-bow`, `g07-gingerbread-star`, `g07-gingham-bow`, `g07-gold-north-star`, `g07-gold-sparkles`, `g07-hanging-stars-bow`, `g07-heart-lollipop`, `g07-holly-bow` and 14 more.
- Borders (`layout: border`, tiles round the hem / cuff): `g07-gingham-ruffle-border`, `g07-lace-bow-border`, `g07-lace-bow-border-2`.
- Fabric swatches (`base_pattern: swatch`): `g07-cable-knit-swatch`, `g07-candy-stripe-swatch`, `g07-fairisle-swatch`, `g07-gingham-swatch`, `g07-plaid-swatch`, `g07-snowflake-swatch`, `g08-cable-knit-swatch`, `g08-tartan-swatch`.
- Reference outfit: [examples/owner-christmas.yaml](examples/owner-christmas.yaml). All of them: [library/INDEX.md](../references/library/INDEX.md), sheet `../references/christmas/library.png`.

## Realistic family
- Archetypes: knit_stripes in red / green / cream.
- Materials: heavy knit.
- Wrapped stripes on heavy knit with ribbed cuffs read as a winter sweater without any festive text.
- Reference: [examples/realistic-knit-stripes.yaml](examples/realistic-knit-stripes.yaml). Vary `shading.seed` across a batch; shading is always the default stack `own-shade-all`.

## Not drawable yet (flag, don't fake)
Reindeer / snowflake knit motifs, fur trim, Santa hats.

## Example
[examples/christmas.yaml](examples/christmas.yaml) · preview [examples/previews/guide-christmas/sheet.png](examples/previews/guide-christmas/sheet.png).

## Variations for a batch
1. Green knit with white rib + red plaid skirt + white tights.
2. Red/white striped knit + grey joggers.
3. Cream knit with red rib + red joggers.
4. Green hoodie + red joggers (matching set).
