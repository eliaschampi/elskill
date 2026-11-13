# PostgreSQL integrity and concurrency

Read for schema, SQL, tenancy, migrations, or durable jobs. Preserve the project's naming and migration conventions. Verify version-specific features against the deployed database; do not import another project's role names, identifiers, page sizes, or deadlines.

## Choose the enforcing mechanism

| Invariant | Preferred mechanism | Important limit |
| --- | --- | --- |
| Required field or row predicate | `NOT NULL`, named `CHECK` | A check is not a cross-row query |
| Relationship or tenant ownership | Foreign key, often composite | Referenced keys need suitable uniqueness |
| Unique active record | Unique constraint or partial unique index | Application prechecks remain racy |
| Conditional state update | Predicate in `UPDATE`, inspect `RETURNING` | Zero rows needs a defined contract |
| Aggregate or cross-row condition | Shared guard lock or serializable transaction | Every conflicting writer must participate |
| Multi-row transfer valid only at commit | Deferred constraint trigger plus concurrency strategy | Deferral alone does not prevent write skew |

Put the rule and its concurrency rationale beside the schema owner. Map expected SQLSTATE and constraint names, never error text. A database invariant and client feedback can coexist without making feedback authoritative.

## Modern features (verify version)

Available from PostgreSQL 18. Confirm `SHOW server_version` and the managed provider's support, and do not assume features of later majors:

- `uuidv7()`: time-ordered UUIDs with better index locality than random v4 keys. Identity stays opaque (B2).
- `RETURNING OLD` and `NEW` on `INSERT`, `UPDATE`, `DELETE`, and `MERGE`: audit rows and optimistic checks without a second read.
- `WITHOUT OVERLAPS` and `PERIOD` temporal constraints: non-overlapping validity ranges enforced in the database instead of by application locks.
- Virtual generated columns (now the default kind): derived values computed at read time (B7); store them when they must be indexed.
- B-tree skip scan can remove the need for an extra index when the leading column has few distinct values; confirm with `EXPLAIN`.

## Tenant isolation

For RLS-based products, use tenant predicates and appropriate composite foreign keys alongside policies. Configure `USING` for visible rows and `WITH CHECK` for new row values. Enable RLS and use `FORCE ROW LEVEL SECURITY` when the owner must be subject to it.

The runtime role should not own tables, be a superuser, have `BYPASSRLS`, or inherit an escape path to elevated privileges. `FORCE` does not constrain superusers or `BYPASSRLS`. A `SET ROLE` from a privileged connection is not sufficient if application SQL can reset to that privileged role. Prefer direct runtime credentials with minimal grants. [PostgreSQL row security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)

Set tenant context transaction-locally, using parameterized `set_config(..., true)` or an equivalent established mechanism. Test missing context, wrong context, cross-tenant references, updates that change tenancy, and connection reuse after commit and rollback. RLS is a query isolation layer, not protection against an application that can arbitrarily select any tenant context.

Views, functions, background jobs, and reporting paths need explicit privilege analysis. Use supported invoker-security views when appropriate; never assume a view automatically preserves caller isolation. Restrict grants on immutable facts to the intended operations and mutable columns.

## Locking and isolation

Write down the invariant, rows or predicate involved, isolation level, and every competing operation before choosing locks.

- Prefer an atomic conditional write for a simple transition; it can avoid a separate read/decision race.
- At READ COMMITTED, a statement has a snapshot. Lock a stable shared guard row first, then read dependent facts in a subsequent statement so that a completed wait is followed by fresh committed facts.
- A lock on one row does not lock a predicate or related rows read through a join. Protect changes to memberships, roles, grants, and scope if authorization depends on them.
- At REPEATABLE READ, a later statement does not refresh the transaction snapshot. Do not apply a READ COMMITTED recipe without reconsidering isolation.
- Serializable isolation can reject a transaction; retry its entire decision and write sequence, not only the failed statement, and only when replay is safe.
- Take locks in a consistent order and configure bounded waits. A deadlock or timeout is not evidence that no prior external effect happened.

