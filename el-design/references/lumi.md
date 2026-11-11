# Lumi integration

Read only for a product using Lumi. Inside the Lumi library itself, follow its contributor instructions and preserve domain-neutral component contracts. This is a lookup and integration guide, not a frozen API specification.

## Inspect before composing

Resolve `@lumi-ui/svelte` from the project's package manager and lockfile. Package layouts can change; inspect its export map before assuming a path.

| Question | Evidence to inspect |
| --- | --- |
| Is the component or helper public? | Package exports and exported type declarations |
| Which props, snippets, and callbacks exist? | Component declarations and implementation when declarations are incomplete |
| Which semantic token exists? | Exported token stylesheet |
| Which composition class exists? | Exported core, layout, utilities, and optional pattern stylesheets |
| How is it used here? | Nearest working screen and existing local wrapper |

Typical installed paths include `dist/index.d.ts`, `dist/components/<Name>/types.d.ts`, and `dist/styles/`; confirm them. When available, the library's consumer reference provides recipes. Do not copy a recipe from a different version without checking its contract.

## Integration owners

- Import shared styles once at the appropriate layout. Load optional pattern styles only for surfaces that use them; follow the package's documented cascade order.
- Keep one notification owner and renderer. Use its public API from event handlers instead of creating a toaster per component.
- Configure locale, currency, time zone, and messages from the product's locale owner. Do not mutate process-global locale per request in SSR; verify the installed locale API's scope.
- Keep theme seeds in one product theme file. Where supported, `--lumi-brand-primary` and `--lumi-brand-secondary` define brand inputs; derived semantic colors remain library-owned.
- Use the documented color-scheme controller and pre-paint initialization when present. Avoid duplicated controllers and theme flashes.

## Choose a public primitive

| Intent | Candidate to verify |
| --- | --- |
| Page context and primary action | `PageHeader` |
| Related surface or titled section | `Card`, `DashboardSection` |
| Text, exact input, multiline text | `Input`, appropriate numeric input, `Textarea` |
| Visible exclusive choice | `Radio`, `SegmentedControl` |
| Long or remote choice list | `Select`, `RemoteSelect` |
| Form boolean or immediate setting | `Checkbox`, `Switch` |
| Column comparison or linear scanning | `Table`, `List`, `ListItem` |
| Persistent feedback or transient confirmation | `Alert`, existing `Toaster` |
| Focused interruption or anchored menu | `Dialog`, `Dropdown`, `Context` |
| Empty, failed, or loading content | `EmptyState`, `ErrorState`, `Skeleton`, `Loading` |

Candidate names are a search map, not permission to invent props. In particular, verify whether navigation uses `href`, action uses `onclick`, icons accept components, and data tables need an explicit stable `rowKey`.

## Compose with the installed vocabulary

Look for existing `lumi-stack`, `lumi-flex`, `lumi-grid`, container, dashboard, and sidebar patterns before custom CSS. Base classes and modifiers may need to be used together; a modifier alone may not establish layout. Match the actual breakpoint definitions rather than copying fixed values from another product.

For custom composition, use verified semantic tokens for spacing, text, surfaces, borders, control size, radius, elevation, focus, and motion. Pair a solid semantic background with its intended foreground. Scope product styles to product elements; do not override private selectors or derived tokens to force a variant.

## Integration traps to exercise

- Verify whether opening animation requires mounting closed and then changing `open`; use the local dialog wrapper if it already owns that behavior.
- Unmount only at the lifecycle event documented by the installed version. Do not remove a dialog before exit animation or focus restoration completes.
- Check the rendered element of clickable cards before placing interactive children inside them.
- Preserve menu semantics in `Dropdown` and `Context`; use a suitable primitive for generic popover content.
- Check portal and clipping behavior under nested scrolling, near viewport edges, and at zoom.
- Confirm error messages are associated with inputs and that loading or disabled controls remain understandable.
- Test theme pairs, long content, keyboard focus, and target widths on the rendered page. Token usage alone does not prove usability or contrast.
