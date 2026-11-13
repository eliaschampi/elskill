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

## Verification

Read package scripts and CI to select type, lint, build, generation, and integration checks. Use a confirmed disposable database with production-equivalent grants; the application's `DATABASE_URL` is not a test target by default. Test direct unauthorized action calls, malformed input, rollback, and the resulting page state through public interfaces.
