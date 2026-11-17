# Archive / avant-garde

**Audience:** mostly masc, older teens who follow fashion. **Trend evidence:** not in the 2026-11-16 Roblox catalog check, so this is a bet on a niche with little competition; "archive" is not yet a trend name word. **Library:** `archive` (irl.yaml).

## The look
Monochrome washed blacks and greys, long hems, layering, wide dark trousers, heavy boots. Mood comes from proportion and tone, never from designer references.

## Spec settings
- Torso: long-line tee or high-neck knit; `hem: plain`; `hem_line` 116-120 (the long hemline is the signature).
- Arms: layered = `sleeves: short` + `arms.under` in a second grey; or long plain sleeves.
- Legs: `type: trousers`, `solid` charcoal, `waistband: none` or `plain`; or a long dark skirt (`skirt_length` 80-96) worn over black tights.
- Shoes: black boots (`["#1A1A1A", "#3A3A3A"]`).

## Palette
Washed black `#1A1A1A`, charcoal `#3A3A3A`, ash grey `#8A8580`, bone `#E8E4DC`. Keep to 2-3 tones per outfit.

## Garment menu
- Tops: washed black long tee, charcoal knit (`base_pattern: knit`).
- Sleeves: ash or bone under-sleeves.
- Bottoms: charcoal wide trousers, long black skirt + tights.

## Name words
Trend words: `goth`, `black`, `aesthetic`, `vintage`, `grey`. Add "archive" only once a trends file lists it.
Example: "Black Long Tee Trousers Goth Outfit Top".

## Moderation traps
- Never name or imitate a designer, runway piece or logo; no replica of a specific collection.
- No occult or religious symbols; distressing never shows skin.

## Families and research (notes and links only)
- **Family fit:** Print or decorated. Print for a washed back graphic (moths, engraved ornaments); decorated for contrast stitching and patches.
- **Motifs seen in current clothing:** Engraving-style moths and ornaments, gothic windows, thorns, barbed wire; deliberately worn wear marks.
- **Composition and inks:** Minimal front, large faded back print; long-line silhouettes. Inks: bone, ash grey on washed black.
- **Fabric and distress:** Faded black / mineral wash; worn + cracked (level 1-2). Recipe: `centered_stack`, tags [moth, thorns, star] (the CC0 moth fits).
- **Sources:** [Puma: archive washed oversized tee](https://us.puma.com/us/en/pd/futurepumaarchive-womens-washed-oversized-graphic-tee/636647), [2026 graphic tee trends](https://ootd.bearblog.dev/graphic-tee-trends-shaping-2026s-fashion-scene/), [Thrifted: vintage tee styles 2026](https://www.thrifted.com/blogs/the-edit/best-vintage-t-shirt-styles-in-2026), [Fashion Week Online: distressed shirts](https://fashionweekonline.com/how-to-style-distressed-shirts-for-a-modern-streetwear-look)

## Decorated family (see [references/archive](../references/archive/sheet.png))
`stitch` (contrast stitching) on torso and legs, `patch` on legs knees or torso, `rip` (distress) on knees; washed solids, `colour-block`.
Use motifs from `tools/motifs.py` or library elements (`element: <id>`, see [library](../references/library/INDEX.md)); colours must be in the outfit palette.

## Owner artwork (58 imported elements fit this style)
Cut from the owner's generated sheets; use them like any library element (`element: <id>`), recoloured to one ink by default, or `original: true` to keep their colours (they then count toward the palette).

- Hero graphics (back / front print, about 90-110 px): `g03-gothic-window-roses`, `g06-skull-crest`.
- Small motifs (chest, sleeve, 12-30 px): `g01-compass-sparkle`, `g01-stitch-x`, `g03-compass-star`, `g03-filigree-corner`, `g03-moth`, `g06-chain-drape`, `g06-fleur`, `g06-lion-knocker`, `g06-spike-compass`, `g06-tape-x`, `g08-crown`, `g08-crowned-shield`, `g08-half-shield`, `g08-laurel-bow` and 2 more.
- Borders (`layout: border`, tiles round the hem / cuff): `g01-stitch-dash-border`, `g03-baroque-border`, `g06-chain-links`, `g06-grommet-strip`, `g06-tape-strip`, `g08-arch-border`, `g08-key-border`, `g08-laurel-border`, `g10-chain-stitch-trim`, `g10-distress-strip`, `g10-frayed-strip`.
- Fabric swatches (`base_pattern: swatch`): `g10-distressed-swatch`.
- Garment parts (realistic family): `g01-stitched-patch`, `g01-zip-border`, `g06-stitched-patch`, `g10-buckle-strap`, `g10-cargo-pocket`, `g10-grommet-panel`, `g10-grommet-patch`, `g10-patchwork-stack`, `g10-pattern-piece`, `g10-quarter-panel`, `g10-seamed-panel`, `g10-snap-tab`, `g10-strap-loops`, `g10-tie-tabs` and 2 more.
- Textures and distress (print overlays): `g01-grunge-texture`, `g06-claw-rips`, `g06-slash-rips`, `g06-smear`, `g06-torn-hole`, `g10-distress-smear`, `g10-draft-lines`, `g10-ink-splatter`, `g10-sketch-frame`, `g10-sketch-marks`, `g10-torn-canvas`, `g10-torn-fabric`.
- Reference outfit: [examples/owner-archive.yaml](examples/owner-archive.yaml). All of them: [library/INDEX.md](../references/library/INDEX.md), sheet `../references/archive/library.png`.

## Realistic family
- Archetypes: bomber_badge, suit_waistcoat.
- Materials: nylon flight jackets, leather, cotton suiting.
- Invented emblems only: a library element in a shield / circle / wreath frame; no real insignia, ranks or flags.
- Reference: [examples/realistic-bomber-badge.yaml](examples/realistic-bomber-badge.yaml). Vary `shading.seed` across a batch; shading is always the default stack `own-shade-all`.

## Not drawable yet (flag, don't fake)
Asymmetric hems, drapes, drop-crotch silhouettes, cargo straps.

## Example
Print family: [examples/print-layered-moth.yaml](examples/print-layered-moth.yaml) · preview [examples/previews/print-layered-moth/sheet.png](examples/previews/print-layered-moth/sheet.png).  
Decorated family: [examples/archive.yaml](examples/archive.yaml) · preview [examples/previews/guide-archive/sheet.png](examples/previews/guide-archive/sheet.png).

## Variations for a batch
1. Bone long tee over charcoal long sleeve + black trousers.
2. Charcoal knit + long black skirt + black tights.
3. Washed black long tee + ash grey trousers.
4. All-black layered look with grey under-sleeves.
