---
name: el-design
description: Design, implement, and review usable web interfaces, including pages, forms, dialogs, tables, responsive layouts, interaction states, accessibility, copy, and frontend performance. Preserve the existing design system; includes focused Svelte 5 and Lumi guidance when those technologies are present.
---

# EL Design

Use [EL Architecture](../el-architecture/SKILL.md) for the shared workflow. This skill owns interaction and presentation. Read [Lumi](references/lumi.md) when Lumi is installed and [Svelte patterns](references/svelte-patterns.md) for Svelte work. Verify unfamiliar component APIs against the installed package.

## Establish direction

Inspect the target and its closest working neighbor. Identify the user, primary task, real content, device, network conditions, and constraints. Decide whether the request preserves, extends, or replaces the existing visual language; a missing design document does not make an application a blank canvas.

Choose composition by the visitor's purpose: completing work favors scanability and consistency; reading favors structure and typography; choosing a product favors a clear proposition and credible evidence; exploring visual work lets the artifact lead. A dashboard and its marketing page need different density.

## Foundation

- **D1. Follow the framework's state model.** In Svelte 5 rune-mode components, use typed `$state` for mutable input, `$derived` for computed values, and `$effect` for external synchronization with cleanup. Do not migrate the framework as an unrelated side effect.
- **D2. Extend the design system.** Prefer its public components, utilities, and semantic tokens. Use Lumi in Lumi products; preserve the adopted system elsewhere. Do not introduce a competing kit for one screen.
- **D3. Respect public styling boundaries.** Use supported variants and theme inputs; do not target private component selectors. Compose with supported primitives or add a reusable capability at its owner.
- **D4. Make color meaningful.** Pair status color with text or shape, and use semantic foreground/background pairs. Brand color must not redefine success, danger, or other feedback meanings.
- **D5. Keep one icon language.** Use the installed set, consistent stroke and sizing, and narrow supported imports. Hide decorative icons from assistive technology; controls still need names.
- **D6. The server owns rules.** Render authoritative data and capabilities. Client validation gives early feedback from shared limits; it never grants permission or guarantees a later mutation will succeed.
- **D7. Reuse state owners.** Contract types, transport, notifications, navigation, formatting, brand, and session each have an existing home. Locale, currency, and time zone come from product context.
- **D8. Ship working affordances.** Every visible action performs its promised task. Do not add decorative controls, fabricated metrics, invented testimonials, or empty future routes.

## Task and structure

- **D9. Make the next action obvious.** Establish hierarchy and a primary action appropriate to the task. Preserve familiar operational patterns; visual novelty must serve the intended experience.
- **D10. Design transitions.** Cover initial load, empty data, no results, partial results, permission limits, validation, submission, success, failure, offline/timeout, and stale data when applicable. Each state explains the next useful action.
- **D11. Explain prerequisites.** Use server-provided capabilities and reasons. Hide irrelevant or sensitive actions; disable with an explanation when discovery helps the user complete the task.
- **D12. Name destructive consequences.** Identify the affected object and irreversible effect. Choose confirmation or undo according to reversibility and risk; color alone is not confirmation.
- **D13. Choose density deliberately.** Prioritize frequent work, meaningful grouping, and fast scanning. Charts, ornament, and empty space must earn their place through the task or brief.
- **D14. Compose before styling.** Start from an appropriate existing structure: navigation, heading/context, actions, feedback, content. A card around every section is not a requirement.
- **D15. Match the data structure.** Tables support column comparison, lists support scanning, and cards represent independently meaningful objects. Bound growing results with pagination or justified virtualization; retain usable semantics on small screens.
- **D16. Preserve identity.** Use stable row keys, clear selection and status, and accessible action names identifying their target. Do not hide essential actions behind hover alone.
- **D17. Choose the interaction container.** Use a dialog for a short focused interruption, inline editing for local changes, and a page for deep links or complex work. CRUD does not automatically imply a modal.
- **D18. Fit layout to content.** Establish reading order, alignment, grouping, and responsive behavior before custom CSS. Test real labels and values rather than ideal placeholders.

## Forms and asynchronous work

