# Visual craft

Read when creating a visual language, redesigning a surface, or asked to polish one. An installed design system's tokens and components win over every number here: these are starting points for decisions the project has not made, not a house style.

## Direction

State the direction in one sentence before styling: who it is for, how it should feel, and the one thing each screen must make obvious. "Calm and dense for a cashier who repeats one task all day" produces different type, spacing, and color than "confident and spacious for a first-time visitor."

Without a brief, default to quiet structure: neutral layered surfaces, one accent, and typography carrying the hierarchy. The test of restraint: remove one more decoration; if the screen still reads as complete, it was not needed.

## Type

- One family for interface text; a second only for a distinct role such as display or code.
- Few sizes with clear steps: a ratio near 1.2 for dense work, 1.25 to 1.333 for reading and marketing. Build hierarchy from size, weight, and color together. When two levels are hard to tell apart, increase their contrast instead of adding a level.
- Body at 16px with 1.5 line height for reading; 13 to 14px with 1.4 for dense operational screens; headings at 1.1 to 1.25. Lines of 45 to 75 characters.
- Tabular numerals and right alignment for numeric columns. Never center long text.

## Space

- One scale on a 4px base: 4, 8, 12, 16, 24, 32, 48, 64. An off-scale value needs a reason.
- Proximity is grouping: the space between groups is at least twice the space within them. Uniform spacing hides structure.
- Align to few shared edges; each extra alignment line is noise.
- Density follows frequency of use. Work repeated all day earns compact rows and controls, within pointer-target limits; an occasional or first-time task earns room and explanation.

## Color

- Neutrals do most of the work: one gray ramp, tinted toward the brand hue, for text, borders, and surfaces.
- One accent, reserved for the primary action, selection, and focus. When everything is accented, nothing is.
- Status colors stay separate from brand, each with a paired foreground, and are never the only signal.
- Define colors in OKLCH so lightness steps look even. In a dark theme, raise surface lightness to show elevation and lower chroma; do not invert.

## Depth and motion

- Separate with space first, then a subtle border or background shift, then elevation. Shadows are for things that float.
- Motion explains a change of state: 150 to 250ms, easing out on entry, faster on exit, and none under reduced motion or on actions repeated many times a minute.

## Three compositions

| Surface | Structure | Why it works |
| --- | --- | --- |
| Operational list and detail | Context and the primary action in the header; filters beside results; a table with stable columns; detail in a panel or page that keeps the list's place | The eye returns to the same places, comparison runs down columns, and the next action is always in one spot |
| Focused task or form | One column no wider than about 40rem; fields grouped by decision; the primary action last, and persistent on small screens | One reading order, no competing targets, and the consequence is visible before committing |
| Product or landing page | One proposition, one piece of real evidence, and one action in the first view; later sections alternate claim and proof | A visitor decides in seconds; everything else supports that one decision |

## Judge the result

Judge the rendered screen, not the code:

1. **Blur it.** The primary action and the three most important things stay identifiable.
2. **Remove color.** The hierarchy survives in grayscale.
3. **Stress it.** The longest label, an empty list, one row and hundreds, an error.
4. **Compare.** When unsure, render two variants of the same screen and keep the one where a first-time viewer finds the next step faster. Say which you chose and why.

These checks show that a composition communicates; whether it is beautiful still needs a person looking at it.
