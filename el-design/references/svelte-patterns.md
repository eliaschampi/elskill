# Svelte implementation patterns

Use for Svelte applications; respect the installed Svelte/SvelteKit versions and existing transport strategy. The patterns below describe responsibilities, not APIs to copy without their implementations.

## State and ownership

| Information | Usual owner |
| --- | --- |
| Shared route context and session | Existing layout loader or server context |
| Page data and query parameters | Route loader or established query layer |
| Current form draft and submission state | Form instance keyed by resource/draft identity |
| Values computed from state | `$derived` in rune-mode components |
| Browser subscription or external integration | Lifecycle hook or `$effect` with cleanup |
| API errors, authentication, request metadata | Existing transport client or framework actions |
| UI authorization hints | Server-provided capabilities |

Use `$props` for typed component inputs and the project's supported snippets/events. Do not copy props into mutable state unless the component deliberately owns a draft. A prop update should not silently reset in-progress user input.

Reserve `$effect` for synchronization outside the reactive graph. Do not use it to maintain a second copy of computable state. Dispose subscriptions, listeners, timers, and obsolete requests; ensure browser-only APIs do not execute during SSR.

## Modern Svelte 5 surface

Check the installed version and configuration first; use only what the project already provides.

- `{@attach fn}` (Svelte 5.29 and newer) is the reactive replacement for actions in new code: it runs in an effect, re-runs when state it reads changes, may return cleanup, and passes through components by prop spreading. `fromAction` adapts existing `use:` actions; type factories with `Attachment` from `svelte/attachments`.
- `<svelte:boundary>` with `pending` and `failed` snippets contains async and error states at a useful granularity, not around every component.
- `$state.raw` for large or immutable data that is replaced rather than mutated; `$derived.by` for multi-statement derivations; `$bindable` only for deliberate two-way props.
- Experimental and opt-in: `await` in components and `$derived` requires `compilerOptions.experimental.async` (5.36 and newer; the flag is removed in Svelte 6, and details may change in minor releases), and SvelteKit remote functions (`query`, `form`, `command`, `prerender`; from 2.27; `experimental.remoteFunctions` plus `compilerOptions.experimental.async`). Use either only where the project has enabled it; otherwise stay on loaders and actions.

## SvelteKit 3

Check the `@sveltejs/kit` major first; on 2.x keep the 2.x APIs. The points below follow the official 3.x migration guide and replace what older knowledge suggests. `npx sv migrate sveltekit-3` automates much of the move; upgrade to the latest 2.x first for targeted deprecation warnings. Server-side changes (CSRF, cookies, `handleError`) are in the [SvelteKit and Kysely reference](../../el-backend/references/sveltekit-kysely.md).

- Floor: Node 22.17, TypeScript 6, Svelte 5.57.1, Vite 8.0.12, `@sveltejs/vite-plugin-svelte` 7.
- `svelte.config.js` is no longer read: pass project config to the `sveltekit({...})` plugin in `vite.config.js` (`kit.*` options become top level, beside `compilerOptions`).
- `$lib` is gone: declare `#lib` and `#lib/*` in `package.json` `imports` and import with explicit extensions (`#lib/foo.js`). Param matchers live in one `src/params.ts` built with `defineParams`.
- `$app/stores` is removed: use `$app/state` and read `page` without `$`. `$app/environment` is now `$app/env`; `$env/*` is deprecated for `$app/env/private` and `$app/env/public`; `base`, `assets`, and `resolveRoute` left `$app/paths` for `resolve(...)` and `asset(...)`, whose paths have no leading slash.
- Navigation: `refreshAll` replaces `invalidateAll`; `pushState` and `replaceState` give way to `goto(url, { shallow: true, state })`; `goto` rejects for URLs that match no route; a link to the current URL runs `refreshAll()`; `page.url` is read-only; `data-sveltekit-*` uses `false`, not `'off'`.
- Enhanced forms (`use:enhance`) see the status passed to `fail` instead of 200, and navigate when `action` targets another page. Remote-function forms need `{...form.fields.x.as('text')}`, not a hand-written `name`.

