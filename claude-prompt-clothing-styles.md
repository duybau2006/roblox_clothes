# Prompt for Claude Code: set up the clothing style library and Codex guidelines

Paste everything below the line into Claude Code, opened in the repo where the clothing store will live.

---

You are setting up the design side of a Roblox classic clothing store (2D shirts and pants sold through my group). Codex will be the designer; you are setting up the rules and style library it follows. Do the tasks below in order. Do not upload anything to Roblox and do not spend Robux in this session.

## Tasks

1. Create a top-level folder `clothing-store/` (do not touch any existing game code). Inside it create:
   - `AGENTS.md`: the Codex designer guidelines, built from the "Codex guidelines" section below.
   - `styles/irl.yaml` and `styles/roblox.yaml`: the two style libraries below, one entry per style, with the fields `id`, `name`, `palette`, `shirts`, `pants`, `details`, `keywords`, `avoid`.
   - `specs/`: empty folder for design specs, plus `specs/_template.yaml` from the "Design spec" section.
   - `trends/`: empty folder for dated trend notes.
2. Verify the Roblox list before anyone designs from it. Open the Roblox Marketplace in the browser, filter to Classic Shirts and then Classic Pants, sort by bestselling (past week and all time). For the first 60 or so items in each, record garment type, colours, style, and the words used in the name. Save the tally to `trends/YYYY-MM-DD-catalog.md`. Then update `styles/roblox.yaml`: reorder by how often each style appeared, add any style that appeared 3+ times and is missing, and mark styles that never appeared as `unverified: true`. Record words and patterns only. Do not download, save, or trace any item's image.
3. If my group already has sales, read the group's sales page and add `trends/YYYY-MM-DD-own-sales.md` listing what sold and the name words those items share.
4. Finish by telling me what changed between my starting list and the verified list, and which 10 styles you would design first and why.

## Codex guidelines (write these into AGENTS.md)

### Role
You design original classic shirts and pants for a Roblox group store. You never draw pixels freehand. You write a design spec (YAML) and the generator script renders it onto the official template, so every item shares the same construction and shading.

### Hard technical rules
- Canvas is exactly 585 x 559 px, PNG, transparent background. Never resize or move template regions.
- Region sizes: front/back 128x128, sides 64x128, top/bottom of torso 128x64, top/bottom of limbs 64x64.
- Art stays inside regions. Patterns must continue across seams (front to side to back) so stripes and waistbands line up.
- Shirts cover torso and arms. Pants cover lower torso and legs. Shoes drawn on pants stay at the very bottom of the leg regions.
- Every garment gets the shared shading layer: soft fold shadows, a highlight on the chest/thigh, darker edges at seams, a visible hem, collar or waistband. Flat colour fills are not acceptable.
- Pair every shirt with a matching pants design (a set), because sets sell together.

### Moderation rules (a rejected upload loses its fee)
- No brand names, logos, or look-alike marks. No three-stripe, swoosh-like, or monogram patterns that imitate a real brand.
- No real sports teams, bands, games, shows, anime or film characters, and nothing using Roblox's own logo or official items.
- Never copy or trace another creator's item. References are for mood, colour and garment type only.
- Little or no text. If text is used: one or two generic words, no slogans, no usernames, no links.
- Nothing sexual or suggestive: no lingerie, no underwear-as-outerwear, no skin-coloured fabric, no see-through panels over the chest or hips. Cropped and sleeveless cuts are fine if clearly ordinary clothing.
- No political, religious, drug, alcohol, gore, or real-weapon imagery. Uniforms use invented insignia, never real agencies, ranks, or flags.
- Nothing that hides the avatar or makes it look invisible.

### How to use the style libraries
- Pick one style entry per design. Use its palette (max 4 colours plus a neutral), garment list and details.
- A blend of two styles is allowed (for example Y2K + grunge) if both are named in the spec.
- Each batch should spread across styles and across masculine, feminine and unisex looks rather than repeat one look.
- Check `trends/` first and favour styles and name words that are currently selling.

### Naming and descriptions
- Name pattern: `[Colour] [Garment] [1-2 style words]`, for example "Black Baggy Cargo Pants Y2K Grunge". Put the words shoppers search first.
- Maximum about 50 characters. No brand names, no "free", no emoji walls, no long keyword lists.
- Description: one sentence saying what it is, one sentence naming the matching item in the set. Nothing else.

### Design spec (save as specs/_template.yaml)
```yaml
id: ""                 # e.g. 2026-11-y2k-cargo-01
type: shirt            # shirt | pants
set_id: ""             # shared by the matching shirt and pants
style: ""              # id from styles/irl.yaml or styles/roblox.yaml
blend_with: ""         # optional second style id
garment: ""            # e.g. cropped zip hoodie, baggy cargo pants
palette: []            # hex colours, max 4 plus one neutral
base_pattern: ""       # solid | stripes | plaid | gradient | colour-block | knit | denim
details: []            # e.g. drawstrings, front pocket, belt, ripped knees
shoes: ""              # pants only, kept at the bottom of the legs
audience: ""           # masc | fem | unisex
name: ""
description: ""
moderation_check: ""   # one line confirming no brands, text, or suggestive elements
```

