# Preppy / old money

**Audience:** masc and fem. **Trend evidence:** 10 catalog hits; "preppy" is a trend name word. **Library:** `preppy-old-money` (roblox.yaml), `old-money`, `preppy-varsity` (irl.yaml).

## The look
Navy, cream and forest knits; chinos or plaid pleated skirts; loafers. Quiet, expensive-looking, no logos.

## Spec settings
- Torso: knit sweater (`base_pattern: knit`), crew collar; `hem: rib` in a contrast colour; `hem_line` 104-110.
- Arms: `long`, `ribbed cuffs`; varsity look = `sleeve_contrast: true` with cream sleeves.
- Legs (masc): `type: trousers`, solid khaki/navy chinos, `waistband: plain`, `belt loops`, `button`, `side pockets`.
- Legs (fem): `type: skirt`, plaid `pleats`, `skirt_length` 40-48, white socks.
- Shoes: brown or black loafers.

## Palette
Navy `#1C2A4A`, cream `#F3EBDD`, forest `#2E4A36`, burgundy `#7A1F2B`, khaki `#9C8A5E` (darker khaki avoids skin-tone warnings), brown `#6B4A2B`.

## Garment menu
- Tops: navy/cream/forest knit sweater, varsity sweatshirt with contrast sleeves.
- Bottoms: khaki or navy chinos, navy/burgundy plaid pleated skirt.
- Shoes: brown loafers (`["#6B4A2B", "#6B4A2B"]`).

## Name words
Trend words: `preppy`, `vintage`, `aesthetic`, `cute`, `girl`.
Example: "Navy Sweater Chinos Preppy Vintage Outfit Top".

## Moderation traps
- No crests, letters or emblems that look like real schools, polo players or animals.
- No designer check patterns (camel/black/red/white house checks).

## Families and research (notes and links only)
- **Family fit:** Decorated. Argyle, cable knit and stripes carry it; prints rarely fit.
- **Motifs seen in current clothing:** Argyle, cable knit, rugby stripes, small stars, anchors, laurel wreaths.
- **Composition and inks:** Pattern-led; at most a small pocket motif. No crests or emblems.
- **Fabric and distress:** Clean or heathered knits; no distress.
- **Sources:** [Adobe Express: t-shirt trends 2025](https://www.adobe.com/uk/express/learn/blog/t-shirt-trends-2025)

## Decorated family (see [references/preppy](../references/preppy/sheet.png))
`argyle` and `cable` patterns for knits, `stripes` for rugby stripes, small `star` on `pocket`; no crests.
Use motifs from `tools/motifs.py` or library elements (`element: <id>`, see [library](../references/library/INDEX.md)); colours must be in the outfit palette.

## Owner artwork (42 imported elements fit this style)
Cut from the owner's generated sheets; use them like any library element (`element: <id>`), recoloured to one ink by default, or `original: true` to keep their colours (they then count toward the palette).

- Hero graphics (back / front print, about 90-110 px): `g01-number-07`, `g08-number-28`.
- Small motifs (chest, sleeve, 12-30 px): `g02-fleur-chrome`, `g03-filigree-corner`, `g03-fleur`, `g08-chevron-navy`, `g08-chevron-wine`, `g08-crown`, `g08-crowned-shield`, `g08-half-shield`, `g08-laurel-ball`, `g08-laurel-bow`, `g08-laurel-rackets`, `g08-sparkle-4`, `g08-striped-bow`, `g08-tennis-rackets` and 3 more.
- Borders (`layout: border`, tiles round the hem / cuff): `g01-double-stripe-border`, `g03-baroque-border`, `g08-arch-border`, `g08-cable-border`, `g08-checker-border`, `g08-diamond-border`, `g08-key-border`, `g08-laurel-border`, `g08-stripe-border-navy`, `g08-stripe-border-wine`.
- Fabric swatches (`base_pattern: swatch`): `g07-cable-knit-swatch`, `g07-plaid-swatch`, `g08-argyle-swatch`, `g08-cable-knit-swatch`, `g08-rib-stripe`, `g08-rugby-stripe-swatch`, `g08-tartan-swatch`.
- Garment parts (realistic family): `g08-piping-arc`, `g08-polo-collar`, `g08-polo-collar-wine`, `g08-raglan-yoke`, `g08-sleeve-panel`, `g08-sleeve-panel-wine`.
- Reference outfit: [examples/owner-preppy.yaml](examples/owner-preppy.yaml). All of them: [library/INDEX.md](../references/library/INDEX.md), sheet `../references/preppy/library.png`.

## Realistic family
- Archetypes: knit_stripes, suit_waistcoat, pleated_skirt_bows.
- Materials: knit, cotton shirting, pressed trousers.
- Collars, plackets, ties and creases are construction parts now; no crests or school names.
- Reference: [examples/realistic-knit-stripes.yaml](examples/realistic-knit-stripes.yaml). Vary `shading.seed` across a batch; shading is always the default stack `own-shade-all`.

## Not drawable yet (flag, don't fake)
Collar peeking over a sweater. (Polo placket and blazer lapels: realistic family parts.)

## Example
[examples/preppy.yaml](examples/preppy.yaml) · preview [examples/previews/guide-preppy/sheet.png](examples/previews/guide-preppy/sheet.png) · fem version [tests/specs/test-skirt.yaml](../../tests/specs/test-skirt.yaml) · varsity [tests/specs/test-contrast-sleeves.yaml](../../tests/specs/test-contrast-sleeves.yaml).

## Variations for a batch
1. Cream knit with navy rib + navy chinos.
2. Forest knit + khaki chinos.
3. Navy varsity sweatshirt with cream sleeves + black trousers.
4. Cream knit + navy/burgundy plaid skirt + white socks.