For “at least one owner remains,” locking the shared tenant or guard before relevant mutations gives concurrent writers a common serialization point. A deferred trigger can validate the final state, but must cover role changes, membership changes, deletion, and transfers that affect the set. An advisory lock helps only if all relevant paths acquire the same scoped lock and snapshot semantics are correct. Test the losing transaction and final durable state. [Transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html)

## Idempotency and counters

An idempotency record owns the operation scope, key, normalized request identity, and durable result. Compare semantic request content or its stable fingerprint; raw JSON byte order is not semantic identity.

1. Authorize the requested operation and tenant.
2. Serialize attempts through the existing aggregate lock, a scoped reservation, or another proven mechanism.
3. If a committed record exists, compare intent and replay its documented result; different intent conflicts.
4. Otherwise, apply the business effect and store the result atomically.
5. If uniqueness races, recover through a fresh transaction or appropriate savepoint before reading the winner. PostgreSQL does not allow ordinary queries in a failed transaction.

Define pending attempts, crash recovery, retention, and ambiguous response behavior. Replayed results still require current access checks. Concurrent identical requests must not create two effects; test retries after the original response is lost.

For business numbering, `UPDATE ... SET last_number = last_number + 1 ... RETURNING` within the document transaction can provide rollback-aware allocation. Ordinary sequences are cheaper and permit gaps. Choose according to the actual requirement and measured contention.

## Durable jobs and external outcomes

Enqueue in the transaction that establishes the business fact. Claim a bounded batch in a short transaction using a suitable lock strategy such as `FOR UPDATE SKIP LOCKED`; establish a fresh lease token and expiry, then commit before external I/O.

Every renewal, completion, and business-result write must verify the current token and an unexpired lease using database time. Once expired, the worker must reacquire through the claim protocol; it cannot resurrect ownership by updating a timestamp. A stale worker that loses the fence writes nothing.

Lease fencing protects database updates, not a provider already contacted. Use provider idempotency keys, immutable outbound artifacts, and reconciliation for ambiguous responses. The delivery contract is generally at least once; do not claim exactly once across unrelated systems. Bound attempts, backoff, job age, and operational recovery.

A privileged cross-tenant claim function should expose only the intended operation. Use a dedicated trusted schema and a safe fixed `search_path`; qualify referenced objects. Its owner and schema must not be writable by untrusted roles. Revoke default `PUBLIC` execution and grant the intended role in the same transaction that creates it. Avoid dynamic SQL and excessive returned data. [Security-definer functions](https://www.postgresql.org/docs/current/sql-createfunction.html)

## Query shape and pagination

Filter and page parent records before hydrating their details. Use batches, joins, or bounded aggregates rather than per-row round trips. Inspect representative plans; `EXPLAIN ANALYZE` executes the statement, so use a safe environment for writes or expensive queries.

Keyset pagination needs a deterministic order and unique tie-breaker. For descending order, match cursor comparisons to that direction; specify null handling and collation. Bind the cursor to filter/sort semantics, cap limits, and reject malformed input. Fetch one extra row to determine continuation when appropriate. Concurrent edits can still move records between pages; document the consistency contract if users need a stable export.

Index actual filter and sort paths. Use partial indexes for selective active/pending subsets, and assess update cost and production cardinality. Stored projections or materialized views require an explicit freshness and repair strategy.

## Migration and release

Use immutable applied migrations and the existing deployment owner. Review table rewrites, lock duration, default evaluation, constraint validation, index creation, and batch size before rollout. Some operations, such as concurrent index creation, cannot run inside an ordinary transaction block.

For mixed application versions: expand compatible schema → deploy compatible readers/writers → backfill and verify → switch reads → retire old use → contract. Name the exit condition for compatibility code. A failed migration needs a recovery plan; a speculative down migration is not a guarantee of data recovery.

Validate against a disposable production-equivalent database, including actual runtime grants and policies. Refresh generated query/schema artifacts. Tests must cover the invariant at commit and under competing writers, not merely confirm that migration SQL parses.
