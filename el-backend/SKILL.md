---
name: el-backend
description: Implement and review reliable web backends, especially Rust with axum, sqlx, and PostgreSQL. Use for APIs, domain logic, authorization, schemas, migrations, transactions, concurrency, workers, and external integrations. Includes adaptations for existing SvelteKit/Kysely and Laravel/PHP applications.
license: MIT
---

# EL Backend

This skill owns server correctness. Project contracts determine names, versions, conventions, and approved infrastructure. A local change needs only this file; read [EL Architecture](../el-architecture/SKILL.md) for its risk classes and for cross-layer, structural, or critical work.

Apply the rule groups the change touches, not all of them:

| Change | Rules |
| --- | --- |
| Any tenant- or user-scoped request | B5, B18–B22 |
| Read endpoint or query | B23–B27, B40–B42 |
| Write | B4, B6–B8, B11–B17, and the read rules |
| Schema, constraint, or migration | B1–B10 |
| Worker, queue, or external call | B13, B28–B32, B44 |
| Authentication, sessions, secrets, public surfaces | B33–B39 |
| Caching or optimization | B40–B44 |
| Any behavior change | B45–B47, scaled to its risk |

| Task | Reference |
| --- | --- |
| Rust HTTP, types, async, SQLx | [Rust implementation](references/rust-axum-sqlx.md) |
| Schema, isolation, concurrency, jobs | [PostgreSQL](references/postgres.md) |
| New or changed authentication, sessions, CSRF, or secret storage | [Web security](references/web-security.md) |
| Existing SvelteKit server | [SvelteKit and Kysely](references/sveltekit-kysely.md) |
| Existing Laravel or PHP server | [Laravel and PHP](references/laravel-php.md) |

Read only the relevant references. Before a mutation, identify its **invariant, atomic boundary, competing writers, retry semantics, and observable failure**. The usual path is bounded input → transaction/context → stable decision facts → authorization → write/audit/outbox → commit → response. Success requires a successful commit.

## Data integrity

- **B1. Schema authority.** Use the existing migration owner. In SQL-first projects, write SQL and generate or verify application types against it; do not introduce a competing schema definition.
- **B2. Opaque identity.** Follow existing key conventions and database-supported generation. Distinguish instants, local dates, and business time zones. IDs must not encode mutable business meaning.
- **B3. Explicit relationships.** Use foreign keys and join tables for relational integrity. JSON suits document-shaped data; it does not replace relational ownership or constraints.
- **B4. Named invariants.** Enforce uniqueness, references, and row predicates in the database. Cross-row rules need a concurrency strategy. Friendly prechecks cannot replace enforcement under races; map known constraint names to domain errors.
- **B5. Tenant scope.** Resolve membership on the server. Scope queries, composite foreign keys, caches, jobs, and idempotency keys. With RLS, verify the actual runtime role, missing context, cross-tenant access, and pooled-connection reuse.
- **B6. Business history.** Mutable entities have meaningful lifecycle states. Correct posted financial, inventory, and audit facts through traceable compensating records; do not silently rewrite them.
- **B7. Derived state.** Derive balances and aggregate status from authoritative facts. A stored projection needs a demonstrated purpose, an update owner, and a reconciliation path.
- **B8. Exact arithmetic.** Specify units, currency, scale, rounding mode and boundary, and overflow behavior. Use decimal or checked scaled-integer arithmetic and lossless wire values. When the domain defines totals as the sum of rounded lines, round each line once and sum those exact values; do not silently substitute header-level rounding. Historical charged amounts may be facts, not values to recalculate from current prices.
- **B9. Compatible migrations.** Never edit an applied migration. Assess locks, volume, backfill, mixed application versions, and recovery. Regenerate schema-dependent artifacts together; readiness checks enforce supported compatibility rather than assuming exact schema equality.
- **B10. Narrow triggers.** Triggers may protect storage invariants or atomic reservations. Cover every mutation path, including referenced-table changes. Do not hide authorization or external workflows in triggers.

## Atomicity and concurrency

- **B11. One transaction per atomic unit.** Keep dependent writes, audit, and durable job creation together. Reads need transactions when context or snapshot semantics require them. Commit explicitly, handle commit errors, and avoid retaining transactions for streaming.
- **B12. Stable decision facts.** Choose conditional writes, locks, version checks, or serializable isolation. Specify the isolation level and all competing writers. At READ COMMITTED, lock shared guard rows before a fresh statement reads dependent facts; a joined locking query is not automatically a fresh authorization snapshot.
- **B13. No external waits inside transactions.** Bound and parse request bodies before business transactions. Finish the transaction before external I/O, then re-enter and revalidate changed facts. A timeout can mean an unknown outcome rather than a failed effect.
- **B14. Bounded contention.** Lock in stable order and configure acquisition, statement, lock, and transaction deadlines. Retry the entire retry-safe transaction after serialization or deadlock failures, with bounded attempts. Distinguish domain conflicts, overload, and infrastructure failures.
- **B15. Deliberate numbering.** Database sequences permit gaps. A number that must roll back with its document needs a scoped transactional counter; assess its contention and the actual business requirement.
- **B16. Complete idempotency.** Scope keys to tenant and operation; bind them to normalized request content. Same key and intent replays the committed result after authorization; changed content conflicts. Serialize duplicate attempts and retain outcomes for the retry window. A unique violation alone is not replay behavior.
- **B17. Meaningful row counts.** Prefer `RETURNING` where useful. Zero affected rows can mean not found, denied visibility, stale version, or already completed; follow the operation's contract instead of always returning success or 404.

## Authorization and contracts

