# Rust web architecture blueprint

Read when starting a web application or deciding a new boundary. Existing applications retain their accepted owners. This profile develops the original core-rs approach without requiring its names, versions, deployment, locale, or budgets.

## Start with decisions, not directories

| Decision | Default worth considering | Change it when |
| --- | --- | --- |
| Deployment unit | Modular monolith | Independent scale, ownership, or isolation has a concrete benefit |
| Domain | Pure types, calculations, and policies | An existing framework already owns these responsibilities coherently |
| Persistence | PostgreSQL with explicit migrations | Product or deployment requirements justify another store |
| Rust HTTP and SQL | axum and sqlx when appropriate | The project already uses a capable alternative |
| Frontend | Existing framework and design system | A new product needs a deliberate stack decision |
| Contract | One definition with generated or checked consumers | Existing contract tooling provides the same guarantee |
| Background work | Direct bounded work first | Durability, latency, or retry semantics require a worker |

Pin compatible toolchains and dependencies in repository manifests and lockfiles. Read actual versions before using APIs; this document is not a version catalog. Do not add infrastructure solely because it appears in this table.

A possible shape, only as responsibilities emerge:

```text
web                  presentation and interaction
  → HTTP contract
server               routes, auth, orchestration, SQL, integrations
  → domain           valid values, pure policy, exact arithmetic
  → PostgreSQL       storage invariants, transaction boundary
migrations           explicit schema evolution
```

A separate domain crate can enforce dependency direction; a small application may start with modules. Keep I/O out of pure rules. Use existing repositories or services where they own meaningful responsibilities; do not add wrappers just to reproduce the diagram.

## Follow one request

1. Bound incoming work, identify the route, parse input, and resolve authentication through established infrastructure.
2. Open the business transaction only after receiving the body. Establish verified tenant context when needed.
3. Stabilize the facts used by a sensitive decision; authorize through its policy.
4. Write the business result, required audit, and durable outgoing work atomically.
5. Commit before success; return the authoritative result or a typed failure.
6. Run external work outside the transaction with explicit retry and reconciliation semantics.

[Backend guidance](../../el-backend/SKILL.md) owns the detailed guarantees. Route identity or a typed extractor cannot by itself prove policy correctness; verify the actual construction path and bypasses.

## Couple each claim to evidence

| Claim | Useful proof |
| --- | --- |
| Domain stays independent | Cargo dependency graph and domain tests without database or runtime |
| Routes enforce access | Explicit route requirements plus HTTP tests for denied and cross-tenant calls |
| Concurrent writes preserve an invariant | Database enforcement and a synchronized conflicting-writer test |
| Client matches server | Contract generation/check plus a representative runtime serialization test |
| Schema supports deployment | Migration rehearsal against representative data and old/new application compatibility |
| Expensive work is bounded | Load test and resource measurements, including cancellation and shutdown |
| UI works for its users | Rendered task completion and recovery on representative device conditions |

Keep the mechanism concrete: private transaction constructors can restrict acquisition; an architecture lint can detect forbidden pool calls; an exhaustive enum match can reject an unmapped error code. Inspect actual visibility, generated code, and alternate entry points before claiming that a boundary cannot be bypassed.

Use existing CI and command owners. A numerical target needs a reason, workload, measuring command, and enforcement location. Measure current latency, query count, memory, or shipped bytes before setting a regression budget; do not copy another application's numbers.

## Grow at demonstrated seams

- Multi-tenant products need verified scope in data access, jobs, and caches. Stable URL context can support multiple tabs; never trust the URL as authorization.
- Public pages may need SSR or prerendering and a dedicated safe projection; they do not automatically need a second backend.
- Heavy computation may need a bounded worker or subprocess. Specify deadlines, credentials, cancellation limits, and ownership of results.
- External payments or delivery need durable state and reconciliation. Do not pretend a database transaction spans a remote provider.
- Compatibility transitions need staged rollout and an explicit retirement condition, not an indefinite second implementation.

Build the first real flow before expanding the module map. Each new module should hide a responsibility that current callers otherwise must manage.
