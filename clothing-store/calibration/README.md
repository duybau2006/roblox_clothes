# Calibration outfit

`calibration-shirt.png` and `calibration-pants.png` are 585x559 test textures. Every panel has its own
colour, its name ("S" = shirt file, "P" = pants file), a white arrow pointing to the top of the panel
image, a 16 px grid, and yellow tags on each edge naming the panel it should join ("~" = joins reversed).
Dashed lines mark the assumed split points: LOWER TORSO 96, HAND 112, FOOT 108, and the template guide at 52.
The `-2x-preview.png` files are only for reading on screen. Upload the 585x559 ones.

## View it in Studio (free image upload, no Robux)

1. Open Roblox Studio and start a new **Baseplate**.
2. **Avatar** tab → **Rig Builder** → Rig Type **R15** → **Block Rig**. Do it again with Rig Type **R6** → **Block Rig**. Move the two rigs apart.
3. **View** → **Asset Manager** → **Bulk Import** → pick `calibration-shirt.png` and `calibration-pants.png`. They upload as free Image assets (they go through normal image moderation).
4. In **Explorer**, hover the R15 rig → **+** → **Shirt**, and again → **Pants**.
5. In Asset Manager, right-click `calibration-shirt` → **Copy Asset ID**. Select the Shirt → **Properties** → paste into **ShirtTemplate**. Do the same with `calibration-pants` → Pants → **PantsTemplate**.
6. Repeat steps 4–5 for the R6 rig.

## Screenshots to send back (for each rig: R15 and R6)

1. Front, back, left side and right side, full body, camera level with the chest.
2. From above (looking down on the shoulders) and from below (looking up at the hands and soles).
3. A close-up of one shoulder and of the hip from the front.
4. With the **Shirt deleted** (pants only): front and back, to see the pants torso.

Name them like `r15-front.png`, `r6-below.png`, `r15-pants-only-back.png` and put them in `calibration/screenshots/`.

## What gets corrected from them

- Which panel lands on which face, and whether any face is rotated or mirrored: arrows and text show it.
- Edge pairs: the yellow tags on the two sides of every real seam should name each other.
- Split points: where the R15 UpperTorso/LowerTorso, hand and foot boundaries fall on the grid. These update `clothing.OUTFIT` and the shading layers.
- After corrections: `python tools/build_regions.py`, `python tools/make_shading.py`, `python tools/run_tests.py`.

## Results (2026-11-16, screenshots in `screenshots/R15` and `screenshots/R6`)

- **Panel map: confirmed.** On both rigs every panel lands on the expected face, upright and not mirrored.
- **Seams: confirmed.** Every yellow edge tag, including on the top and bottom faces (above/below shots), names the panel it really touches. The shoulder and hip neighbours match `outfit_seams` in regions.json. No change to regions.json panels or seams.
- **R6:** one part per body part; each side panel is mapped whole and uniformly, so there are no split lines to respect.
- **R15:** each body part shows its own slice of the panel at its own scale. Measured split rows (±2 px):

| Split | Assumed | Measured | Now used |
|---|---|---|---|
| UpperTorso / LowerTorso | 96 | ~92 | default `waist_line` 92 |
| Elbow (UpperArm / LowerArm) | none | ~50 | elbow creases moved to ~50 |
| Hand | 112 | ~110 | sleeve cuff 98-110, hand below 110 |
| Knee | none | ~51 | knee creases already at 50-66 |
| Foot | 108 | ~106 | ankle cuff 94-106, shoes 106-128 |

The values are stored in `templates/regions.json` (`rig_calibration`) and `tools/clothing.py` (`OUTFIT`). The calibration PNGs were re-rendered with the new lines. Re-upload them only if you want to re-check.
