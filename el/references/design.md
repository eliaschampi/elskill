# Design rules (D1-D49)

Interaction, presentation, accessibility. Preserve the existing design system. For a new or redesigned look read design-direction.md as well; Svelte work also reads svelte.md; RenUI products read renui.md.

## Contents
- Which rules apply
- Establish direction
- Foundation (D1-D8)
- Task and structure (D9-D18)
- Forms and async work (D19-D30)
- Visual craft (D31-D38)
- Accessibility and language (D39-D49)
- Verify the rendered result

## Which rules apply

| Change | Rules |
| --- | --- |
| Wording, labels, messages | D43-D46 |
| Styling within the existing system | D2-D5, D31-D38 |
| Page, list, table, navigation | D1-D18, D27-D30, D39-D42 |
| Report, dashboard, chart, activity view | D6, D10, D13-D15, read-models.md |
| Form, dialog, mutation | D1-D8, D19-D29, D39-D42 |
| Dependency, heavy asset, slow screen | D47-D49 |
| New visual language or redesign | Establish direction, D31-D38, design-direction.md |

Before writing JavaScript or adding a dependency for an overlay, positioning, transition, validation, or scroll effect, check whether the platform already provides it within the project's browser support: the `modern-web-guidance` skill when installed, otherwise MDN and Baseline (web-platform.md lists current candidates by tier).

## Establish direction

Inspect the target and its closest working neighbor. Identify the user, primary task, real content, device, network, and constraints. Decide whether the request preserves, extends, or replaces the visual language; a missing design document does not make an app a blank canvas.

Composition follows the visitor's purpose, chosen from the surface, not the product: Operate (finishing work) favors scanability, consistency, and earned familiarity; Read favors structure and typography; Persuade (choosing a product) favors a clear proposition, a working action, and credible evidence; Experience lets the artifact lead. A dashboard and its marketing page are different modes with different density; design-direction.md says how ambition scales by mode.

For a genuinely new visual system write a compact brief (purpose, content hierarchy, type roles, semantic palette, spacing and density, interaction states), implement and inspect one representative screen, then spread. Keep durable choices in the existing design owner; no separate document is required.

## Foundation

- **D1. Follow the framework's state model.** In Svelte 5 rune-mode components: typed `$state` for mutable input, `$derived` for computed values, `$effect` for external sync with cleanup. Never migrate the framework as a side effect.
- **D2. Extend the design system.** Prefer its public components, utilities, semantic tokens. RenUI in RenUI products; elsewhere preserve the adopted system. No competing kit for one screen.
- **D3. Respect public styling boundaries.** Supported variants and theme inputs only; never target private component selectors. Compose from supported primitives or add a reusable capability at its owner.
- **D4. Make color meaningful.** Pair status color with text or shape; use semantic foreground/background pairs. Brand color never redefines success, danger, or other feedback.
- **D5. One icon language.** The installed set, consistent stroke and size, narrow imports. Hide decorative icons from assistive tech; controls still need names.
- **D6. Respect the authority boundary.** The server enforces authorization and validates mutations. Client checks reuse native constraints or the server's own schema or function; they never restate a server rule. Render server-owned totals, balances, status, period bounds, and permissions from typed facts. Never infer them from formatted text. For a draft preview with all inputs available locally, reuse the same pure domain calculation. A preview that depends on private or changing server facts needs a server result; coalesce rapid edits and discard stale replies. Treat previews as provisional. Offline and client-only tools keep pure computation local.
- **D7. Reuse state owners.** Contract types, transport, notifications, navigation, formatting, brand, and session each have an existing home. Locale, currency, and time zone come from product context.
- **D8. Ship working affordances.** Every visible action performs its promised task. No decorative controls, fabricated metrics, invented testimonials, or empty future routes.

## Task and structure

