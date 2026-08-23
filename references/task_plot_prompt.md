Use case: scientific-educational
Asset type: TaskBeacon task flow diagram
Primary request: Create a clean, publication-ready timeline collection for the Negative Priming behavioral task described below.

Task: Negative Priming
Construct: selective attention / inhibitory control

Rows and exact trial logic:
- No distractor: READY -> Blank -> Prime fixation -> Prime response with a green irregular outline target on the left and a white irregular outline reference on the right, with NO red distractor -> Blank -> Probe fixation -> Probe response with an unrelated green target plus overlapping red distractor on the left and white reference on the right.
- Control: READY -> Blank -> Prime fixation -> Prime response with green target plus overlapping red distractor on the left and white reference on the right -> Blank -> Probe fixation -> Probe response with green target plus overlapping red distractor on the left and white reference on the right; every probe shape is unrelated to every prime shape.
- Negative priming: READY -> Blank -> Prime fixation -> Prime response with green target plus overlapping red distractor on the left and white reference on the right -> Blank -> Probe fixation -> Probe response with green target plus overlapping red distractor on the left and white reference on the right. The ignored RED prime distractor must have the exact same distinctive notched outline as the GREEN probe target. Change only its color and role so the ignored-to-target repetition is visually obvious.

Seven columns, with these exact phase and timing labels:
1. Ready — `SPACE`
2. Blank — `1,100 ms`
3. Prime fixation — `500 ms`
4. Prime response — `F different / J same`, `5.0 s max`
5. Blank — `100 ms`
6. Probe fixation — `500 ms`
7. Probe response — `F different / J same`, `5.0 s max`

Visual requirements:
- White or very light gray background, landscape orientation, crisp dark typography, restrained blue/green/red accents.
- Exactly three horizontal rows labeled `No distractor`, `Control`, and `Negative priming`.
- Exactly seven aligned participant-screen cards in each row, connected by subtle arrows.
- Participant screens are black rectangles with a thin neutral border and a consistent 16:10 ratio.
- READY is blue; fixation is a centered white `+`; blanks are empty black screens.
- Response cards show abstract irregular closed outline shapes only: green target and red distractor overlap on the LEFT, and one white reference outline is isolated on the RIGHT.
- Draw the red outline first and the green outline in front so both remain visible. Use no filled shapes.
- Keep all labels, cards, shapes, arrows, and timings separated with no overlap.
- Make all text legible at normal document preview size.
- Leave the top 17% completely blank. It is reserved for a fixed title, `Construct: ...` subtitle, and TaskBeacon logo added after generation.

Accuracy constraints:
- Do not invent phases, stimuli, feedback, keys, rewards, conditions, or timings.
- Do not add people, brains, hands, keyboards, laboratory equipment, decorative icons, logos, watermarks, brands, or `TaskBeacon` text.
- Do not place a red distractor on the right. The right-hand shape is always white.
- The No distractor PRIME must have no red shape.
- In the Negative priming row only, repeat the exact same distinctive notched outline from the red prime distractor as the green probe target. Other prime-to-probe outlines must be visibly different.
- If a detail is unknown, omit it rather than guessing.

Style: TaskBeacon scientific infographic style, clean vector-like raster rendering, orderly spacing, restrained colors, and a blank header-safe area.

## Revision history

- Round 1: corrected unequal target/distractor scale.
- Round 2: rejected because probe distractors were removed during revision.
- Round 3: restored all probe distractors and equalized response-shape scale; rejected because the critical identity repeated within color rather than from red distractor to green target.
- Round 4: changed only the negative-priming prime color roles so the red prime distractor and green probe target share the exact same scalloped outline. Accepted.
