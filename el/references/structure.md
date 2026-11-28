# Project structure

Read for a new application, a new module/crate/package boundary, or documentation layout. An existing application keeps its accepted owners; nothing here mandates a rewrite. Layouts are decisions, not templates: build the first real flow before expanding the module map.

## Contents
- Decide first
- Layout principles
- Growth ladder
- Reference layout
- Mechanical guards
- Follow one request
- Claims and proof
- Grow at demonstrated seams
- Document ownership

## Decide first

For a new product, record a north star where product intent already lives (the spec, else the README): who the product serves, the job it does for them, and the observable signal of success. Choose the first working slice from that signal; name an exclusion only when it changes a decision. Change the north star only as a recorded decision (A22).

| Decision | Default worth considering | Change it when |
| --- | --- | --- |
| Deployment unit | Modular monolith | Independent scale, ownership, or isolation has a concrete benefit |
| Domain | Pure types, calculations, policies | A framework already owns these coherently |
| Persistence | PostgreSQL, explicit migrations | Product or deployment requirements justify another store |
| Rust HTTP + SQL | axum + sqlx | The project already uses a capable alternative |
| Frontend | Existing framework and design system | A new product needs a deliberate stack decision |
| Contract | One definition, generated or checked consumers | Existing tooling gives the same guarantee |
| Background work | Direct bounded work first | Durability, latency, or retry semantics need a worker |

Pin toolchains and dependencies in manifests and lockfiles; read actual versions before using APIs. This file is not a version catalog. Add no infrastructure merely because it appears here.

## Layout principles

1. **Package by feature, depend by layer.** Top-level folders name product capabilities (orders, billing, identity), not technical buckets. Inside a feature, dependencies point inward: transport, then use case, then domain. Storage and adapters depend on the domain, never the reverse.
2. **Every feature is a deep module.** A small public surface (module root or index) hides handlers, SQL, and mappers. Callers cannot import internals; enforce with visibility or a boundary lint.
3. **One composition root.** The single place that wires config, pools, clients, and routes. No globals or singletons reachable from domain code.
4. **Name by domain vocabulary.** No `utils`, `helpers`, `common`, `manager`, or generic `service` drawers. A shared file earns its name through one responsibility and at least two real consumers.
5. **Co-locate what changes together.** A feature's migration, query, handler, schema, and test sit together or are indexed together. Cross-cutting infrastructure (auth, tenancy, errors, telemetry, db) lives once, in shared infra.
6. **Verify shared contracts.** When a wire format crosses a language, repository, or deployment boundary, maintain its schema or check compatibility at that boundary. Edit generated artifacts through their source.
7. **Tests mirror behavior.** Unit tests for pure domain; integration tests at the HTTP and database boundary on the real engine; a few end-to-end journeys for the primary flows.
8. **Make the entry point discoverable.** Extend the existing project guide; a new project gets one that lists commands, boundaries, and the owner map. Each hard rule names the check that enforces it. Link deeper detail at its owner.
9. **One operation, many surfaces.** When a product has several surfaces (UI, API, CLI, jobs, agent tools such as MCP), each user-visible action is one typed operation with input and output schemas that every surface calls. A programmatic call never needs an interactive step; a parity test covers each surface. Add a surface only for a present consumer (A11).

## Growth ladder

Climb only on evidence; each rung needs the failure it removes.

| Rung | Shape | Climb when |
| --- | --- | --- |
| L0 | One crate or package, modules by feature | Start here |
| L1 | Extract a pure `domain` module/crate | I/O leaks into rules, or the compiler should enforce purity |
| L2 | Workspace: `domain`, `server`, `contract`, `xtask` | Several consumers of the contract; checks need real code |
| L3 | Separate deployable | Independent scale, ownership, isolation, or failure domain, with its own contract and data owner |

## Reference layout

Modular monolith, Rust API plus SvelteKit web. Start as folders; promote to crates when a boundary needs compiler enforcement. Adapt names to the stack and the domain.

```text
repo/
  CLAUDE.md               commands, boundaries, owner map (entry; links out)
  docs/{adr/, spec.md}    decisions and product intent; only what exists
  apps/web/               SvelteKit: src/routes (thin), src/lib/{features/<f>, ui, api, i18n}
  crates/domain/          pure types, policy, exact arithmetic; no I/O
  crates/server/          composition root
    src/features/<f>/     mod, routes, queries, jobs, tests
    src/platform/         auth, tenancy, errors, telemetry, db
  crates/contract/        wire schema, generated TS client (single source)
  db/migrations/          ordered, named constraints (B9)
  xtask/                  repo checks as code
```

