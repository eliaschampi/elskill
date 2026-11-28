# PostgreSQL integrity and concurrency

For schema, SQL, tenancy, migrations, durable jobs. Keep the project's naming and migration conventions. Verify version-specific features against the deployed database; never import another project's role names, identifiers, page sizes, or deadlines.

## Contents
- Choose the enforcing mechanism
- Modern features (verify version)
- Tenant isolation
- Locking and isolation
- Idempotency and counters
- Durable jobs and external outcomes
- Query shape and pagination
- Migration and release

## Choose the enforcing mechanism

| Invariant | Preferred mechanism | Limit |
| --- | --- | --- |
| Required field, row predicate | `NOT NULL`, named `CHECK` | A check is not a cross-row query |
| Relationship, tenant ownership | Foreign key, often composite | Referenced keys need suitable uniqueness |
| Unique active record | Unique constraint or partial unique index | Application prechecks stay racy |
| Conditional state change | Predicate in `UPDATE`, inspect `RETURNING` | Zero rows needs a defined contract |
| Aggregate or cross-row condition | Shared guard lock or serializable transaction | Every conflicting writer must participate |
| Multi-row rule valid only at commit | Deferred constraint trigger plus concurrency strategy | Deferral alone does not stop write skew |

Put the rule and its concurrency rationale beside the schema owner. Map SQLSTATE and constraint names, never error text.

## Modern features (verify version)

