# Style references (original swatches)

One folder per style. Each holds `sheet.png` (all swatches) plus one PNG per motif or pattern. Every swatch is drawn by the same code the renderer uses (`tools/motifs.py`, `render.paint_pattern`), so anything shown here can go straight into an outfit spec's `decor` list or `base_pattern`. Regenerate with `python tools/make_references.py`.

**Originality rule.** These are our own drawings of each style's *motif vocabulary*. We do not save, trace or imitate other creators' Roblox items, and we never use brand logos, monograms, real characters, crosses, skulls or text. Real-life fashion photos for mood can go in `clothing-store/references/` (git-ignored, local only).

## Element library (all three design families)

[library/](library/INDEX.md) holds 124 reusable elements, **one JSON file each** (plus a mask PNG for public-domain art), tagged with style, mood, motif, smallest readable size and the families it suits. Previews: `library/previews/`, all elements: [library/all.png](library/all.png), per style: `<style>/library.png`.

| Elements per style | y2k | vamp-goth | emo | baddie | grunge | gen-z | archive | soft-girl | preppy | cottagecore | christmas | athleisure |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| count | 68 | 59 | 74 | 62 | 69 | 35 | 41 | 35 | 17 | 24 | 20 | 16 |

- **Original elements** (118): drawn as code in `tools/build_library.py` (wings, stylised skulls without gore, roses, thorns, bats, moths, butterflies, chains, barbed wire, flames, stars, hearts, webs, filigree, chandelier, candles, keys, an ornamental dagger drawn diagonally, gothic window tracery, tribal spikes, and more).
- **Public-domain elements** (6): two moth studies, a moth plate, a dragonfly brooch, a lace border and an acanthus ornament from The Met Open Access (CC0), imported by `tools/import_public_domain.py` only after the museum API confirmed `isPublicDomain = true`. Source URL, licence, title, artist and date are in [LICENSES.md](LICENSES.md). Only derived ink masks enter the repo, never the source images.
- **Blocked:** crosses and other religious symbols, text, logos, gore. `validate.py` rejects any element that is blocked, unlicensed or not in the library.
- Rebuild: `python tools/build_library.py && python tools/library_sheets.py`.

## Owner-generated artwork (2026-11-16)

Ten motif sheets the owner generated with ChatGPT (`inbox/sheet-01.png` .. `sheet-10.png`). `tools/import_motifs.py` cut every element out using the hand-checked boxes in `inbox/classify.yaml`, and saved for each: the original colour version, a 3-tone ink mask the renderer recolours, a greyscale ink version, a bold simplified mask where engraving turns to mud at real size, and seamless tiles for borders (horizontal) and swatches (both ways). Numbered contact sheets: `inbox/contact/sheet-NN.png` (red = imported, purple = held); scale tests: `inbox/contact/sheet-NN-scale.png`. Held elements (crosses, halos, unclothed figures, three-skull groups, hooded fairies, brand look-alikes, money, lips, blood, wounds, words) are in [held/](held/README.md) with a contact sheet and never enter the library.

## Collected shading layers, vault check, skipped sources

- **Shading layers** (9): PeZsmistic's public-domain shirt shadow templates (DevForum, waiver: "may be freely used for any purpose", credit not required). Converted to greyscale maps, checked against the 585x559 panels and seam-healed (0 failing seam pairs after healing) by `tools/shading_custom.py`; saved with a licence JSON in `templates/shading/custom/`. Contact sheet: [shading-contact-sheet.png](shading-contact-sheet.png). Side-by-side quality check: [realistic-comparison-3x.png](realistic-comparison-3x.png).
- **Owner-supplied shading templates** (3, the defaults since 2026-11-16): `own-shade-1` (soft scribble folds), `own-shade-2` (radial folds with highlights), `own-shade-3` (bold folds; it arrived as a JPEG flattened on a checkerboard, so the checker was divided out, the arm-bottom faces missing from it were filled flat, and it is used shadows-only). All three are seam-healed across shoulders and hips and shade torso, arms and legs. Since 2026-11-16 every outfit in every family is shaded with `own-shade-all`, the three stacked (1.0 + 1.0 + 0.8, gain 0.7). Source and licence were not given: they are listed separately in LICENSES.md and `validate.py` WARNs until the owner confirms them.
- **LihFolk vault**: read, not imported. The V2 notes and the Asset Pack licences allow use inside your own games but forbid selling or redistributing their images, templates or assets, and clothing listings are a sale of the image. The V1 Lite CC BY 4.0 files are rig sheets, UI and 3D renders, not clothing textures. Listed on [vault-contact-sheet.png](vault-contact-sheet.png); raw vault files are git-ignored.
- **Skipped**: every outside item not imported, with the reason, is in [skipped.json](skipped.json) and the "Skipped" section of [LICENSES.md](LICENSES.md) (example renders, unclear or credit-required licences, sources that block downloads, vault files).
- `validate.py` fails any outfit whose `shading.layer` has no licence JSON or no LICENSES.md entry, and any library element without one.

