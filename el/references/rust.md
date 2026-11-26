# Rust, axum, SQLx

Resolve versions and features from `rust-toolchain.toml`, manifests, and lockfiles (axum, SQLx, and tokio APIs change between minor lines; read the installed crate or matching docs before using an unfamiliar signature). This describes responsibilities, not a scaffold to copy.

## Contents
- Boundaries and types
- HTTP extraction and transaction lifetime
- SQL and generated contracts
- Async, cancellation, shutdown
- Verification

## Boundaries and types

- Keep pure domain calculations and policies independent of HTTP and database crates when the project already separates them. A small app does not automatically need more crates.
- Validated newtypes for values with real invariants; enums for exclusive states. Private fields, validating constructors, checked overflow and conversions. Private fields alone do not make derived deserialization validate.
- Route Serde input through `#[serde(try_from = "String")]` plus `TryFrom<String>` calling the parser, or a custom `Deserialize`. Never derive unrestricted `Deserialize` for an invariant-bearing wrapper. Storage decoding preserves the same invariant; use infallible `From` only when validity is already guaranteed. Test invalid input through deserialization, not just the parser. [Serde container attrs](https://serde.rs/container-attrs.html)
- Separate domain models, persisted facts, and public representations only where responsibilities differ; no DTO conversions that rename identical data.
- Accept dependencies at real I/O boundaries. A trait earns its place through a present test, security, or substitution need, not through one implementation or a mock.
- Borrowed inputs, owned values at task boundaries. Do not scatter `clone`, `Arc<Mutex<_>>`, or allocations to appease the compiler; identify ownership and lifetime first.
- Inherit workspace lints; keep suppressions narrow and explained. Secrets never derive ordinary `Debug` or `Serialize`; redacted wrappers must preserve that through nested types.

## HTTP extraction and transaction lifetime

axum runs extractors in argument order and a body-consuming extractor must be last. A `FromRequestParts` extractor that opens a transaction therefore runs before a later `Json<T>` finishes reading, holding a connection while a slow client uploads. [axum extractors](https://docs.rs/axum/latest/axum/extract/index.html)

Use the project's verified approach:

1. Extract bounded metadata and identity without keeping a transaction; parse bounded JSON; then begin the business transaction, resolve current authorization facts, mutate.
2. Or a deliberate composite `FromRequest` extractor that bounds and parses the body before acquiring the transaction and authorization context.

Do not move `Json` ahead of a parts extractor and assume it compiles to the right behavior. Keep early authentication and rate limits, body limits, and body-read deadlines at the ingress layer. Authentication may use short reads; it must not hold a business transaction during body reception.

Handler order: enter context, stabilize facts, apply policy, write, audit/outbox, commit, respond. Map extractor, query, and commit failures through the established error contract. A typed permission marker helps only if constructors and alternate routes cannot bypass it; keep route-coverage and policy tests.

## SQL and generated contracts

- Prefer SQLx checked macros where the repo uses them. Keep `.sqlx` metadata consistent with schema, features, and queries; regenerate with the project's command, never hand-edit.
- Bind values. Dynamic filters and sorting use supported builders and allowlisted structure; placeholders cannot bind identifiers.
- Run atomic work through the transaction connection. A pool call inside that flow silently escapes atomicity and transaction-local tenant context.
- Return the public projection with `RETURNING` where possible; check optional rows and affected counts by operation semantics.
- Do not force nullable columns to non-null to silence inference; an override needs a query-level invariant and a test.
- Preserve wire semantics: decimal strings, timestamp offsets, optional vs null, enum encoding, integer precision. Check generation drift with existing tooling.
- Known internal error codes are an enum mapped to HTTP status by an exhaustive `match`; generate or verify the client's exhaustive presentation map so a new code fails checks. At an independently versioned wire boundary, decode unknown codes to a safe fallback rather than crashing or leaking provider diagnostics.

An uncommitted SQLx transaction rolls back on drop; that covers normal abandonment but a disconnected client does not prove a commit failed. Resolve ambiguous mutations through idempotency. [SQLx Transaction](https://docs.rs/sqlx/latest/sqlx/struct.Transaction.html)

## Async, cancellation, shutdown

- No blocking or sustained CPU work on the async executor. Bound expensive work before scheduling; a large blocking pool is not a concurrency budget.
- Acquire an owned semaphore permit before `spawn_blocking`, move it into the closure, hold it until the computation ends. Dropping the request or join handle must not release capacity while work continues.
- Started `spawn_blocking` tasks cannot be aborted; a timeout stops waiting, not computing. Use cooperative cancellation or a supervised process when hard termination is needed. [Tokio spawn_blocking](https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html)
- Never hold a synchronous mutex guard across `.await`. Pick synchronization by contention and I/O needs, not as a default wrapper.
- Bound fan-out and channels. Track spawned work, propagate cancellation, handle join failures; no detached required work via unobserved `tokio::spawn`.
- Shutdown: stop accepting work, stop claiming jobs, drain within a bound, leave unfinished durable work recoverable. A deadline cannot kill running blocking tasks.
- Trace request and job identity, error category, durations, resource waits. Redact bodies and secrets; keep metric labels bounded.

## Verification

Use repository commands and production-equivalent database privileges. Candidates, only where configured:

```bash
cargo fmt --all -- --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
cargo sqlx prepare --workspace --check -- --all-targets
```

Match the real features and targets used in CI; do not force `--all-features`. Exercise rejection mapping, invalid input, commit failure, cancellation, and authorization wiring where changed. SQLx test databases are disposable and separate from application data. Coordinate concurrent tests with barriers or observable lock state, not assumed scheduling overlap.
