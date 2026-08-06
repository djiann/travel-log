# Travel Itinerary Map — Permanent Prompt Pack

Repo-versioned copy of the successful map-generation method.
Cursor agent skill (invokable memory): `~/.cursor/skills/travel-itinerary-map/`

**Invoke:** mention「旅遊地圖」「旅程地圖」「依 skill travel-itinerary-map」or regenerate a Day map after itinerary edits.

---

## Hard bans

1. Never use Python/PIL/`render-journey-maps.py` (deleted on purpose) to draw maps.
2. Never invent neon / flat UI / crayon styles.
3. Never ship content that disagrees with the **current** guide HTML.
4. Always compare original reference PNGs before generating.

## Workflow

1. Read current Day itinerary from guide HTML.
2. Inspect references: `day-01-20260812.png`, `day-02-20260812.png`, `overview-20260812.png`.
3. Fill the strict prompt below; call GenerateImage `3:4` with those references.
4. Fit **1024×1536**, compress **~1MB**, preserve rich color.
5. Sync `Japan/<trip>/assets` and `docs/Japan/<trip>/assets`.

## Strict prompt template

```text
Create a Day {{DAY_NUMBER}} travel itinerary map that MATCHES the attached reference maps EXACTLY in art style.

STYLE LOCK — copy the references, not a new style:
- Soft Japanese watercolor + thin delicate ink / fountain-pen outlines
- Cream textured travel-diary paper background
- Soft watercolor washes with gentle blended gradients
- Rainbow multi-color dashed winding road (pink→orange→yellow→green→blue→purple) connecting stops
- Numbered circular station badges along the road
- Cute kawaii animal mascots (panda / rabbit) like the originals
- Sticky-note / memo tip boxes
- Side panels for 必吃 and 旅行小貼士
- Bottom 備案 boxes if provided
- Traditional Chinese text only
- RICH cheerful color accents like Day1/Day2 originals (green JR train, vivid food, sunset sky, colorful light-show blues/pinks) — NOT grey washed-out only

STRICTLY FORBIDDEN:
- Crayon, oil pastel, wax pastel, chalk, thick rough grainy strokes
- Neon metro poster, dark cyberpunk, flat vector UI cards, app timeline
- Programmatic / template card maps
- English-only labels (Chinese first; short English only if on real storefronts)
- Outdated itinerary items not listed below

LAYOUT:
- Vertical adventure map, same composition language as the reference day maps
- Header board + ribbon subtitle
- Central winding path with clear journey flow top→bottom
- Right side: 必吃 + 旅行小貼士
- Bottom: 備案 if any

HEADER:
- Title: {{HEADER_TITLE}}
- Main heading: {{MAIN_HEADING}}
- Ribbon subtitle: {{RIBBON_SUBTITLE}}

STOPS ON THE WINDING PATH (in order, with small detailed watercolor illustrations):
{{NUMBERED_STOPS}}

RIGHT SIDE 必吃美食 (ONLY these — do not invent removed restaurants):
{{MUST_EAT}}

RIGHT SIDE 旅行小貼士:
{{TIPS}}

BOTTOM 備案:
{{BACKUPS}}

Keep it readable, cute, soft watercolor, and colorful like the Day1/Day2 references. Sense of journey flow along the road is mandatory.
```

## Acceptance

Regenerate if: crayon/neon/UI look; too grey vs Day1/Day2; wrong times/foods; not 繁中; no winding flow.