- **B18. Protected entry points.** Explicitly classify public, authenticated, and privileged routes. Direct API calls and workers require the same protection as browser flows.
- **B19. One policy per decision.** Load authoritative facts and evaluate the complete operation. Recheck within the mutation boundary when concurrent revocation matters; do not distribute fragments of a policy among handlers.
- **B20. Capabilities and scope.** Respect the existing permission catalog and implications. Avoid scattered role-name checks, privilege escalation, and unauthorized delegation.
- **B21. Authoritative UI capabilities.** Derive `can_*` from the server policy. They describe presentation, not credentials or a guarantee that a later write will succeed.
- **B22. Controlled disclosure.** Scope lookups before returning details. Follow a consistent not-found/forbidden policy so cross-tenant requests do not reveal protected resource existence.
- **B23. Valid input types.** Bound sizes, ranges, nesting, and collection counts at ingress. Specify unknown-field behavior per contract. Deserialization and storage-to-domain conversion must use the validating constructor rather than bypass it. Database-dependent validity remains transactional.
- **B24. Stable, safe errors.** Use one documented shape with a typed internal error catalog, exhaustive HTTP/presentation mappings, field locations where relevant, and support correlation. Independently versioned clients need a safe unknown-code fallback. Product requirements determine message language; internal causes belong in redacted diagnostics.
- **B25. Structural error mapping.** Inspect SQLSTATE and known constraint names, never database message text. Unknown failures remain internal errors; do not expose schema or query details.
- **B26. One wire contract.** Generate consumers or verify compatibility mechanically. Check nullability, enum evolution, limits, pagination, and public projections. Change definitions, generated consumers, and affected documentation together.
- **B27. Lossless representation.** Encode instants with offsets, local dates as dates, exact amounts losslessly, and external identifiers as strings. Generated types alone do not prove runtime serialization matches them.

## External effects and workers

- **B28. Durable delivery.** Enqueue required work atomically with the business fact. Claim briefly, perform I/O outside the transaction, and fence every completion write with the current lease token and validity check. Design for duplicate delivery.
- **B29. Unknown outcomes.** Use provider idempotency or status lookup before retrying an irreversible send. A database lease cannot undo an external effect. Route unresolved outcomes to the product's operational recovery path.
- **B30. Immutable artifacts.** Persist signed or issued bytes and their identity once; retries transport that artifact. Regeneration is a new domain operation when its meaning changes.
- **B31. Bounded integrations.** Define connect/response deadlines, retryable errors, attempt limits, and backoff with jitter. Honor applicable rate-limit guidance; never blindly retry a non-idempotent effect.
- **B32. Bounded expensive work.** Limit CPU, memory, queue depth, and concurrency. Use a job or supervised process when the request budget cannot contain the work; avoid a queue for trivial computation.

## Security and resources

- **B33. Secret boundaries.** Exclude secrets from ordinary serialization and debug output. Hash passwords; protect retrievable credentials with an established vault or authenticated encryption and managed keys. Bind ciphertext to its tenant, record, and purpose when substitution is a threat. Do not claim memory erasure the runtime cannot guarantee.
- **B34. Password verification.** Use maintained hashing implementations and current project security parameters, outside the async executor with memory-aware concurrency limits. Avoid account enumeration through responses and practical timing differences.
- **B35. Session ownership.** Extend the existing authentication system. Protect cookies, expiration, rotation, and revocation. For opaque sessions, store token digests instead of bearer tokens; do not replace authentication during unrelated work.
- **B36. Trust boundaries.** Parameterize SQL and allowlist dynamic identifiers. Cookie-authenticated mutations need CSRF protection; CORS alone is insufficient. Validate redirects, uploads, outbound destinations, and proxy-derived client information at their boundary.
- **B37. Abuse limits.** Reserve limits before expensive work. Bound attacker-controlled keys and distinguish trusted identity from spoofable headers. Return the documented retry behavior.
- **B38. Public projections.** Select public fields explicitly; never serialize administrative models by default. Scope public links to purpose, expiry, and consumption semantics.
- **B39. Explicit runtime failures.** Avoid panics on request data and blocking calls in async tasks. Prefer safe Rust; exceptional unsafe code or suppressions require project justification. Validate required configuration at startup.
- **B40. Real database cost.** Avoid per-row queries, repeated permission loads, and unbounded detail hydration. Measure query count, latency, and pool wait on representative paths.
- **B41. Bounded collections.** Prefer keyset pagination for large changing lists, with deterministic order and a unique tie-breaker. Bind cursors to filter/sort semantics and enforce server-side limits.
- **B42. Evidence-based indexes.** Inspect representative plans and cardinality. Indexes cost writes and storage; partial indexes suit selective active or pending subsets.
- **B43. Measured optimization.** Profile before caching or parallelizing. Caches need tenant-aware keys, bounds, invalidation, and staleness semantics; cached permissions also need revocation semantics.
- **B44. Resource lifetimes.** Bound pools, bodies, fan-out, task spawning, and queues. Propagate cancellation where safe and drain on shutdown. Observe latency, errors, saturation, and job age without secret or unbounded metric labels.

## Verification

- **B45. Important failure tests.** Pure tests cover arithmetic and policy matrices. HTTP/database integration covers contracts, rollback, isolation, idempotency, and races using the production database engine and runtime privileges. Synchronize competing operations when needed; launching two futures alone does not prove a race occurred.
- **B46. Independent assertions.** Test observable behavior and durable invariants, not private call order, getters, or a copy of the implementation. Preserve behavioral tests across refactors; test serialization when representation itself is the risk.
- **B47. Isolated effects.** Use disposable databases with confirmed targets and fake external services. Never run destructive setup against development or production data, or contact live payment or delivery providers from CI.

Finish with repository checks and evidence for the changed invariant. Include commit-time failure and retry behavior when relevant; compilation cannot demonstrate isolation or atomicity.
