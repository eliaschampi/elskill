# RenUI integration

Only for a product using RenUI (`@renui/svelte`, 2.x). RenUI was published as Lumi UI (`@lumi-ui/svelte`) through 1.2.1; a product still importing that name needs the 2.0 migration below. Inside the RenUI library itself follow its `AGENTS.md` and keep components domain-neutral. This is a lookup and integration guide, not a frozen API: installed exports, types, and source outrank it. Checked against 2.0.1 (peer `svelte ^5.56.4`; browsers Chrome/Edge 125+, Firefox 128+, Safari 18+ because colors use CSS relative color syntax; LTR only).

## Inspect before composing

Resolve `@renui/svelte` from the package manager and lockfile; read its export map before assuming a path. The npm tarball ships `dist` only. Docs live in the repo `eliaschampi/renui`: `docs/CONSUMER_REFERENCE.md` (recipes), `docs/GUIDE.md` (one section), `docs/UPGRADE.md`. Use them only when the version matches, and trust `dist` where they disagree.

| Question | Evidence |
| --- | --- |
| Is the component or helper public? | `dist/index.d.ts` and the export map |
| Which props, snippets, callbacks exist? | `dist/components/<Name>/types.d.ts`; the `.svelte` file when snippets are local |
| Which semantic token exists? | `dist/styles/tokens.base.css` |
| Which composition class exists? | `dist/styles/{layout,utilities,patterns}.css` |
| How is it used here? | Nearest working screen and existing local wrapper |

Entry points: `@renui/svelte` (components, types, locale, formatters, `portal`, icon registry API), `/styles`, `/styles/{tokens.base,base,layout,utilities,patterns,charts}.css`, `/icons` (optional `renIcons` map), `/color-scheme`, `/drive` (pure Drive helpers and copy).

## Integration owners

- Import `@renui/svelte/styles` once at the root layout (tokens + base + layout + utilities), then the product theme file. `patterns.css` is opt-in: load it in the layouts that use it. SEO-sensitive public trees can import only `tokens.base.css`, `base.css`, and `utilities.css`. Global layers are ordered `ren.tokens, ren.base, ren.components, ren.layout, ren.patterns, ren.utilities`, so unlayered product CSS wins; restyle through tokens and props, never component internals.
- One notification owner: a single `createToaster()` in client code, one `<Toaster>`, `show()` from handlers.
- `setRenLocale({ locale, currency, timeZone, messages })` once at the root layout. Context-based, so SSR requests stay isolated. English is the default; `renEs` (and `renDriveEs` from `/drive`) add Spanish. Keep `messages` a stable object, or pass a function to follow reactive state. Explicit label props win. Prefer `formatNumber`, `formatDate`, `getInitials` over app copies.
- Theme seeds live in one product theme file loaded after the styles: `--ren-brand-primary`, `--ren-brand-secondary`; status seeds `--ren-status-{success,warning,danger,info}`; optional `--ren-color-canvas` and `--ren-color-neutral` (calibrate light and dark). Never reassign derived `--ren-color-*` tokens.
- Color scheme is optional: one `createColorScheme(options)` controller plus one `<ColorSchemeScript {...options} />`, sharing a single options object (`system | light | dark`; default storage key `ren-color-scheme`). With a strict CSP use `createColorSchemeBootScript` and a nonce.
- Icons: pass Lucide components via deep imports (`@lucide/svelte/icons/<name>`). String names render nothing until `registerIcons` (for example `renIcons`) runs in the layout that needs them.

## Choose a public primitive

| Intent | Candidate to verify |
| --- | --- |
| Page context and primary action | `PageHeader` |
| Related surface, titled section | `Card`, `DashboardSection` |
| Text, exact input, multiline | `Input`, `NumberInput`, `Textarea` |
| Visible exclusive choice | `SegmentedControl`; `Radio` when options need description |
| Several independent toggles | `ToggleGroup`, `Checkbox`, `Switch` |
| Long or remote choice list | `Select`, `RemoteSelect` |
| Column comparison, linear scanning | `Table`, `List`, `ListItem` |
| Persistent feedback, transient confirmation | `Alert`, `Toaster` |
| Focused interruption, anchored menu | `Dialog`, `Dropdown`, `Context` |
| Empty, failed, loading | `EmptyState`, `ErrorState`, `Skeleton`, `Loading` |

Names are a search map, not permission to invent props. Verify that navigation uses `href`, actions use `onclick`, icons accept components, and `Table` has a stable `rowKey` when records lack `id` or `key`.

## Compose with the installed vocabulary

Use `ren-stack`, `ren-flex`, `ren-grid`, `ren-container`, `ren-dashboard-layout`, `ren-layout--two-columns`, and the sidebar and page-sidebar classes before custom CSS. A grid modifier needs the base `ren-grid`; breakpoints are rem-based, so match the installed definitions and never copy values from another product.

Custom composition uses `--ren-*` tokens for spacing, text, surfaces, borders, control size, radius, elevation, focus, and motion. A solid role background pairs with its `-foreground`; soft surfaces use `-bg`; `.ren-tone` with a `--secondary|--success|--warning|--danger|--info` variant sets the accent for consumer CSS. Scope product styles to product elements; never override private selectors or derived tokens to force a variant.

Lumen look: brand-tinted canvas, opaque surfaces, thin borders, soft elevation, no decorative glass or gradient. `.ren-bg--glass` remains but renders opaque.

## Migrating from Lumi UI 1.x

Rename `@lumi-ui/svelte` to `@renui/svelte` (same subpaths), `--lumi-*` to `--ren-*`, `.lumi-*` to `.ren-*`, `lumi.*` layers to `ren.*`, `Lumi*`/`useLumiLocale` to `Ren*`/`useRenLocale`, and storage key `lumi-color-scheme` to `ren-color-scheme` (default-key preferences reset once). Props and entry points are unchanged. Removed glass, gradient, and blur tokens are listed with replacements in `docs/UPGRADE.md`. From a RenUI checkout run `node scripts/migrate-2.0.mjs <app-dir>` (dry run first, then `--write`). It exits non-zero until no `error:` or `manual:` line remains. Then run the app's `svelte-check`, build, tests, and a light and dark visual pass.

## Traps to exercise

- A clickable `Card` renders as a button; no nested interactive children. `ListItem` with `href` or `onclick` uses a stretched target, so `trailing` actions stay real siblings.
- `Dropdown` and `Context` are menus: keep menu roles; use another primitive for generic popover content. Overlays opened inside a `Dialog` render inside it.
- Check opening animation, exit animation, and focus restoration through the documented lifecycle; never unmount a dialog early.
- `MessageList` needs a height; pass `busy` while a reply streams and `loading` while history loads.
- Icon-only controls need an accessible name.
- Check portal and clipping under nested scrolling, near viewport edges, and at zoom.
- Confirm errors are associated with inputs and that loading or disabled controls stay understandable.
- Test theme pairs, long content, keyboard focus, and target sizes on the rendered page; token use alone proves neither usability nor contrast.
