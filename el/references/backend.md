# Backend rules (B1-B47)

Server correctness. Project contracts decide names, versions, conventions, and approved infrastructure. Apply the groups the change touches, not all of them.

## Contents
- Which rules apply
- Before a mutation
- Data integrity (B1-B10)
- Atomicity and concurrency (B11-B17)
- Authorization and contracts (B18-B27)
- External effects and workers (B28-B32)
- Security and resources (B33-B44)
- Verification (B45-B47)

## Which rules apply

| Change | Rules |
| --- | --- |
| Tenant- or user-scoped request | B5, B18-B22 |
| Read endpoint or query | B23-B27, B40-B42 |
| Write | B4, B6-B8, B11-B17, plus the read rules |
| Schema, constraint, migration | B1-B10 (and postgres.md) |
| Worker, queue, external call | B13, B28-B32, B44 |
| Authentication, sessions, secrets, public surface | B33-B39 (and security.md) |
| Caching or optimization | B40-B44 |
| Any behavior change | B45-B47, scaled to risk |

## Before a mutation

Name its **invariant, atomic boundary, competing writers, retry semantics, and observable failure.** Usual path: bounded input, transaction/context, stable decision facts, authorization, write + audit + outbox, commit, response. Success requires a successful commit.

## Data integrity

- **B1. Schema authority.** Use the existing migration owner. In SQL-first projects write SQL and generate or verify application types against it; no competing schema definition.
- **B2. Opaque identity.** Follow existing key conventions and database-supported generation. Distinguish instants, local dates, and business time zones. IDs never encode mutable business meaning.
- **B3. Explicit relationships.** Foreign keys and join tables for relational integrity. JSON suits document-shaped data, not relational ownership or constraints.
- **B4. Named invariants.** Uniqueness, references, and row predicates live in the database. Cross-row rules need a concurrency strategy. Prechecks cannot replace enforcement under races; map known constraint names to domain errors.
- **B5. Tenant scope.** Resolve membership on the server. Scope queries, composite foreign keys, caches, jobs, and idempotency keys. With RLS, verify the actual runtime role, missing context, cross-tenant access, and pooled-connection reuse.
- **B6. Business history.** Mutable entities have meaningful lifecycle states. Correct posted financial, inventory, and audit facts with traceable compensating records, never silent rewrites.
- **B7. Derived state.** Derive balances and aggregate status from authoritative facts. A stored projection needs a demonstrated purpose, an update owner, and a reconciliation path. Reports aggregate in the query and ship typed figures and state keys, not prose a consumer must parse (read-models.md).
- **B8. Exact arithmetic.** Specify units, currency, scale, rounding mode and boundary, overflow behavior. Use decimal or checked scaled integers and lossless wire values. If the domain defines totals as the sum of rounded lines, round each line once and sum those exact values; no header-level substitute. Historical charged amounts are facts, not values to recompute from current prices.
- **B9. Compatible migrations.** Never edit a migration that has run on a database whose data must be kept (production, staging, shared or teammate data); runners skip or reject changed history, so schemas drift. Treat a migration that is in a release or deployment, or whose status you cannot establish, as run. Before that, revise it in place and recreate the disposable databases that ran it, after confirming their target (B47). Assess locks, volume, backfill, mixed application versions, recovery. Regenerate schema-dependent artifacts together; readiness checks enforce supported compatibility, not exact schema equality.
- **B10. Narrow triggers.** Triggers may protect storage invariants or atomic reservations. Cover every mutation path, including referenced-table changes. Never hide authorization or external workflows in triggers.

## Atomicity and concurrency

- **B11. One transaction per atomic unit.** Dependent writes, audit, and durable job creation commit together. Reads need a transaction when context or snapshot semantics require it. Commit explicitly, handle commit errors, never hold a transaction for streaming.
- **B12. Stable decision facts.** Choose conditional writes, locks, version checks, or serializable isolation; specify the isolation level and every competing writer. At READ COMMITTED, lock shared guard rows before a fresh statement reads dependent facts; a joined locking query is not automatically a fresh authorization snapshot.
- **B13. No external waits inside transactions.** Bound and parse request bodies before business transactions. Finish the transaction before external I/O, then re-enter and revalidate changed facts. A timeout can mean an unknown outcome, not a failed effect.
- **B14. Bounded contention.** Lock in stable order; configure acquisition, statement, lock, and transaction deadlines. After serialization or deadlock failure retry the whole retry-safe transaction, with bounded attempts. Distinguish domain conflict, overload, and infrastructure failure.
- **B15. Deliberate numbering.** Sequences permit gaps. A number that must roll back with its document needs a scoped transactional counter; assess its contention and the real business requirement.
- **B16. Complete idempotency.** Scope keys to tenant and operation; bind them to normalized request content. Same key and intent replays the committed result after authorization; changed content conflicts. Serialize duplicate attempts, retain outcomes for the retry window. A unique violation alone is not replay behavior.
- **B17. Meaningful row counts.** Prefer `RETURNING`. Zero affected rows can mean not found, hidden, stale version, or already done; follow the operation's contract instead of always answering success or 404.

## Authorization and contracts

