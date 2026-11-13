# Visual craft

Read when creating a visual language, redesigning a surface, or asked to polish one. An installed design system's tokens and components win over every number here: these are starting points for decisions the project has not made, not a house style. The brief wins over any default named below. Tokens, platform features, motion, and performance are in [web platform](web-platform.md).

## Contents
- Mode sets the ambition
- Direction
- Type
- Space
- Color
- Depth and motion
- Three compositions
- Defaults to question
- Subtract first
- Judge the result

## Mode sets the ambition

Choose the mode from the surface, not the product: a tool's landing page is Persuade; a fashion house's documentation is Read.

| Mode | Visitor | Ambition shows as | The world may lend |
| --- | --- | --- | --- |
| Persuade (landing, pricing, campaign) | Decides and acts | Full commitment: the opening makes the offer intelligible and desirable, exposes the real working action (a search, a slot picker, add to cart; not a link elsewhere), and shows something only this product can prove | Ground, type, structure |
| Operate (app, dashboard, admin, tool) | Completes a task | Precision and earned familiarity: a category-fluent user trusts it at once | Type, palette, density, one signature move; never layout, navigation, or controls |
| Read (docs, article, changelog) | Understands | The frame carries the world (masthead, rail, ground, openers, how code and tables are set); the column stays calm: a reading face, real contrast, 60 to 75 characters, monospace only for code | The frame, never the reading order |
| Experience (portfolio, gallery) | Is inside the work | The artifact leads from the first viewport; the interface recedes | The carrier |

Operate surfaces default to restraint, but color still does real jobs (shell, state, selection, data series): gray with one accent is the category default without its polish. One family, a fixed rem scale (not fluid), a second neutral layer for rails and panels, the full state vocabulary (hover, focus, active, disabled, selected, loading, error, warning, success, info), skeletons rather than spinners, empty states that teach, inline editing before a modal, overlays that escape clipping, and one vocabulary for buttons and controls across screens. Strangeness without purpose is the failure.

## Direction

State the direction in one sentence before styling: who it is for, how it should feel, and the one thing each screen must make obvious. "Calm and dense for a cashier who repeats one task all day" produces different type, spacing, and color than "confident and spacious for a first-time visitor."

Without a brief, name the subject, audience, and primary job (confirm only when consequential), then derive the direction from the audience's own world rather than a genre template:

1. List five to seven concrete visual systems the audience knows by heart: publications, notation, signage, packaging, data graphics, rituals. For each, say why it resonates, its ground and main colors, its type voice, and the one signature that makes it recognizable. For Operate and Read surfaces draw from graphic traditions and places, not from tools the audience operates; a terminal, scope, or cockpit comes back as a costume.
2. Choose by resonance, fuse at most two, and name one signature move concretely ("service health drawn as a transit map", "a schedule set in a timetable's column rhythm"). A world that appears only as a color scheme has not found its move.
3. Self-test: if someone could guess the aesthetic from the category alone, rework it. Generated interfaces converge on four looks: cream ground with high-contrast serif and a terracotta or red accent; near-black with one neon accent and glows; broadsheet hairlines with italic serif and tracked monospace labels; flat saturated ink with black boxes, hard offset shadows, and condensed display type. Each is legitimate when the brief asks for it.
4. Spend boldness once: one memorable decision, with everything around it disciplined. If every element got louder, the surface got flatter.
5. Illustrative content may be authored at full fidelity in greenfield work; label it synthetic and list what to replace. Never invent prices, customers, benchmarks, or capabilities (D8).

Restraint is a choice, not a fallback: quiet without a point of view collapses to generic. The test of restraint: remove one more decoration; if the screen still reads as complete, it was not needed. "Bolder" on one section means touching only that section and amplifying what the system already owns (its motif, its type scale at full strength) until it matches its neighbors; strip the copy and check that the bare structure still says what the section is. "Quieter" means fewer weights, flatter surfaces, tinted neutrals, and shorter motion.

## Type

- One family for interface text; a second only for a distinct role such as display or code. Operate and Read surfaces are well served by a system UI stack or one workhorse variable family.
- For Persuade and Experience, choose a face as you would a material for the subject, from its era, trade, or culture, not the first match for the genre. The faces generated interfaces converge on (Inter, Roboto, Fraunces, Geist, Plus Jakarta Sans, Space Grotesk, Playfair, Cormorant, Lora, Newsreader, Syne, DM Sans, DM Serif, Outfit, IBM Plex, Instrument Sans, Space Mono) need a reason no other face satisfies; "books want a serif" is not one. Self-host an open-license face; a system display face is not the display voice of a committed world.
- Few sizes with clear steps: a ratio near 1.2 for dense work (a fixed rem scale), 1.25 to 1.333 for reading and marketing. Adjacent roles less than 1.25 apart read as a flat hierarchy. Build hierarchy from size, weight, and color together. When two levels are hard to tell apart, increase their contrast instead of adding a level.
- Body at 16px with 1.5 to 1.7 line height for reading; 13 to 14px with 1.4 for dense operational screens; functional text never under 11px; headings at 1.1 to 1.25. Lines of 45 to 75 characters. Display type at most 6rem, long headlines smaller, tracking no tighter than -0.04em, wide tracking only on short uppercase labels.
- `text-wrap: balance` on headings, `text-wrap: pretty` on body (both progressive). Light text on a dark surface needs slightly more leading and tracking, and sometimes a weight step.
- Tabular numerals and right alignment for numeric columns. Never center long text; never set body in all caps or justified.