## Loading and navigation

- Load page data through its route/query owner; use framework-provided fetch/context where required for server rendering and authentication.
- Reuse the existing context invalidation key. Navigation should not reload stable context unnecessarily, but membership, tenant, and session changes must invalidate stale context.
- Include route identity, tenant, sort, filters, and cursor in request identity. Abort obsolete requests when supported and discard responses whose identity is no longer current; abort alone is insufficient protection against every late completion.
- Reset cursor and result accumulation when filters or ordering change. Deduplicate stable IDs only as pagination reconciliation, not to hide a server query defect.
- Keep server state out of process-global mutable stores during SSR.

## Draft and submission lifecycle

Use an existing form helper when it already owns these transitions. Otherwise implement only the state the current interaction needs:

```text
editing → submitting → committed → closed or editing a new intent
                    → rejected  → editing with values and errors
                    → unknown   → reconciliation or a safe retry
```

1. Initialize the draft for a stable resource/draft identity. Keep changes local until submission; do not mutate loader data through shared object references.
2. Submit a real form, guard duplicate activation, and capture the payload and idempotency key together when the backend contract supports them.
3. Reuse that pair on retry after a timeout. If the user changes the payload, resolve an uncertain prior outcome before starting a new irreversible intent.
4. Map server field locations through the existing form convention. Keep operation errors in the form and focus an appropriate invalid control or summary.
5. Mark server success before subsequent UI refresh work. If invalidation fails after commit, show that saving succeeded and refreshing failed; do not encourage another create request.
6. Reset or dismiss only after the accepted lifecycle transition. Reenable recovery after rejection or timeout; a busy flag must not remain stuck.

Store eligible drafts only under the product's privacy rules, scoped to account, tenant, and resource, with explicit cleanup. Do not persist authentication secrets or sensitive payment input.

## Dialogs

Use the established wrapper and actual open/close callbacks. Keying a form by draft identity can intentionally create a fresh instance; keying it by every reactive change destroys input and focus.

Route close-button, Escape, backdrop, Cancel, and applicable back/navigation exits through one dismissal decision for dirty and submitting states. Preserve or confirm discarding unsaved changes as the product requires; any temporary closing restriction must release into a bounded recovery path.

A modal needs an accessible name, focus inside on open, contained keyboard navigation, meaningful dismissal, and focus restoration. On touch devices, a focusable heading can avoid raising the keyboard while still moving focus into the modal. Preserve focus behavior through animation and unmounting. Restrict closing only for a justified, bounded critical operation, and expose a recovery state if it stalls.

These requirements follow the [WAI-ARIA modal dialog pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/); implement them through the existing accessible primitive rather than rebuilding modal mechanics.

## Mutation reconciliation

A local patch belongs to the query snapshot it updates. Replace it when authoritative loader data changes; never let a response from a previous tenant or filter overwrite the current list.

Use a mutation response directly when it contains the full row and the client can maintain membership, order, totals, and pagination correctly. Otherwise invalidate the narrowest affected query. Creation, deletion, or a changed sort key often requires refreshed page boundaries; a bare append can break a cursor list.

Optimistic updates need a real benefit, a rollback/reconciliation path, and protection against overlapping writes. Avoid optimism for irreversible operations whose server outcome may be unknown.

## Preserve the framework path

In a SvelteKit action-based application, extend existing actions, `fail`, redirects, and progressive enhancement rather than importing a second SPA client architecture. Match installed `use:enhance` behavior, including reset and invalidation semantics, before adding custom callbacks.

In an API-based application, extend its typed resource client. Preserve safe return paths after reauthentication, typed field errors, cancellation, retry metadata, and support correlation. Components should not each reinterpret raw HTTP failures.

## Verification targets

Exercise the changed flow with keyboard submission, validation failure, duplicate activation, expired session, timeout, late responses, navigation during loading, and long content where applicable. Inspect focus and draft preservation through close/reopen. Verify only the applicable rendering mode and supported themes; type checking does not establish these runtime behaviors.