## Style library A: 20 real-life styles (for styles/irl.yaml)

1. **Streetwear**: black, grey, white, one loud accent. Oversized hoodie, graphic-free boxy tee, bomber. Baggy cargos, wide jeans. Details: drawstrings, kangaroo pocket, chunky sneakers. Keywords: streetwear, baggy, oversized.
2. **Y2K**: baby pink, sky blue, silver, lime. Cropped baby tee, zip hoodie, halter-style top. Low-rise flared jeans, cargo pants, mini skirt over leggings. Details: star and butterfly shapes, belts, platform shoes. Keywords: y2k, 2000s, baby tee.
3. **Gorpcore**: olive, tan, orange, navy. Fleece zip, puffer vest over long sleeve, shell jacket. Hiking pants, zip-off cargos. Details: toggles, zip pulls, hiking boots. Keywords: outdoor, hiking, fleece, puffer.
4. **Athleisure**: black, heather grey, sage, lilac. Fitted zip jacket, sports tee, quarter-zip. Joggers, track pants, leggings. Details: side piping, drawcord, running shoes. Keywords: gym, joggers, sporty.
5. **Sporty jersey**: bold two-colour schemes. Invented football or basketball jersey, track jacket. Matching shorts over tights, track pants. Details: invented numbers, side stripes of original width, invented crest shapes. Keywords: jersey, track, sports.
6. **Old money / quiet luxury**: cream, camel, navy, forest green. Cable-knit sweater, polo, blazer over shirt. Tailored trousers, pleated slacks. Details: collar, buttons, belt, loafers. Keywords: old money, classy, elegant.
7. **Preppy / varsity**: navy, burgundy, white, green. Varsity jacket with invented letter, sweater vest over shirt, rugby stripe. Chinos, pleated skirt with socks. Details: ribbed cuffs, patch shapes, loafers. Keywords: preppy, varsity, school.
8. **Minimalist**: white, black, beige, stone. Plain heavyweight tee, crewneck, overshirt. Straight trousers, clean jeans. Details: subtle seams only, white sneakers. Keywords: basic, clean, plain.
9. **Grunge**: black, charcoal, faded red, moss. Flannel over dark tee, ripped sweater. Ripped jeans, black skinny or baggy jeans. Details: plaid, frayed hems, chains, combat boots. Keywords: grunge, flannel, ripped.
10. **Coquette / soft feminine**: blush, ivory, baby blue, rose. Bow-front cardigan, puff-sleeve top, lace-trim blouse. Pleated skirt, ruffle shorts with tights. Details: bows, ribbon, small florals, ballet flats. Keywords: coquette, bow, cute, pink.
11. **Cottagecore**: sage, cream, mustard, dusty rose. Embroidered blouse, knitted vest, gingham top. Long skirt, overalls, linen trousers. Details: tiny flowers, gingham, apron ties, boots. Keywords: cottagecore, floral, gingham.
12. **Techwear**: black, graphite, one neon. Shell jacket, strapped vest over long sleeve. Tactical cargos with straps, tapered joggers. Details: buckles, straps, panel lines, high-top boots. Keywords: techwear, tactical, cyber.
13. **Workwear**: tan, brown, navy, washed black. Chore jacket, canvas overshirt, thermal henley. Carpenter pants, double-knee trousers, overalls. Details: contrast stitching, tool pockets, work boots. Keywords: workwear, carpenter, canvas.
14. **Boho**: rust, cream, turquoise, brown. Fringe vest, embroidered tunic, crochet top. Flared trousers, tiered skirt. Details: fringe, paisley-like original pattern, suede boots. Keywords: boho, fringe, festival.
15. **Western**: brown, denim blue, cream, red. Pearl-snap shirt, denim jacket, yoke-detail shirt. Bootcut jeans, chaps-look pants. Details: pointed yoke, belt buckle, cowboy boots. Keywords: western, cowboy, cowgirl.
16. **Double denim**: light, mid and dark washes. Denim jacket, denim shirt. Straight or baggy jeans, denim skirt. Details: stitching lines, pockets, fades at knees and elbows. Keywords: denim, jeans, jacket.
17. **Dark academia**: brown, black, deep green, cream. Tweed blazer, turtleneck, argyle-like original knit vest. Plaid trousers, pleated skirt with tights. Details: elbow patches, buttons, oxford shoes. Keywords: academia, blazer, vintage.
18. **Skater**: washed black, cream, forest green, mustard. Striped long sleeve, oversized tee over long sleeve. Baggy jeans, corduroy pants, long shorts. Details: horizontal stripes, flat-sole skate shoes. Keywords: skater, baggy, striped.
19. **Checks and tartan**: red/black, green/navy, brown/cream. Plaid shirt, tartan jacket. Plaid trousers, tartan skirt. Details: aligned checks across seams (the main quality test). Keywords: plaid, tartan, checkered.
20. **Cozy knit and faux fur**: oatmeal, chocolate, cream, burgundy. Chunky sweater, fur-collar coat, cardigan. Knit lounge pants, corduroy. Details: knit texture, fluffy trim, ugg-style boots. Keywords: cozy, sweater, winter, fluffy.

