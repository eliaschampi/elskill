# Web platform: modern, light, fast

Implementation toolkit for the look chosen in design-direction.md: tokens, platform features by tier, motion, and shipping less. Prefer the platform over a dependency (D48); the project's browser targets decide what is usable.

## Contents
- Tokens
- Platform features by tier
- Motion
- Performance

## Tokens

Three tiers in a cascade layer: primitives (OKLCH ramps from one hue), semantic roles, component aliases. A theme change remaps semantic roles. Space on a 4px base (4 8 12 16 24 32 48 64); grouping and alignment follow D18.

```css
@layer reset, tokens, base, components, utilities;

@layer tokens {
  :root {
    color-scheme: light dark;
    --hue: 265;                                  /* replace with the world's hue */
    --bg:      light-dark(oklch(0.985 0.004 var(--hue)), oklch(0.16 0.012 var(--hue)));
    --surface: light-dark(oklch(1 0 0),                  oklch(0.21 0.014 var(--hue)));
    --ink:     light-dark(oklch(0.22 0.02 var(--hue)),   oklch(0.95 0.008 var(--hue)));
    --ink-2:   color-mix(in oklch, var(--ink) 62%, var(--bg));
    --line:    color-mix(in oklch, var(--ink) 14%, var(--bg));
    --accent:  light-dark(oklch(0.55 0.2 var(--hue)),    oklch(0.72 0.17 var(--hue)));
    --on-accent: oklch(0.99 0 0);                /* fallback */
    --step-0: clamp(1rem, 0.95rem + 0.25vw, 1.125rem);
    --ease-out: cubic-bezier(0.16, 1, 0.3, 1);   /* exponential ease-out */
    --dur: 180ms;
  }
  @supports (color: contrast-color(red)) {
    :root { --on-accent: contrast-color(var(--accent)); }
  }
}

@layer base {
  :root { accent-color: var(--accent); caret-color: var(--accent); scrollbar-color: var(--line) transparent; }
  ::selection { background: color-mix(in oklch, var(--accent) 30%, transparent); }
  :focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  h1, h2, h3 { text-wrap: balance; }
  p { text-wrap: pretty; }
}
```

Depth: space first, then a border or background shift, then elevation; shadows are for things that float. Dark themes raise surface lightness for elevation; do not invert.

## Platform features by tier

Status checked 2026-11-12 against web.dev/baseline/2025, /2026 and the modern-css.com tracker; statuses move, so recheck MDN or Baseline and the project's browser targets before relying on one. "Newly available" means every major engine shipped it recently, not that older versions are covered.

| Tier | Use for | Features |
| --- | --- | --- |
| Established | Default choices | `oklch()`, `color-mix()`, relative color, container size queries, `:has()`, subgrid, nesting, `@layer`, `text-wrap: balance`, logical properties, `dvh`/`svh`, `@starting-style`, `light-dark()` colors, `<dialog>`, `@property`, Web Animations API |
| Baseline 2025 | Replace JS | Popover API, invoker commands (`commandfor`/`command`), same-document View Transitions (`view-transition-name`, `view-transition-class`), `::details-content`, `scrollbar-color`, `text-autospace`, `abs()`/`sign()`, `dialog.requestClose()`, `scrollend`, `URLPattern` |
| Baseline 2026 (newly) | Replace libraries; check targets | Anchor positioning (`anchor-name`, `position-anchor`, `position-area`, `position-try`), scroll-driven animations (`animation-timeline: scroll()` / `view()`), `@scope`, `contrast-color()`, `field-sizing: content`, `text-box-trim`, `shape()`, container style queries, `:open`, `sibling-index()`/`sibling-count()`, `:active-view-transition`, Navigation API |
| Enhance only | Gate with `@supports`; never carries meaning | `corner-shape`, `if()`, customizable `<select>` (`appearance: base-select`), `interpolate-size`, scroll-state queries, `dialog closedby`, cross-document view transitions, `text-wrap: pretty` |

Ship correct semantics and layout first, then layer enhancements behind `@supports` or feature detection.

## Motion

Motion explains state, relationship, or hierarchy; decoration without a job is debt. Write a thesis first: the one focal moment the surface earned (if any), the continuity changes that need explaining, the feedback that needs acknowledging, and which effects are expensive and how often they run. A generic fade-and-rise, hover lift, or scroll reveal is not a thesis.

| Duration | Use |
| --- | --- |
| 100-150ms | Immediate feedback |
| 150-300ms | Routine state change |
| 300-500ms | Layout, overlay, view transition |
| 500-800ms | A deliberately authored focal entrance |

Exit faster than entry. Use exponential ease-out (`--ease-out` above) for confident arrivals; overshoot, spring, or bounce only when the chosen world calls for it, small and deliberate. Operate and Read surfaces: fast feedback, no page-load choreography.

- Reach past transform and opacity when the transition means something: shared-element and view transitions for continuity, bounded blur or backdrop for focus and depth, masks and `clip-path` for reveal. Keep those regions small and isolated.
- Keep content visible in the default state so a failed script never hides the page. Do not casually animate `width`, `height`, `top`, `left`, or margins; use transforms, FLIP, or grid techniques. Apply `will-change` only during a known animation.
- `prefers-reduced-motion`: fewer and gentler, not none. Drop spatial movement; keep the opacity, color, and state changes that carry meaning. Pause any non-essential loop when off-screen or hidden; never autoplay sound.
- **Ambitious effects** (shaders, WebGL or WebGPU, spring physics, scroll-driven scenes): propose two or three options with their support and cost trade-offs and get a pick before building. Progressive enhancement with a fallback that still looks good (`@supports (animation-timeline: scroll())`; WebGPU only behind `navigator.gpu.requestAdapter()` with a WebGL2 or CSS fallback). Lazy-initialize near the viewport, pause off-screen, hold about 50-60fps on a mid-range device or simplify. Never use technical ambition to mask weak fundamentals, and never stack competing spectacle.

## Performance

Measure before and after, on a real mid-range phone and a throttled network; fix the biggest bottleneck first. Published Core Web Vitals "good" thresholds are a floor, not a target: LCP under 2.5s, INP under 200ms, CLS under 0.1. A project budget measured from its own baseline wins (A24).

- **Fonts:** system stack or one variable family; subset with `unicode-range`; load only the weights and axes used; `font-display: swap` (or `optional`); preload only the critical file; metric-matched fallback (`size-adjust`, `ascent-override`, `descent-override`, `line-gap-override`) so the swap does not shift layout.
- **Images:** AVIF or WebP, `srcset` plus `sizes`, explicit dimensions or `aspect-ratio` (CLS), lazy-load below the fold only, never the LCP image, quality around 80-85.
- **CSS and DOM:** flat DOM; `content-visibility: auto` and `contain` on long or independent regions; drop unused CSS; batch DOM reads before writes; virtualize very long lists.
- **JS:** split by route, remove unused dependencies, defer non-critical scripts, move heavy computation to a worker, break up long tasks. Do not add a dependency for what CSS or HTML expresses.
- **Network:** paginate, compress, cache, one CDN origin for static assets; remove unused third-party scripts; prefetch likely next pages.
