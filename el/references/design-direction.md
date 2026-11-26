# Design direction: a distinctive, modern, light look

Read when creating a visual language, redesigning, polishing, or building a landing, marketing, portfolio, docs, or dashboard surface. An installed design system's tokens and components win over everything here; this fills decisions the project has not made. Pair with design.md (D31-D38); implementation details are in web-platform.md. Synthesis informed by pbakaus/impeccable (Apache-2.0), rewritten.

## Contents
- Refine, extend, or replace
- Mode sets the ambition
- Derive the world
- Color strategy
- Type
- Craft floor
- Tells of no decision
- Subtract first
- Persist and judge

## Refine, extend, or replace

- **The brief wins.** Honor pinned aesthetics, eras, fonts, and palettes even against a tell below; steering a clear brief toward your taste is failure.
- **Refine** keeps identity, behavior, copy, and everything outside scope. **Extend** (a section or state inside an established surface) inherits it; no identity exercise for a local addition. **Replace** keeps product truth, content, function, and constraints, and treats the old look as evidence, not authority; never split the difference into polish on the discarded look. A missing design doc does not mean greenfield: inspect the incumbent first.
- **"Bolder" on a section:** touch only the named target. Amplify what the system already owns (its motif, its type scale at full strength) to the conviction its neighbors reach; one decisive move, then quiet everything around it. Skeleton test: strip the copy; does the bare structure still say what the section is? **"Quieter":** fewer weights, flatter surfaces, tinted neutrals, shorter motion. Restraint still needs a point of view; generic quiet is gray text on white and a grid of identical cards.

## Mode sets the ambition

Choose the mode from the surface, not the product (a tool's landing page is Persuade; a fashion house's docs are Read).

| Mode | Visitor | Ambition shows as | The world may lend |
| --- | --- | --- | --- |
| Persuade (landing, pricing, campaign) | Decides and acts | Full commitment: the opening makes the offer intelligible and desirable, exposes the real working action (a search, a slot picker, add to cart; not a link elsewhere), and shows something only this product can prove | Ground, type, structure |
| Operate (app, dashboard, admin, tool) | Completes a task | Make frequent work easy and errors recoverable | Type, palette, density; let the task guide changes to layout, navigation, and controls (D9) |
| Read (docs, article, changelog) | Understands | The frame carries the world (masthead, rail, ground, openers, how code and tables are set); the column stays calm: reading face, real contrast, 60-75ch, mono only for code | The frame, never the reading order |
| Experience (portfolio, gallery) | Is inside the work | The artifact leads from the first viewport; the interface recedes | The carrier |