```text
domain  <-  server features  <-  server platform  <-  composition root
(no arrow points from domain to anything)
```

## Mechanical guards

Add when the project outgrows convention; prefer the project's existing tools. One command surface (`just`, package scripts, or `cargo xtask`) so humans, agents, and CI run the same checks.

| Guard | Catches | Example tooling |
| --- | --- | --- |
| Dependency direction | Domain importing I/O; feature reaching into another's internals | `cargo tree`, `cargo-deny`, ESLint boundaries, dependency-cruiser |
| Contract drift | Client and server disagreeing | Regenerate then `git diff --exit-code` |
| Migration lint, query metadata | Locking DDL, stale `.sqlx` | squawk, `cargo sqlx prepare --check` |
| Static analysis | Type and lint regressions | `cargo clippy -D warnings`, `tsc --noEmit`, `svelte-check` |
| Secret scan | Credentials in history | gitleaks or the host's scanner |
| Budget | Bundle, query count, latency regressions | A script tied to a measured baseline |
| Design tokens | Literal colors, spacing, radius, or type sizes in product styles | A stylelint rule or CI grep that allows them only in the token owner |
| Ratchet | A migration's exception list growing back | A checked list that may only shrink |

Fast checks in a pre-commit hook; the rest in CI. A guard must reject a violation, accept a control, and fail on checker errors (A14).

## Follow one request

1. Bound incoming work, identify the route, parse input, resolve authentication through established infrastructure.
2. Open the business transaction only after receiving the body; establish verified tenant context when needed.
3. Stabilize the facts a sensitive decision uses; authorize through its policy.
4. Write the result, required audit, and durable outgoing work atomically.
5. Commit before reporting success; return the authoritative result or a typed failure.
6. Run external work outside the transaction with explicit retry and reconciliation semantics.

backend.md owns the detailed guarantees. Route identity or a typed extractor alone does not prove policy correctness; verify the construction path and bypasses.

## Claims and proof

| Claim | Useful proof |
| --- | --- |
| Domain stays independent | Dependency graph; domain tests without database or runtime |
| Routes enforce access | Explicit route requirements; HTTP tests for denied and cross-tenant calls |
| Concurrent writes keep an invariant | Database enforcement; a synchronized conflicting-writer test |
| Client matches server | Contract generation or check; a runtime serialization test |
| Schema supports deployment | Migration rehearsal on representative data; old and new app compatibility |
| Expensive work is bounded | Load test and resource measurements, including cancellation and shutdown |
| UI works for its users | Rendered task completion and recovery under representative device conditions |

Measure current latency, query count, memory, or shipped bytes before setting a budget; never copy another application's numbers.

## Grow at demonstrated seams

- Multi-tenant products need verified scope in data access, jobs, and caches. A URL can carry context; it never authorizes.
- Public pages may need SSR or prerendering and a dedicated safe projection, not a second backend.
- Heavy computation: bounded worker or subprocess with deadlines, credentials, cancellation limits, and result ownership.
- Payments and delivery need durable state and reconciliation; a database transaction does not span a remote provider.
- Compatibility transitions need staged rollout and a retirement condition, not an indefinite second implementation.

## Document ownership

Reuse equivalent files; create only what the task needs. The goal is discoverable decisions, not a mandatory document set.

| Information | Common owner | Keep out |
| --- | --- | --- |
| Agent workflow, commands, boundaries | CLAUDE.md or AGENTS.md | Duplicated product rules |
| Product intent (north star), invariants, architecture | Existing spec or ADRs, else the README | Progress claims |
| Wire behavior, compatibility | API schema or contract docs | A separately maintained type system |
| Verified status | Existing status record | Predictions presented as facts |
| Active outcome, remaining work | Existing tracker or plan | Permanent rules copied from the spec |

Record shapes: **Decision** (context, choice, reason, rejected alternative, revisit condition). **Constraint** (invariant or metric, enforcement command, scope, stage, reason; exceptions carry scope, rationale, owner, expiry). **Task** (observable outcome, slices, status, open decisions; a backlog is not permission). **Evidence** (revision, command or artifact, result, limits; mark unavailable checks, drop stale success). **Handoff** (scope, changed paths, decisions, checks, next step).

Link to the authoritative rule instead of restating it. Update contract, consumers, and docs together. Remove superseded instructions but keep valid constraints and their reasons. If several agent tools need entry files, point them at one owner by mechanisms they support; never keep divergent copies.