## Motif vocabulary by style (research, 2026-11-16)

| Style | Motifs and patterns | Notes from research |
|---|---|---|
| Y2K | butterfly, star, sparkle (rhinestone glints), heart, flame, leopard | Butterflies are the signature motif; stars, hearts, flames and airbrush-style graphics on baby tees; rhinestone sparkle as a finish. |
| Vamp / goth | bat, rose, spider web, moon, lace trim, dark plaid | Bats, roses and webs appear as small accents (pendant/embroidery scale) more than all-over prints; lace and velvet for romantic goth. |
| Grunge | rips (distressing), safety pin, patch, plaid, stripes, checkerboard | Plaid and stripes are the hallmark prints; distressed, thrifted, pinned. |
| Emo / scene | star, heart, lightning, studs, chain, stripes, checker, leopard | Studs, wallet chains, stripes, leopard and checkerboard. |
| Archive | contrast stitching, patches, distressing, washed solids, colour-block | Visible seams, raw edges, patchwork panels, manufactured wear. |
| Gen Z | small pocket motifs (star, heart, sparkle), heather, light denim | Minimal: one small mark at most; quality comes from construction. |
| Baddie | heart, butterfly, flame, chain necklace, leopard | Bold single chest graphic + silver chains. |
| Soft girl / coquette | bow, heart, cherry, flower, lace, gingham | Bows, gingham, hearts and soft pastels; ditsy florals. |
| Preppy | argyle, cable knit, rugby stripe, plaid, small pocket star | Knit textures and argyle carry the look; no crests or emblems. |
| Cottagecore | ditsy flower, cherry, bow, lace collar, gingham, knit | Rural, modest, printed cottons and small florals. |
| Christmas | star, snow sparkle, heart, candy stripe, cable knit, tartan | Invented festive patterns only; no religious symbols or licensed characters. |
| Athleisure | lightning, star, colour-block, heather | No side stripes or swoosh-like curves. |
| Realistic (all styles) | materials, folds, collars, lapels, ties, waistcoats, zips, pockets, belts, jeans stitching, cut-outs, shoes, numbers 0-99, invented emblems | Construction carries the look; numbers are digits only; emblems are library elements in an invented frame. |

## Sources
- Y2K motifs: [Refinery29: butterflies trend](https://www.refinery29.com/en-us/2021/10/10724912/butterflies-spring-2022-fashion-trend), [The Zoe Report: butterfly motif](https://www.thezoereport.com/fashion/butterfly-motif-fashion-trend), [Primark: the Y2K revival](https://www.primark.com/en-us/a/inspiration/style-trends/the-y2k-revival), [Ragstock: Y2K fashion](https://ragstock.com/y2k-fashion/)
- Goth / vamp: [VampireFreaks: what goths look like](https://vampirefreaks.com/blogs/goth/what-do-goths-look-like), [Fuga Studios: gothic fashion guide](https://fuga-studios.com/en/blogs/journal/gothic-fashion-guide), [The Pleat: fashion and the gothic](https://thepleat.substack.com/p/05-fashion-and-the-gothic)
- Archive / deconstruction: [FIT: Fashion Unraveled](https://fitnyc.edu/museum/exhibitions/fashion-unraveled.php), [ASU FIDM: deconstruction in fashion](https://asufidmmuseum.asu.edu/learn/articles/deconstruction-fashion), [SSENSE: whiskered jeans](https://www.ssense.com/en-ar/editorial/fashion/worn-this-way-whiskered-jeans-explained)
- Grunge / emo / punk: [Refinery29: how to dress emo](https://www.refinery29.com/en-au/how-to-dress-emo-guide), [ThredUp: emo style](https://www.thredup.com/bg/p/emo-style), [Sew Guide: punk fashion](https://sewguide.com/punk-fashion-style/)
- Coquette / cottagecore: [Business of Fashion: coquette explained](https://businessoffashion.com/articles/marketing-pr/coquette-trend-explained/), [SSENSE: coquette aesthetic](https://www.ssense.com/en-pg/editorial/market/coquette-trend-aesthetic), [Bustle: cottagecore](https://www.bustle.com/style/spicy-cottagecore-outfits-spring-2025)
- Preppy (argyle, cable knit): no strong sources found; based on standard knitwear construction.