- **B18. Protected entry points.** Classify every route as public, authenticated, or privileged. Direct API calls and workers get the same protection as browser flows.
- **B19. One policy per decision.** Load authoritative facts and evaluate the whole operation. Recheck inside the mutation boundary when concurrent revocation matters; never scatter policy fragments across handlers.
- **B20. Capabilities and scope.** Respect the existing permission catalog and implications. No scattered role-name checks, privilege escalation, or unauthorized delegation.
- **B21. Authoritative UI capabilities.** Derive `can_*` from the server policy. They describe presentation, not credentials, and do not guarantee a later write succeeds.
- **B22. Controlled disclosure.** Scope lookups before returning details. Use one consistent not-found/forbidden policy so cross-tenant requests cannot probe resource existence.
- **B23. Valid input types.** Bound sizes, ranges, nesting, and collection counts at ingress. Specify unknown-field behavior per contract. Deserialization and storage-to-domain conversion use the validating constructor; database-dependent validity stays transactional.
- **B24. Stable, safe errors.** One documented shape; a typed internal catalog with exhaustive HTTP/presentation mappings; field locations where relevant; a support correlation id. Independently versioned clients need a safe unknown-code fallback. Product requirements set message language; internal causes go to redacted diagnostics.
- **B25. Structural error mapping.** Inspect SQLSTATE and known constraint names, never message text. Unknown failures stay internal; never expose schema or query details.
- **B26. One wire contract.** Generate consumers or verify compatibility mechanically. Check nullability, enum evolution, limits, pagination, public projections. Change definitions, generated consumers, and docs together.
- **B27. Lossless representation.** Instants with offsets, local dates as dates, exact amounts losslessly, external identifiers as strings. Generated types alone do not prove runtime serialization matches.

## External effects and workers

- **B28. Durable delivery.** Enqueue required work atomically with the business fact. Claim briefly, do I/O outside the transaction, and fence every completion write with the current lease token and validity check. Design for duplicate delivery.
- **B29. Unknown outcomes.** Use provider idempotency or status lookup before retrying an irreversible send. A database lease cannot undo an external effect. Route unresolved outcomes to the product's operational recovery path.
- **B30. Immutable artifacts.** Persist signed or issued bytes and their identity once; retries transport that artifact. Regeneration is a new domain operation when its meaning changes.
- **B31. Bounded integrations.** Define connect and response deadlines, retryable errors, attempt limits, backoff with jitter; honor rate-limit guidance; never blindly retry a non-idempotent effect.
- **B32. Bounded expensive work.** Limit CPU, memory, queue depth, concurrency. Use a job or supervised process when the request budget cannot contain the work; no queue for trivial computation.

## Security and resources

- **B33. Secret boundaries.** Keep secrets out of ordinary serialization and debug output. Hash passwords; protect retrievable credentials with an established vault or authenticated encryption and managed keys. Bind ciphertext to tenant, record, and purpose when substitution is a threat. Do not claim memory erasure the runtime cannot guarantee.
- **B34. Password verification.** Maintained hashing implementation with current project parameters, outside the async executor, with memory-aware concurrency limits. Prevent account enumeration through responses and practical timing.
- **B35. Session ownership.** Extend the existing authentication system. Protect cookies, expiry, rotation, revocation. Opaque sessions store token digests, not bearer tokens. Do not replace authentication during unrelated work.
- **B36. Trust boundaries.** Parameterize SQL; allowlist dynamic identifiers. Cookie-authenticated mutations need CSRF protection (CORS is not enough). Validate redirects, uploads, outbound destinations, and proxy-derived client info at the boundary.
- **B37. Abuse limits.** Reserve limits before expensive work. Bound attacker-controlled keys; separate trusted identity from spoofable headers. Return the documented retry behavior.
- **B38. Public projections.** Select public fields explicitly; never serialize administrative models by default. Scope public links by purpose, expiry, and consumption.
- **B39. Explicit runtime failures.** No panics on request data, no blocking calls in async tasks. Prefer safe Rust; exceptional `unsafe` or suppressions need project justification. Validate required configuration at startup.
- **B40. Real database cost.** No per-row queries, repeated permission loads, or unbounded detail hydration. Measure query count, latency, and pool wait on representative paths.
- **B41. Bounded collections.** Prefer keyset pagination for large changing lists, with deterministic order and a unique tie-breaker. Bind cursors to filter and sort semantics; enforce server-side limits.
- **B42. Evidence-based indexes.** Inspect representative plans and cardinality. Indexes cost writes and storage; partial indexes suit selective active or pending subsets.
- **B43. Measured optimization.** Profile before caching or parallelizing. Caches need tenant-aware keys, bounds, invalidation, and staleness semantics; cached permissions need revocation semantics.
- **B44. Resource lifetimes.** Bound pools, bodies, fan-out, task spawning, queues. Propagate cancellation where safe and drain on shutdown. Observe latency, errors, saturation, and job age without secret or unbounded metric labels.

## Verification

- **B45. Important failure tests.** Pure tests for arithmetic and policy matrices. HTTP and database integration for contracts, rollback, isolation, idempotency, and races, on the production engine with runtime privileges. Synchronize competing operations; launching two futures alone does not prove a race occurred.
- **B46. Independent assertions.** Derive expected values from the contract, an independent calculation, reference data, or a reviewed example, never from the output of the code under test or a copy of its logic. Test observable behavior and durable invariants, not private call order, and keep those tests across refactors. Test serialization when representation is the risk.
- **B47. Isolated effects.** Disposable databases with confirmed targets and fake external services. Never run destructive setup against development or production data, or contact live payment or delivery providers from CI.

Finish with repository checks and evidence for the changed invariant, including commit-time failure and retry behavior when relevant; compilation cannot demonstrate isolation or atomicity.
