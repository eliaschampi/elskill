# SvelteKit and Kysely

Read when the existing server uses this stack. Inspect route siblings, hooks, `locals`, authorization, parsers, repositories, and package versions. Preserve accepted boundaries; do not transplant a Rust service layout into a working monolith.

## Request ownership

A route coordinates HTTP, authentication, parsing, and the framework response. An existing repository owns SQL and aggregate mapping. An application service earns its place through orchestration, atomicity, or a shared rule; simple validated writes do not need a pass-through service.

- Authorize every sensitive `load`, action, and endpoint. A parent layout check or client capability does not secure a direct action request.
- Reuse the project's request parser and domain vocabulary. Bound form data and query parameters; preserve original drafts when returning validation errors.
- Put dependent writes in a Kysely transaction and pass its executor to all participating operations. Using the root database object inside the callback escapes that transaction.
- Revalidate mutable authorization facts inside the protected mutation boundary when concurrent changes matter.
- Inspect affected rows according to the operation contract. Map expected SQLSTATE and constraint names; unexpected errors remain internal.
- Keep credentials, database handles, and private projections out of returned page data. Use server-only modules and the framework's established serialization boundary.

## Data and UI integration

Use the existing migration and database-type generation commands; never edit generated types. Follow the [PostgreSQL reference](postgres.md) for concurrency, RLS, and migrations. Bulk related writes, scope by tenant and operational location, and paginate growing results.

Prefer the established form-action and progressive-enhancement path. Return field/form errors through the project's `fail` convention and preserve redirect/error control flow; a broad catch must not swallow framework redirects. Invalidate the data owner whose result changed using established dependency keys. Do not create a second HTTP client or local cache to imitate a separate API architecture. SvelteKit remote functions are experimental; use them only where the project has already opted in.

Request-scoped user data must not live in shared server module state. Test two users or tenants in the same process and stale client responses during navigation when these paths change.

## SvelteKit 3

On `@sveltejs/kit` 3.x (version floor, config location, and `#lib` are in the [Svelte patterns](../../el-design/references/svelte-patterns.md); on 2.x keep the 2.x behavior):

- CSRF is always on: `csrf.checkOrigin` is removed, so allow cross-origin hosts with `csrf.trustedOrigins` and set `paths.origin` behind a reverse proxy. Cross-origin mutative requests without a `Content-Type` are rejected.
- `handleError` receives every error, including expected `error()` ones, may return `status`, and gets remote-function validation errors as `kind: 'validation'` (`handleValidationError` is gone). `error(status, message, extra)` takes a string message; extra `App.Error` fields go third.
- Cookies: `path` defaults to `'/'` instead of the request path; names must be ASCII.
- Server-only means any `server` filename segment or directory outside `src/routes` and `static`, not only `src/lib/server`.
- `redirect()` to an external URL needs `{ external: true }` or an origin list; a 204 response has no body; `json()` and `text()` are deprecated for `Response.json()` and `new Response()`.
- Remote functions stay experimental. Inside a `query`, `event.url`, `event.params`, and `event.route` throw: pass values as arguments.
- First-party adapters require Kit 3: Vercel drops the edge runtime, and Cloudflare APIs come from `cloudflare:workers`, not `platform`.

## Verification

Read package scripts and CI to select type, lint, build, generation, and integration checks. Use a confirmed disposable database with production-equivalent grants; the application's `DATABASE_URL` is not a test target by default. Test direct unauthorized action calls, malformed input, rollback, and the resulting page state through public interfaces.
