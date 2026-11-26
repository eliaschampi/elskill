# Svelte implementation patterns

For Svelte applications; respect the installed Svelte and SvelteKit versions and the existing transport strategy. These describe responsibilities, not APIs to copy blindly.

## Contents
- State and ownership
- Modern Svelte 5 surface
- SvelteKit 3
- Loading and navigation
- Draft and submission lifecycle
- Dialogs
- Mutation reconciliation
- Preserve the framework path
- Verification targets

## State and ownership

| Information | Usual owner |
| --- | --- |
| Shared route context, session | Existing layout loader or server context |
| Page data, query parameters | Route loader or established query layer |
| Current draft and submission state | Form instance keyed by resource and draft identity |
| Computed values | `$derived` (rune mode) |
| Browser subscription, external integration | Lifecycle hook or `$effect` with cleanup |
| API errors, authentication, request metadata | Existing transport client or framework actions |
| UI authorization hints | Server-provided capabilities |

`$props` for typed inputs and the project's snippets and events. Do not copy props into mutable state unless the component deliberately owns a draft; a prop update must not silently reset in-progress input. Reserve `$effect` for synchronization outside the reactive graph, never to keep a second copy of computable state. Dispose subscriptions, listeners, timers, and obsolete requests; keep browser-only APIs out of SSR.

## Modern Svelte 5 surface

Check the installed version first; use only what the project's version and config provide.

- `{@attach fn}` (5.29+) replaces actions for new code: it runs in an effect, is fully reactive (re-runs when state it reads changes), can return cleanup, and passes through components via prop spreading. `fromAction` adapts existing `use:` actions; type factories with `Attachment` from `svelte/attachments`.
- `<svelte:boundary>` with `pending`, `failed` snippets for async and error containment at a useful granularity, not around every component.
- `$state.raw` for large or immutable data that is replaced, not mutated; `$derived.by` for multi-statement derivations; `$bindable` only for deliberate two-way props.
- **Experimental, opt-in only:** `await` in components and `$derived` needs `compilerOptions.experimental.async: true` (5.36+, flag removed in Svelte 6; details may change in minors). SvelteKit remote functions (`query`, `form`, `command`, `prerender`, from 2.27) are experimental and opt-in (`experimental.remoteFunctions` plus `compilerOptions.experimental.async`). Use either only if the project already enables it; otherwise stay on loaders and actions.

## SvelteKit 3

Check the `@sveltejs/kit` major first; on 2.x keep the 2.x APIs. The points below follow the official 3.x migration guide and replace what older knowledge suggests. `npx sv migrate sveltekit-3` automates much of the move; upgrade to the latest 2.x first for targeted deprecation warnings. Server-side changes (CSRF, cookies, `handleError`) are in sveltekit-kysely.md.

- Floor: Node 22.17, TypeScript 6, Svelte 5.57.1, Vite 8.0.12, `@sveltejs/vite-plugin-svelte` 7.
- `svelte.config.js` is no longer read: pass project config to the `sveltekit({...})` plugin in `vite.config.js` (`kit.*` options become top level, beside `compilerOptions`).
- `$lib` is gone: declare `#lib` and `#lib/*` in `package.json` `imports` and import with explicit extensions (`#lib/foo.js`). Param matchers live in one `src/params.ts` built with `defineParams`.
- `$app/stores` is removed: use `$app/state` and read `page` without `$`. `$app/environment` is now `$app/env`; `$env/*` is deprecated for `$app/env/private` and `$app/env/public`; `base`, `assets`, and `resolveRoute` left `$app/paths` for `resolve(...)` and `asset(...)`, whose paths have no leading slash.
- Navigation: `refreshAll` replaces `invalidateAll`; `pushState` and `replaceState` give way to `goto(url, { shallow: true, state })`; `goto` rejects for URLs that match no route; a link to the current URL runs `refreshAll()`; `page.url` is read-only; `data-sveltekit-*` uses `false`, not `'off'`.
- Enhanced forms (`use:enhance`) see the status passed to `fail` instead of 200, and navigate when `action` targets another page. Remote-function forms need `{...form.fields.x.as('text')}`, not a hand-written `name`.