- **D19. Give each draft a lifecycle.** Initialize once for its identity, preserve recoverable failures, and reset after success or deliberate discard. Match the installed dialog lifecycle, including exit animation and focus restoration.
- **D20. Prevent duplicates without trapping the user.** Guard concurrent submissions and indicate progress. Any restriction on dismissal during a critical operation needs a bounded wait and recovery; failure must not leave an unclosable modal. Closing the UI does not prove server cancellation.
- **D21. Keep errors near their owner.** Map field errors to controls, put operation errors in the form, and retain values. Associate messages programmatically. Separate submission failure from a later refresh failure.
- **D22. Support keyboard submission.** Use a real form, sensible Enter behavior, and focus the first invalid field or error summary. Clear stale errors when corrected without erasing useful feedback prematurely.
- **D23. Reconcile authoritative results.** Patch locally only when the response preserves filters, sort order, aggregates, and pagination. Otherwise invalidate the affected query through its existing owner; never append blindly to a filtered page.
- **D24. Preserve retry identity.** An idempotency key belongs to one immutable submission intent. Reuse it after an ambiguous response; changed payload requires a new intent and key. Reconcile an unknown result before offering another irreversible operation.
- **D25. Protect drafts across interruption.** Restore eligible drafts after reauthentication or navigation according to product privacy requirements. Never persist passwords, payment secrets, or another tenant's draft in shared browser storage.
- **D26. Match controls to their promise.** A checkbox typically contributes to a submitted form; a switch commonly changes an immediate setting. Persistent problems need persistent feedback; transient success can use notifications.
- **D27. Load data at its owner.** Use route loaders, actions, or the existing query layer. Key requests by route, tenant, filters, and identity; cancel or discard stale responses so old results cannot overwrite a newer view.
- **D28. Reuse the transport boundary.** Keep resource calls on the existing client or framework actions. Preserve cancellation, typed errors, authentication, and request context instead of scattering raw requests across components.
- **D29. Recover explicitly.** Handle reauthentication with a safe internal return path, denied access, field errors, rate limits, conflicts, and network failure. Distinguish a failed mutation from an unknown outcome.
- **D30. Choose rendering per surface.** Preserve the application strategy. SSR or prerendering can serve public discovery and reading; SPA behavior can suit interactive work. One browser-dependent component does not justify disabling SSR globally.

## Visual craft

- **D31. Make hierarchy intentional.** Use typography, proportion, spacing, and content to establish identity. Avoid habitual gradients, glass, icon grids, and metric cards unless the brief justifies them; honor an explicitly requested style.
- **D32. Assign surfaces a role.** Group related content, separate distinct tasks, and reserve elevation for actual layering. Reuse one treatment per role instead of nesting decorative containers.
- **D33. Keep geometry and motion coherent.** Use system spacing, radius, elevation, and timing tokens. Motion explains state or continuity, respects reduced motion, and does not delay input or comprehension.
- **D34. Reuse before inventing.** Seek an existing token, variant, primitive, or neighboring pattern. Extract a shared primitive when its consumers truly share a visual responsibility.
- **D35. Simplify without removing capability.** Reduce props, branching, duplicated controls, and decoration. Preserve readable contrast, feedback, discoverability, and accessibility.
- **D36. Scope CSS to its responsibility.** Follow project conventions, use low specificity and public tokens, and avoid global overrides that silently alter unrelated surfaces.
- **D37. Respond to content and input.** Prefer logical properties, flexible layouts, and content-driven breakpoints. Verify text expansion, zoom, touch, narrow screens, and supported writing directions; do not merely shrink desktop composition.
- **D38. Make overlays robust.** Use established primitives for positioning, clipping, stacking, scrolling, and focus. Test near viewport edges and under zoom.

## Accessibility and language

- **D39. Use native semantics first.** Links navigate; buttons act; labels identify inputs; headings describe structure; tables expose headers. ARIA supplements correct behavior rather than repairing a clickable generic element.
- **D40. Name controls accessibly.** Associate help and error text, label icon-only actions, and provide useful image alternatives. Convey state beyond color and announce important asynchronous changes without excessive repetition.
- **D41. Verify focus.** Every action works by keyboard with visible focus. Focus enters a dialog, stays within a modal, and returns sensibly on close. Choose an appropriate initial target on every input device; a heading can avoid opening the mobile keyboard. Honor standard dismissal except a justified, bounded critical operation.
- **D42. Preserve interaction semantics.** Do not nest controls inside a clickable card. Use menu roles only for actual menus, and provide keyboard alternatives to pointer-only gestures.
- **D43. Write in the product's language.** Prefer concrete verbs and objects, consistent domain terms, and direct consequences. Skill documentation is English; the product's locale follows its requirements.
- **D44. Make errors actionable.** Explain the problem and recovery without blame or internal diagnostics. Unexpected failures may expose a safe support reference, never stack traces or secrets.
- **D45. Explain consequences in help text.** State important constraints before submission, especially irreversible choices. Do not repeat a label as its description.
- **D46. Centralize formatting.** Use locale-aware helpers for dates, plurals, units, and exact money. Preserve identifier strings and business time semantics; do not convert exact decimals to floating point merely to render them.
- **D47. Measure user-facing cost.** Use project budgets and representative devices, data, and networks. Record loading, responsiveness, layout stability, and bundle impact where relevant; a fast development machine is not mobile evidence.
- **D48. Justify dependencies.** Apply architecture dependency criteria, including shipped bytes and accessibility behavior. Prefer existing primitives; a specialized accessible library can justify itself by removing real complexity.
- **D49. Remove unnecessary work.** Avoid request waterfalls, repeated context loads, oversized assets, and unused imports. Split expensive features at useful boundaries; excessive chunking or lazy-loading critical content can worsen the experience.

## Verify the rendered result

Run applicable project checks. For a material UI change, open the affected route and exercise its primary action and important recovery path. Inspect narrow and wide layouts, supported themes, keyboard navigation, zoom, long content, and console/network errors. Batch related visual checks, fix observed problems, and inspect again.

Use existing accessibility and visual-regression tools, but do not equate a clean scan with full accessibility. If the application cannot run, report the exact limitation and what was inspected; never claim a screenshot or interaction check that did not happen.