Available from PostgreSQL 18 (check `SHOW server_version` and the managed provider's support before relying on them; do not assume PG 19 features):

- `uuidv7()`: time-ordered UUIDs, better index locality than random v4 for primary keys. Still opaque identity (B2).
- `RETURNING OLD.*, NEW.*` on `INSERT`/`UPDATE`/`DELETE`/`MERGE`: audit rows and optimistic checks without a second read.
- `WITHOUT OVERLAPS` / `PERIOD` temporal constraints: non-overlapping validity ranges in the database instead of application locks.
- Virtual generated columns (now the default kind): derived values computed at read time (B7); stored when it must be indexed.
- Skip scan on multicolumn B-tree indexes can reduce the need for an extra index when the leading column has few distinct values; confirm with `EXPLAIN`.

## Tenant isolation

For RLS products use tenant predicates and composite foreign keys alongside policies. `USING` governs visible rows, `WITH CHECK` governs new values. Enable RLS and `FORCE ROW LEVEL SECURITY` when the owner must be subject to it.

The runtime role must not own tables, be a superuser, hold `BYPASSRLS`, or inherit an escape path. `FORCE` does not constrain superusers or `BYPASSRLS`. `SET ROLE` from a privileged connection is not enough if application SQL can reset it. Prefer direct runtime credentials with minimal grants. [Row security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)

Set tenant context transaction-locally with parameterized `set_config(..., true)` or an equivalent. Test missing context, wrong context, cross-tenant references, updates that change tenancy, and connection reuse after commit and rollback. RLS isolates queries; it does not protect against application code that can select any tenant context.

Views, functions, background jobs, and reporting paths need explicit privilege analysis; use invoker-security views where appropriate, never assume a view preserves caller isolation. Restrict grants on immutable facts to the intended operations and mutable columns.

## Locking and isolation

Write down the invariant, the rows or predicate, the isolation level, and every competing operation before choosing a lock.

- Prefer an atomic conditional write for a simple transition; it removes the read-decide race.
- At READ COMMITTED each statement has its own snapshot. Lock a stable shared guard row first, then read dependent facts in a later statement so a completed wait is followed by fresh committed facts.
- A row lock does not lock a predicate or joined rows. Protect changes to memberships, roles, grants, and scope if authorization depends on them.
- At REPEATABLE READ a later statement does not refresh the snapshot; do not apply a READ COMMITTED recipe there.
- Serializable may reject a transaction: retry the entire decision-and-write sequence, only when replay is safe.
- Lock in a consistent order with bounded waits. A deadlock or timeout is not evidence that no earlier external effect happened.

For "at least one owner remains": lock the shared tenant or guard row before relevant mutations so writers share a serialization point. A deferred trigger can validate final state but must cover role changes, membership changes, deletion, and transfers. An advisory lock helps only if every path takes the same scoped lock with correct snapshot semantics. Test the losing transaction and the final durable state. [Isolation](https://www.postgresql.org/docs/current/transaction-iso.html)

## Idempotency and counters

An idempotency record owns operation scope, key, normalized request identity, and durable result. Compare semantic content or a stable fingerprint; raw JSON byte order is not identity.

1. Authorize the operation and tenant.
2. Serialize attempts via the aggregate lock, a scoped reservation, or another proven mechanism.
3. If a committed record exists, compare intent and replay its documented result; different intent conflicts.
4. Otherwise apply the effect and store the result atomically.
5. If uniqueness races, recover in a fresh transaction or savepoint before reading the winner (a failed transaction accepts no ordinary queries).

Define pending attempts, crash recovery, retention, and ambiguous-response behavior. Replays still need current access checks. Test retries after a lost response.

Business numbering: `UPDATE ... SET last_number = last_number + 1 ... RETURNING` inside the document transaction gives rollback-aware allocation; plain sequences are cheaper and allow gaps. Choose by requirement and measured contention.

## Durable jobs and external outcomes

Enqueue in the transaction that establishes the business fact. Claim a bounded batch in a short transaction (`FOR UPDATE SKIP LOCKED`), set a fresh lease token and expiry, commit before I/O.

Every renewal, completion, and business-result write verifies the current token and an unexpired lease using database time. After expiry the worker must reclaim through the protocol; updating a timestamp cannot resurrect ownership. A stale worker writes nothing.

Fencing protects database updates, not a provider already contacted. Use provider idempotency keys, immutable outbound artifacts, and reconciliation. Delivery is at least once; never claim exactly once across unrelated systems. Bound attempts, backoff, and job age; keep an operational recovery path.

A privileged cross-tenant claim function exposes only the intended operation: dedicated trusted schema, fixed safe `search_path`, qualified references, owner and schema unwritable by untrusted roles, default `PUBLIC` execute revoked and the intended grant made in the creating transaction, no dynamic SQL, minimal returned data. [Security-definer functions](https://www.postgresql.org/docs/current/sql-createfunction.html)

## Query shape and pagination

Filter and page parent rows before hydrating details; use batches, joins, or bounded aggregates, not per-row round trips. Inspect representative plans. `EXPLAIN ANALYZE` executes the statement; use a safe environment for writes or expensive queries.

Keyset pagination needs a deterministic order and a unique tie-breaker. For descending order match cursor comparisons to direction; specify null handling and collation. Bind the cursor to filter and sort semantics, cap limits, reject malformed input, and fetch one extra row to detect continuation. Concurrent edits can still move rows between pages; document the consistency contract if users need a stable export.

Index real filter and sort paths. Partial indexes suit selective active or pending subsets; weigh update cost and production cardinality. Stored projections and materialized views need a freshness and repair strategy.

## Migration and release

A migration that has run on kept data, or is released, deployed, or of unknown status, is immutable (B9); use the existing deployment owner. Review table rewrites, lock duration, default evaluation, constraint validation, index creation, and batch size. Some operations (concurrent index creation) cannot run in a transaction block.

Mixed application versions: expand compatible schema, deploy compatible readers and writers, backfill and verify, switch reads, retire old use, contract. Name the exit condition for compatibility code. A failed migration needs a recovery plan; a speculative down migration does not guarantee data recovery.

Validate on a disposable production-equivalent database with real runtime grants and policies. Refresh generated query and schema artifacts. Tests cover the invariant at commit and under competing writers, not merely that the SQL parses.