- **D9. Make the next action obvious.** Give the primary task a clear path using familiar controls. When the brief targets workflow friction, try the smallest interaction change that addresses it. Compare the same task against the current flow on the relevant measure (steps, errors, or recovery), including keyboard use. Distinguish observed behavior from expected user benefit.
- **D10. Design transitions.** Initial load, empty, no results, partial results, permission limits, validation, submission, success, failure, offline/timeout, stale data. Each state names the next useful action.
- **D11. Explain prerequisites.** Use server-provided capabilities and reasons. Hide irrelevant or sensitive actions; disable with an explanation when discovery helps the task.
- **D12. Name destructive consequences.** Identify the object and the irreversible effect. Choose confirmation or undo by reversibility and risk; color alone is not confirmation.
- **D13. Choose density deliberately.** Frequent work, meaningful grouping, fast scanning. Charts, ornament, and empty space must earn their place through the task or brief.
- **D14. Compose before styling.** Start from an existing structure: navigation, heading and context, actions, feedback, content. Every action has a home (page header, section header, row, or dialog footer) and a view has one primary action; a control that fits none of them means a group is missing. A card around every section is not a requirement.
- **D15. Match the data structure.** Tables compare columns, lists support scanning, cards are independently meaningful objects. A table has one identifying column, aligned figures, a stated order, and only the columns the task compares. Bound growing results with pagination or justified virtualization; keep usable semantics on small screens.
- **D16. Preserve identity.** Stable row keys, clear selection and status, action names that identify their target. Essential actions never hide behind hover alone.
- **D17. Choose the interaction container.** Dialog for a short focused interruption, inline edit for local change, page for deep links or complex work. A form holds fields: choosing among many uses a search picker that shows the choice, not the collection, and work with lines, a growing list, or more than a screen of fields is a page. CRUD does not imply a modal.
- **D18. Fit layout to content.** Reading order, alignment, grouping, and responsive behavior before custom CSS. Gaps between groups at least double those within; few shared alignment edges; in working views start-align content and center only standalone blocks (empty states, sign-in). Test real labels and values, not ideal placeholders.

## Forms and async work

- **D19. Give each draft a lifecycle.** Initialize once per identity, keep recoverable failures, reset after success or deliberate discard. Match the installed dialog lifecycle, including exit animation and focus restoration.
- **D20. Prevent duplicates without trapping the user.** Guard concurrent submissions and show progress. Any restriction on dismissal during a critical operation needs a bounded wait and recovery; failure must not leave an unclosable modal. Closing the UI does not prove server cancellation.
- **D21. Keep errors near their owner.** Field errors on controls, operation errors in the form, values retained, messages associated programmatically. Separate submission failure from a later refresh failure.
- **D22. Support keyboard submission.** A real form, sensible Enter, focus on the first invalid field or an error summary. Clear stale errors when corrected without erasing useful feedback early.
- **D23. Reconcile authoritative results.** Patch locally only when the response preserves filters, sort, aggregates, and pagination; otherwise invalidate the affected query through its owner. Never blind-append to a filtered page.
- **D24. Preserve retry identity.** An idempotency key belongs to one immutable submission intent. Reuse it after an ambiguous response; a changed payload gets a new intent and key. Reconcile an unknown result before offering another irreversible operation.
- **D25. Protect drafts across interruption.** Restore eligible drafts after reauthentication or navigation per product privacy rules. Never persist passwords, payment secrets, or another tenant's draft in shared browser storage.
- **D26. Match controls to their promise.** A checkbox contributes to a submitted form; a switch changes an immediate setting. Persistent problems get persistent feedback; transient success may use notifications.
- **D27. Load data at its owner.** Route loaders, actions, or the existing query layer. Key requests by route, tenant, filters, identity; cancel or discard stale responses so old results never overwrite a newer view.
- **D28. Reuse the transport boundary.** Resource calls stay on the existing client or framework actions, preserving cancellation, typed errors, authentication, request context. No raw requests scattered through components.
- **D29. Recover explicitly.** Reauthentication with a safe internal return path, denied access, field errors, rate limits, conflicts, network failure. Distinguish a failed mutation from an unknown outcome. For a closed generated error-code union make missing presentation handlers fail static checks, and keep a safe runtime fallback for unknown wire codes across deployments.
- **D30. Choose rendering per surface.** Keep the app's strategy. SSR or prerendering for public discovery and reading; SPA behavior for interactive work. One browser-dependent component does not justify disabling SSR globally.

## Visual craft