## Space

- One scale on a 4px base: 4, 8, 12, 16, 24, 32, 48, 64. An off-scale value needs a reason; an 8-only scale misses the useful middle steps.
- Proximity is grouping: the space between groups is at least twice the space within them, with more space above a heading than below it. Uniform spacing hides structure.
- Align to few shared edges; each extra alignment line is noise.
- Density follows frequency of use. Work repeated all day earns compact rows and controls, within pointer-target limits; an occasional or first-time task earns room and explanation.

## Color

- Choose a strategy before colors: restrained (tinted neutrals plus one accent), committed (one saturated color owns 30 to 60% of the surface), full palette (3 to 4 named roles), or drenched (the surface is the color). Persuade and Experience may take the bolder ones; Operate's floor is restrained. Color commits at region scale, not as scattered accents. Light or dark follows the real scene of use (who, where, under what light), never the category.
- Neutrals do most of the work: one gray ramp, tinted toward the brand hue only when that creates cohesion, for text, borders, and surfaces. On a colored surface derive secondary text from that surface's hue, not gray; prefer explicit colors to stacked alpha, which makes contrast depend on what sits behind.
- One accent, reserved for the primary action, selection, and focus. When everything is accented, nothing is.
- Build roles, not swatches: canvas and raised surfaces, ink and secondary ink, action, focus, selection, borders, status, data series. Status colors stay separate from brand, each with a paired foreground, and are never the only signal. Data also needs lightness, shape, or labels.
- Define colors in OKLCH so lightness steps look even, and reduce chroma near white and black. In a dark theme, raise surface lightness to show elevation and lower chroma; do not invert.

## Depth and motion

- Separate with space first, then a subtle border or background shift, then elevation. Shadows are for things that float and carry an offset and a soft blur; a zero-offset colored halo is decoration.
- Motion explains a change of state: 150 to 250ms, easing out on entry, faster on exit, and none under reduced motion or on actions repeated many times a minute. A surface earns at most one authored moment; Operate and Read surfaces skip page-load choreography. Timings, easing, and the performance rules are in [web platform](web-platform.md).
- Theme what the design did not draw, from the palette: text selection, caret, accent color, scrollbar, focus ring, underline offset, numerals. Theme native controls rather than replacing them. It is the cheapest signal that a page was built rather than assembled.

## Three compositions

| Surface | Structure | Why it works |
| --- | --- | --- |
| Operational list and detail | Context and the primary action in the header; filters beside results; a table with stable columns; detail in a panel or page that keeps the list's place | The eye returns to the same places, comparison runs down columns, and the next action is always in one spot |
| Focused task or form | One column no wider than about 40rem; fields grouped by decision; the primary action last, and persistent on small screens | One reading order, no competing targets, and the consequence is visible before committing |
| Product or landing page | One proposition, one piece of real evidence, and one action in the first view; later sections alternate claim and proof | A visitor decides in seconds; everything else supports that one decision |

## Defaults to question

These are the category's defaults, not bans; a brief can earn any of them, and D31 owns the rule. Reaching for one when the axis is free means no decision was made: rewrite the element rather than soften it.

- **Scaffolds:** same-size icon, heading, text cards as the page structure; nested cards; a rounded icon tile above a heading; the big-number hero-metric template; an eyebrow above a heading; section numbers without a real sequence; a centered hero over three cards; a modal where no interruption is needed.
- **Surface:** gradient text; purple-to-blue or cyan-on-dark palettes; cream as the reflex "tasteful" ground; decorative glass, glow, or radial halos; a colored border on one side of a card above 1px; hairline border plus wide shadow on a whole row of cards; hard offset shadows outside a neobrutalist world; decorative grid-line or stripe backgrounds; emoji as icons; monospace as a costume for "technical"; an italic serif hero; a long headline at display size.
- **Motion:** fade-and-rise on every section, hover lift on every card, marquees, bounce or elastic easing by reflex.

## Subtract first

Lightness is a design decision before it is a performance one. One or two brand hues plus neutrals; one family, 3 or 4 sizes, 2 or 3 weights; spacing and alignment before containers; one primary action, a few secondary, the rest revealed when needed; fewer component variants. Simplicity removes obstacles, not capability: keep accessibility and the information a decision needs. Mystery is not minimalism. Shipping less (fonts, images, CSS, JavaScript) is in [web platform](web-platform.md).

## Judge the result

Judge the rendered screen, not the code:

1. **Blur it.** The primary action and the three most important things stay identifiable.
2. **Remove color.** The hierarchy survives in grayscale.
3. **Stress it.** The longest label, an empty list, one row and hundreds, an error.
4. **Compare.** When unsure, render two variants of the same screen and keep the one where a first-time viewer finds the next step faster. Say which you chose and why.
5. **Subtract.** Remove one more decoration and see whether the screen still reads as complete.

These checks show that a composition communicates; whether it is beautiful still needs a person looking at it. Keep durable choices in the existing design owner. When the project has none, a `DESIGN.md` beside the tokens (named tokens, then overview, color, type, elevation, components) is a reasonable owner, with one token source and the other form a verbatim export; it is not required.