Ask product questions only when evidence leaves them open: Persuade (who must act, what they should believe, which proof exists); Operate (task, key states, frequency); Read (the reader's question, structure); Experience (what leads).

**Operate defaults.** Use a readable type scale and consistent controls. Give color a job in selection, status, or data. Show the states the task can reach, choose loading feedback that fits the wait, and keep recovery close to the failed action. Use overlays when the task warrants an interruption, and check that they escape clipping.

## Derive the world

For Persuade, Experience, a Read frame, or a replacement:

1. **Ground it.** One line each: the product's unique mechanism; the audience's real scene (who, where, under what light); its cultural home; what this first surface must prove. Name the page this category always ships and its predictable opposite; both are the rut.
2. **Find a reference the audience recognizes.** A publication, sign, package, or notation may suggest how to organize the content. Start with the brief's direction when it supplies one. Explore alternatives only while a consequential visual choice remains open.
3. **Choose by resonance.** Fuse at most two and name one signature move concretely ("service health drawn as a transit map", "a schedule set in a timetable's column rhythm"). A world that shows up only as a color scheme has not found its move.
4. **Self-test.** If someone could guess the aesthetic from the category alone, rework it. Models converge on four looks: cream ground, high-contrast serif, terracotta or red accent; near-black with one neon accent and glows; broadsheet hairlines, italic serif, tracked mono labels; flat saturated ink with black boxes, hard offset shadows, condensed display. Each is legitimate when the brief asks for it; landing there by default means no decision was made.
5. **Spend boldness once.** One memorable decision (a type-led hero, a shared-element transition from list to detail, a scroll-linked narrative, a domain-native data idiom). If every element got louder, the surface got flatter.
6. **Truth binds claims, not demonstrations.** In greenfield work author illustrative content at full fidelity, label it synthetic, and list what to replace. Never invent prices, customers, benchmarks, or capabilities (D8).

## Color strategy

Choose the strategy before the colors: **Restrained** (tinted neutrals plus one accent), **Committed** (one saturated color owns 30-60% of the surface), **Full palette** (3-4 named roles), **Drenched** (the surface is the color). Persuade and Experience may take the bolder ones; Operate's floor is Restrained. Color commits at region scale, not as scattered accents. Light or dark follows the scene sentence from step 1, never the category.

Build roles, not swatches: canvas and raised surfaces, ink and secondary ink, action, focus, selection, borders, success, warning, error, info, data series. Ramps in OKLCH: vary lightness, reduce chroma near white and black. On a colored surface derive secondary text from that surface's hue, never gray; prefer explicit colors to stacked alpha, which makes contrast depend on what sits behind. Tint neutrals toward the hue only when it creates cohesion. Dark themes get explicit elevation steps and lower chroma; never invert. Data needs lightness, shape, or label as well as hue.

## Type

- **Operate and Read:** a system UI stack or one workhorse variable family: lightest and most familiar. **Persuade and Experience:** choose a face as you would a material for the subject, from its era, trade, or culture, not the first match for the genre. The faces models converge on (Inter, Roboto, Fraunces, Geist, Plus Jakarta Sans, Space Grotesk, Playfair, Cormorant, Lora, Newsreader, Syne, DM Sans, DM Serif, Outfit, IBM Plex, Instrument Sans, Space Mono) need a reason no other face satisfies; "books want a serif" and "tech wants mono" are not reasons. Self-host an open-license face; never a system display face as the display voice of a committed world.
- **Hierarchy:** few roles; adjacent steps at least 1.25x apart or the hierarchy is flat; combine size, weight, space, and tone. Ratio 1.125-1.2 for dense work, 1.25-1.333 for reading and marketing (fluid `clamp()` only here).
- **Numbers:** body 16px (floor 14), functional text never under 11px, body leading 1.5-1.7 (wider measure needs more), headings 1.1-1.25, measure 45-75ch, display at most 6rem and long headlines smaller, tracking no tighter than -0.04em, wide tracking only on short uppercase labels, never all-caps or justified body.
- **Breaks:** `text-wrap: balance` on headings and short centered blocks, `text-wrap: pretty` on body (both progressive).
- **Light on dark:** slightly more leading and tracking, one weight step up. Paragraph rhythm by spacing or first-line indent, not both. Tabular numerals for data.

## Craft floor

Check the built render, batched in one look; never announce the checklist.

- **Contrast** per design.md; secondary text on color tinted from the surface.
- **Depth:** shadows carry an offset and a soft blur; a zero-offset colored halo is decoration.
- **Spacing:** tight groups, generous separation, more above a heading than below, a 4px-base scale (an 8-only scale misses the middle steps), `gap` for siblings. Read computed values. Squint test: primary, secondary, and groups still read in order.
- **Browser surfaces:** theme what you did not draw, from the palette: `::selection`, `caret-color`, `accent-color`, `scrollbar-color`, `:focus-visible` ring, underline thickness and offset, tabular numerals, `::placeholder`. Theme native controls; do not replace them. It is the cheapest signal a page was built, not assembled.
- **States and content:** hover, focus, disabled, loading, error, empty, with real content. Content is visible at rest: reveals enhance, never gate. DOM and focus order match visual order.
- **Copy:** the product's language, plain and active, controls name their action. Avoid em-dash overuse, buzzwords, aphoristic cadence.

## Tells of no decision

Keep one only when the brief earns it.

- **Scaffolds:** same-size icon-heading-text cards as the page structure; nested cards; a rounded icon tile above a heading; the hero-metric template (big number, small label, stats, accent); an eyebrow or kicker above a heading (no brief earns it back); numbered sections unless the sequence is information; centered hero over three cards; a modal where no interruption is needed.
- **Surface:** gradient text; purple or violet gradients, cyan on dark; cream or beige as the reflex "tasteful" ground; glass and blur as decoration; colored glow shadows, radial halos and spotlights; a colored `border-left` or `border-right` above 1px on cards and alerts; hairline border plus wide shadow on a whole row of cards; hard offset shadows outside a world that chose neobrutalism; decorative grid-line or stripe backgrounds (grids belong to canvases and maps); sparklines and progress rings as filler; geometric masks faking organic contours.
- **Type and icons:** italic serif hero; a long headline at display size; monospace as a costume for "technical"; emoji or Unicode glyphs as icons (one drawn set, one stroke); uppercase micro-labels above everything.
- **Motion:** fade-and-rise on every section; hover lift on every card; auto-scrolling marquees; pulsing dots; bounce or elastic easing by reflex.

If the project already uses Impeccable, its detector (deterministic rules, no model call) flags many of these; findings are defect evidence and a clean scan is a floor, not proof of quality.

## Subtract first

Lightness is a design decision before it is a performance one. One to two brand hues plus neutrals; one family, 3-4 sizes, 2-3 weights; spacing and alignment before containers; flat structure; one primary action, secondary actions few, the rest hidden until needed; fewer variants (three cover most cases). Simplicity removes obstacles, not capability: keep accessibility and the information a decision needs. Mystery is not minimalism. Shipping less (fonts, images, CSS, JS) is in web-platform.md.

## Persist and judge

**Persist.** When no design owner exists, record the direction in a root `DESIGN.md` (A3): YAML frontmatter of named OKLCH tokens, then Overview, Colors, Typography, Elevation, Components, Do and Do Not. One token source (usually the CSS); the other form is a verbatim export.

**Judge the render**, not the code, at about 375, 768, and 1280px, light and dark, with the session's browser tooling:

1. **Blur it:** the primary action and the three most important things stay identifiable.
2. **Remove color:** the hierarchy survives in grayscale.
3. **Stress it:** longest label, empty list, one row and hundreds, an error.
4. **Compare** variants only if the choice is still open. Use a sketch or focused render that exposes the difference. Claim a speed gain only if timed on the task.
5. **Subtract:** remove one more decoration; if the screen still reads as complete, it was not needed.

These show a composition communicates; whether it is beautiful still needs a person looking at it.