- **D31. Make hierarchy intentional.** Typography, proportion, spacing, and content establish identity. Avoid habitual gradients, glass, icon grids, and metric cards unless the brief justifies them; honor an explicitly requested style.
- **D32. Give surfaces a role.** Group related content, separate distinct tasks, reserve elevation for real layering. One treatment per role, not nested decorative containers.
- **D33. Keep geometry and motion coherent.** System spacing, radius, elevation, and timing tokens. Motion explains state or continuity, respects reduced motion, never delays input or comprehension.
- **D34. Reuse before inventing.** Look for an existing token, variant, primitive, or neighboring pattern. Extract a shared primitive only when consumers share a visual responsibility.
- **D35. Simplify without removing capability.** Cut props, branching, duplicated controls, decoration, while keeping contrast, feedback, discoverability, accessibility.
- **D36. Scope CSS to its responsibility.** Follow project conventions; low specificity and public tokens; no global overrides that alter unrelated surfaces.
- **D37. Respond to content and input.** Logical properties, flexible layouts, content-driven breakpoints. Verify text expansion, zoom, touch, narrow screens, supported writing directions; do not merely shrink the desktop composition.
- **D38. Make overlays robust.** Established primitives for positioning, clipping, stacking, scrolling, focus. Test near viewport edges and under zoom.

## Accessibility and language

- **D39. Native semantics first.** Links navigate, buttons act, labels identify inputs, headings describe structure, tables expose headers. ARIA supplements correct behavior; it does not repair a clickable generic element.
- **D40. Name controls accessibly.** Associate help and error text, label icon-only actions, useful image alternatives. Convey state beyond color; announce important async changes without repetition.
- **D41. Verify focus.** Every action works by keyboard with visible focus. Focus enters a dialog, stays inside a modal, returns sensibly on close. Pick an initial target suited to every input device (a heading can avoid raising the mobile keyboard). Honor standard dismissal except a justified, bounded critical operation.
- **D42. Preserve interaction semantics.** No controls nested inside a clickable card. Menu roles only for real menus. Keyboard alternatives for pointer-only gestures.
- **D43. Write in the product's language.** Concrete verbs and objects, consistent domain terms, direct consequences. Skill text is English; product copy follows the product's locale.
- **D44. Make errors actionable.** State the problem and the recovery, without blame or internals. Unexpected failures may show a safe support reference, never stack traces or secrets.
- **D45. Explain consequences in help text.** State constraints before submission, especially irreversible ones. Never repeat the label as its description.
- **D46. Centralize formatting.** Locale-aware helpers for dates, plurals, units, exact money. Preserve identifier strings and business time semantics; never convert exact decimals to floats just to render.
- **D47. Measure user-facing cost.** Project budgets, representative devices, data, networks. Record loading, responsiveness, layout stability, bundle impact; a fast dev machine is not mobile evidence.
- **D48. Justify dependencies.** Apply architecture dependency criteria plus shipped bytes and accessibility behavior. Prefer existing primitives; a specialized accessible library can pay for itself by removing real complexity.
- **D49. Remove unnecessary work.** No request waterfalls, repeated context loads, oversized assets, unused imports. Split expensive features at useful boundaries; excessive chunking or lazy-loading critical content can hurt.

## Verify the rendered result

Run applicable project checks. For a material UI change open the affected route, exercise the primary action and the important recovery path, and inspect narrow and wide layouts, supported themes, keyboard navigation, zoom, long content, and console and network errors. Batch related visual checks, fix what you see, inspect again. Read the accessibility tree or a text snapshot first; screenshot only what pixels show (layout, alignment, contrast, imagery, motion).

Baseline: [WCAG 2.2 AA](https://www.w3.org/TR/WCAG22/) unless the project requires stricter. Check rendered text contrast (4.5:1 normal, 3:1 qualifying large text), non-text UI contrast (3:1), text resize to 200%, reflow at 320 CSS px for vertical scrolling, visible unobscured keyboard focus, and pointer targets of at least 24 by 24 CSS px or an applicable exception. These are focused checks, not proof of conformance.

When polishing, classify each drift before fixing it: missing token, one-off that a shared component should replace, conceptual mismatch with comparable flows, or local defect; fix at the narrowest correct level. Triage in this order: broken or blocked tasks, misleading state, inaccessible paths; then missing loading, empty, error, and disabled states; then flow, hierarchy, and system drift; then visual and motion inconsistency; then code and asset cleanup. Do not perfect one corner while the rest sits below the same bar.

Use existing accessibility and visual-regression tools, but a clean scan is not full accessibility. If the app cannot run, report the exact limitation and what was inspected; never claim a screenshot or interaction check that did not happen.