## Loading and navigation

- Load page data through the route or query owner; use the framework's fetch and context where SSR and authentication need them.
- Reuse the existing context invalidation key. Navigation should not reload stable context, but membership, tenant, and session changes must invalidate stale context.
- Request identity includes route, tenant, sort, filters, cursor. Abort obsolete requests when supported and discard responses whose identity is no longer current (abort alone does not stop every late completion).
- Reset cursor and accumulated results when filters or order change. Deduplicate stable IDs only as pagination reconciliation, never to hide a server query defect.
- No server state in process-global mutable stores during SSR.

## Draft and submission lifecycle

Use an existing form helper when it already owns these transitions; otherwise implement only the state the interaction needs.

```text
editing -> submitting -> committed -> closed, or editing a new intent
                      -> rejected  -> editing with values and errors
                      -> unknown   -> reconciliation or a safe retry
```

1. Initialize the draft for a stable resource and draft identity. Keep changes local until submit; never mutate loader data through shared references.
2. Submit a real form, guard duplicate activation, capture payload and idempotency key together when the backend supports them.
3. Reuse that pair on retry after a timeout. If the payload changes, resolve the uncertain prior outcome before starting a new irreversible intent.
4. Map server field locations through the existing form convention; keep operation errors in the form and focus an invalid control or summary.
5. Mark server success before follow-up refresh work. If invalidation fails after commit, say saving succeeded and refreshing failed; do not invite a second create.
6. Reset or dismiss only after the accepted transition; re-enable recovery after rejection or timeout; a busy flag must never stick.

Store eligible drafts only under the product's privacy rules, scoped by account, tenant, and resource, with cleanup. Never persist authentication secrets or sensitive payment input.

## Dialogs

Use the established wrapper and its real open and close callbacks. Keying a form by draft identity can intentionally create a fresh instance; keying by every reactive change destroys input and focus.

Route close button, Escape, backdrop, Cancel, and applicable back-navigation through one dismissal decision for dirty and submitting states. A temporary closing restriction must release into a bounded recovery path.

A modal needs an accessible name, focus inside on open, contained keyboard navigation, meaningful dismissal, and focus restoration, preserved through animation and unmounting. On touch, a focusable heading can avoid raising the keyboard while still moving focus into the modal. Implement through the existing accessible primitive, or the native `<dialog>` and Popover API, rather than rebuilding modal mechanics. [WAI-ARIA modal dialog](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)

## Mutation reconciliation

A local patch belongs to the query snapshot it updates; replace it when authoritative loader data changes, and never let a response from a previous tenant or filter overwrite the current list. Use a mutation response directly only when it holds the full row and the client can maintain membership, order, totals, and pagination; otherwise invalidate the narrowest affected query. Creation, deletion, or a changed sort key often needs refreshed page boundaries; a bare append can break a cursor list.

Optimistic updates need a real benefit, a rollback path, and protection against overlapping writes. Avoid them for irreversible operations whose server outcome may be unknown.

## Preserve the framework path

In a SvelteKit action-based app extend existing actions, `fail`, redirects, and progressive enhancement rather than importing a second SPA client architecture; match installed `use:enhance` behavior (reset, invalidation) before adding callbacks. In an API-based app extend the typed resource client, preserving safe return paths after reauthentication, typed field errors, cancellation, retry metadata, and support correlation. Components must not each reinterpret raw HTTP failures.

## Verification targets

Exercise the changed flow with keyboard submission, validation failure, duplicate activation, expired session, timeout, late responses, navigation during loading, and long content where applicable. Inspect focus and draft preservation through close and reopen. Verify only the applicable rendering mode and themes; type checking establishes none of these runtime behaviors.