## Style library B: 20 Roblox styles (starting list for styles/roblox.yaml, to be verified in task 2)

1. **Soft girl / cute pastel**: pink, lilac, cream, baby blue. Cropped cardigan, heart-detail sweater. Pleated skirt with leg warmers, light jeans. Keywords: soft, cute, aesthetic.
2. **Y2K crop and cargo**: black, pink, white, camo-like original pattern. Crop top, zip hoodie. Baggy cargos with belt and chunky shoes. Keywords: y2k, cargo, crop top.
3. **Emo / scene**: black, hot pink, purple, neon green. Striped long sleeve under tee, studded-look hoodie. Skinny black jeans, plaid pants with chains. Keywords: emo, scene, striped.
4. **Dark grunge boy**: black, grey, dark red. Black hoodie, flannel, layered tee. Ripped black jeans with boots. Keywords: grunge, dark, black hoodie.
5. **Streetwear hoodie set**: any bold colour with black or white. Oversized hoodie with drawstrings. Matching sweatpants with sneakers. Keywords: hoodie, sweatpants, set.
6. **Preppy / old money**: navy, cream, green. Sweater over collar, polo, tennis sweater. Trousers, tennis skirt. Keywords: preppy, old money, classy.
7. **Kawaii**: pastel rainbow, white. Sailor-style collar top, animal-ear-hood hoodie (hood drawn flat). Suspender skirt, striped stockings. Keywords: kawaii, pastel, cute.
8. **Fairycore**: sage, lavender, pearl white. Corset-look top over blouse, sheer-look sleeves drawn opaque. Layered petal skirt. Keywords: fairy, fairycore, floral.
9. **School uniform**: navy, grey, white, plaid accents. Blazer with invented crest, sailor-style top, vest and tie. Pleated skirt, slacks. Keywords: school, uniform, blazer.
10. **Idol / stage outfit**: black, white, metallic, one bright accent. Cropped jacket with harness-look straps, sparkle top. Wide pants, shorts with tall boots. Keywords: stage, idol, performance.
11. **Roleplay job uniforms**: medic, chef, barista, firefighter, pilot, generic security. Invented badges and names only. Keywords: uniform, roleplay, the job name.
12. **Group / military-style uniforms**: olive, navy, black, tan. Field jacket, dress uniform with invented insignia. Matching trousers with boots. Keywords: uniform, officer, cadet.
13. **Suits and formal**: black, navy, white, burgundy. Suit jacket with shirt and tie, tuxedo, waistcoat. Suit trousers with dress shoes, formal gown skirt. Keywords: suit, formal, tuxedo, prom.
14. **Cozy oversized sweater**: cream, brown, sage. Chunky knit, off-shoulder-look sweater with opaque undershirt. Leggings with fuzzy boots. Keywords: cozy, sweater, fall.
15. **Techwear / cyber**: black with neon lines. Strapped jacket, panelled vest. Tactical pants with glow-colour piping. Keywords: techwear, cyber, tactical.
16. **Retro blocky classic**: primary colours, simple shading. Plain bright tee with pocket, simple jacket. Plain jeans with visible shoes. No Roblox logos or official item copies. Keywords: classic, retro, simple.
17. **Sports kits**: bold two-tone. Invented team jersey with number. Shorts with long socks and cleats. Keywords: jersey, soccer, basketball, kit.
18. **Pajamas and loungewear**: soft pastels, plaid. Pajama shirt, onesie-look top. Pajama pants with slippers. Keywords: pajamas, pjs, sleepover.
19. **Seasonal**: Christmas sweaters and winter sets now, then Valentine's, spring, summer, Halloween. Invented festive patterns. Keywords: christmas, winter, the holiday name.
20. **Skirts and dresses drawn on pants**: plaid, denim, floral. Matching top. Skirt drawn on the lower torso and upper legs, tights or socks below, shoes at the bottom. Keywords: skirt, dress, plaid skirt.

## Prompt Codex uses for each batch (put at the end of AGENTS.md)

"Read AGENTS.md, both files in styles/, and the newest files in trends/. Propose a batch of N sets (each set is one shirt and one matching pants). Spread the batch across at least N/2 different styles and across masc, fem and unisex. For each item write a spec in specs/ using the template. Before finishing, re-read every spec against the moderation rules and fix or drop any that could fail. Do not render or upload; stop and list the specs for approval."
