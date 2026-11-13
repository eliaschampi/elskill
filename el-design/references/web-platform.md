# Web platform

Read when implementing a visual direction: CSS tokens, platform features, motion, fonts, images, and the UI performance budget. Prefer the platform to a dependency (D48); the project's browser targets decide what is usable. Visual decisions themselves live in [visual craft](visual-craft.md).

## Contents
- Tokens
- Platform features by tier
- Motion
- Performance

## Tokens

Three tiers in a cascade layer: primitives (OKLCH ramps from one hue), semantic roles, component aliases. A theme change remaps semantic roles. The values below are placeholders for a chosen direction, not a house palette.

```css
@layer reset, tokens, base, components, utilities;

@layer tokens {
  :root {
    color-scheme: light dark;
    --hue: 265;                                  /* replace with the chosen direction's hue */
    --bg:      light-dark(oklch(0.985 0.004 var(--hue)), oklch(0.16 0.012 var(--hue)));
    --surface: light-dark(oklch(1 0 0),                  oklch(0.21 0.014 var(--hue)));
    --ink:     light-dark(oklch(0.22 0.02 var(--hue)),   oklch(0.95 0.008 var(--hue)));
    --ink-2:   color-mix(in oklch, var(--ink) 62%, var(--bg));
    --line:    color-mix(in oklch, var(--ink) 14%, var(--bg));
    --accent:  light-dark(oklch(0.55 0.2 var(--hue)),    oklch(0.72 0.17 var(--hue)));
    --on-accent: oklch(0.99 0 0);                /* fallback */
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

Space on a 4px base; use `gap` for sibling rhythm. Dark themes raise surface lightness for elevation rather than inverting.

## Platform features by tier

Status checked 2026-11-12 against web.dev/baseline/2025, web.dev/baseline/2026, and the modern-css.com tracker. Statuses move: recheck MDN or Baseline and the project's browser targets before relying on one. "Newly available" means every major engine shipped it recently, not that older versions are covered.

| Tier | Use for | Features |
| --- | --- | --- |
| Established | Default choices | `oklch()`, `color-mix()`, relative color, container size queries, `:has()`, subgrid, nesting, `@layer`, `text-wrap: balance`, logical properties, `dvh` and `svh`, `@starting-style`, `light-dark()` colors, `<dialog>`, `@property`, Web Animations API |
| Baseline 2025 | Replace JavaScript | Popover API, invoker commands (`commandfor`, `command`), same-document View Transitions (`view-transition-name`, `view-transition-class`), `::details-content`, `scrollbar-color`, `text-autospace`, `abs()` and `sign()`, `dialog.requestClose()`, `scrollend`, `URLPattern` |
| Baseline 2026 (newly) | Replace libraries; check targets | Anchor positioning (`anchor-name`, `position-anchor`, `position-area`, `position-try`), scroll-driven animations (`animation-timeline: scroll()` or `view()`), `@scope`, `contrast-color()`, `field-sizing: content`, `text-box-trim`, `shape()`, container style queries, `:open`, `sibling-index()` and `sibling-count()`, `:active-view-transition`, Navigation API |
| Enhance only | Gate with `@supports`; never carries meaning | `corner-shape`, `if()`, customizable `<select>` (`appearance: base-select`), `interpolate-size`, scroll-state queries, `dialog closedby`, cross-document view transitions, `text-wrap: pretty` |

Ship correct semantics and layout first, then layer enhancements behind `@supports` or feature detection.

## Motion

Motion explains state, relationship, or hierarchy; decoration without a job is debt. Write a short thesis first: the one focal moment the surface earned (if any), the continuity changes that need explaining, the feedback that needs acknowledging, and which effects are expensive and how often they run. A generic fade-and-rise, hover lift, or scroll reveal is not a thesis.

| Duration | Use |
| --- | --- |
| 100 to 150ms | Immediate feedback |
| 150 to 300ms | Routine state change |
| 300 to 500ms | Layout, overlay, view transition |
| 500 to 800ms | A deliberately authored focal entrance |

Exit faster than entry. Use exponential ease-out for confident arrivals; overshoot, spring, or bounce only when the chosen world calls for it, small and deliberate.

- Reach past transform and opacity when the transition means something: shared-element and view transitions for continuity, bounded blur or backdrop for focus and depth, masks and `clip-path` for reveal. Keep those regions small and isolated.
- Keep content visible in the default state so a failed script never hides the page. Do not casually animate `width`, `height`, `top`, `left`, or margins; use transforms, FLIP, or grid techniques. Apply `will-change` only during a known animation.
- `prefers-reduced-motion` means fewer and gentler animations, not none: drop spatial movement, keep the opacity, color, and state changes that carry meaning. Pause non-essential loops when off-screen or hidden; never autoplay sound.
- Ambitious effects (shaders, WebGL or WebGPU, spring physics, scroll-driven scenes): propose two or three options with their support and cost trade-offs and get a pick before building. Use progressive enhancement with a fallback that still looks good (`@supports (animation-timeline: scroll())`; WebGPU only behind `navigator.gpu.requestAdapter()` with a WebGL2 or CSS fallback). Initialize lazily near the viewport, pause off-screen, and hold about 50 to 60fps on a mid-range device or simplify. Never use technical ambition to mask weak fundamentals.

## Performance

Measure before and after, on a real mid-range phone and a throttled network; fix the biggest bottleneck first. The published Core Web Vitals "good" thresholds are a floor, not a target: LCP under 2.5s, INP under 200ms, CLS under 0.1. A budget measured from the project's own baseline wins (A24).

- **Fonts:** a system stack or one variable family; subset with `unicode-range`; load only the weights and axes used; `font-display: swap` or `optional`; preload only the critical file; a metric-matched fallback (`size-adjust`, `ascent-override`, `descent-override`, `line-gap-override`) so the swap does not shift layout.
- **Images:** AVIF or WebP, `srcset` with `sizes`, explicit dimensions or `aspect-ratio` (CLS), lazy-load below the fold only and never the LCP image, quality around 80 to 85.
- **CSS and DOM:** flat DOM; `content-visibility: auto` and `contain` on long or independent regions; drop unused CSS; batch DOM reads before writes; virtualize very long lists.
- **JavaScript:** split by route, remove unused dependencies, defer non-critical scripts, move heavy computation to a worker, break up long tasks. Add no dependency for what CSS or HTML expresses.
- **Network:** paginate, compress, cache, serve static assets from one CDN origin, remove unused third-party scripts, prefetch likely next pages.
