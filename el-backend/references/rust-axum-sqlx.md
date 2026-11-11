# Rust, axum, and SQLx

Read for Rust backend work. Resolve versions and features from `rust-toolchain.toml`, manifests, and lockfiles. Inspect installed crate APIs or matching official documentation before using unfamiliar signatures. The guidance below describes responsibilities, not a scaffold to copy verbatim.

## Boundaries and types

- Keep pure domain calculations and policies independent of HTTP and database crates when the project already separates them. A small application does not automatically need more crates.
- Use validated newtypes for values with real invariants and enums for exclusive states. Keep fields private, expose validating constructors, and check overflow and conversions. Private fields alone do not make derived deserialization validate input.
- Route Serde input through `#[serde(try_from = "String")]` and a `TryFrom<String>` implementation that calls the parser, or an equivalent custom `Deserialize`. Do not derive unrestricted `Deserialize` for an invariant-bearing wrapper. Storage decoding and other conversions must preserve the same invariant; use infallible `From` only when validity is already guaranteed. Test invalid input through deserialization, not just the parser. [Serde conversion attributes](https://serde.rs/container-attrs.html)
- Distinguish domain models, persisted facts, and public representations where their responsibilities differ. Do not add DTO conversions that merely rename identical data.
- Accept dependencies at genuine I/O boundaries. A trait can earn its place through a current test, security, or substitution requirement; neither one implementation nor a mock automatically justifies it.
- Prefer borrowed inputs and owned values at task boundaries. Do not scatter `clone`, `Arc<Mutex<_>>`, or allocations merely to satisfy the compiler; identify the required ownership and lifetime first.
- Inherit workspace lint policy. Keep suppressions narrow and explained. Secrets should not derive ordinary `Debug` or `Serialize`; redacted wrappers must preserve that guarantee through nested types.

## HTTP extraction and transaction lifetime

Axum evaluates extractors in argument order; a body-consuming extractor must be last. A `FromRequestParts` extractor that opens a transaction therefore runs before a later `Json<T>` finishes reading the body. That can hold a connection while a slow client uploads. [Axum extraction](https://docs.rs/axum/latest/axum/extract/index.html)

Choose the existing project's verified approach:

1. Extract bounded metadata and identity without retaining a transaction; parse bounded JSON; then begin the business transaction, resolve current authorization facts, and mutate.
2. Use a deliberate composite `FromRequest` extractor that bounds/parses the body before acquiring the transaction and authorization context.

Do not reorder `Json` before a parts extractor and assume the handler will compile. Keep early authentication/rate limits, body limits, and body-read deadlines at the appropriate ingress layer. Authentication may use short database reads; it must not retain a business transaction during body reception.

Within the handler: enter context → stabilize facts → apply the policy → write → audit/outbox → commit → respond. Map extractor, query, and commit failures through the established error contract. A typed permission marker helps only if constructors and alternate routes cannot bypass it; route coverage and policy tests remain necessary.

## SQL and generated contracts

- Prefer SQLx checked macros when the repository uses them. Keep `.sqlx` metadata consistent with the target schema, features, and queries; regenerate through the project's command rather than editing metadata.
- Bind values. For dynamic filters or sorting, use supported query builders and allowlisted SQL structure; placeholders cannot bind identifiers.
- Execute atomic work through the transaction connection. A pool call inside that flow silently escapes atomicity and transaction-local tenant context.
- Return the intended public projection with `RETURNING` when possible. Check optional rows and affected counts according to the operation's semantics.
- Do not force nullable columns to non-null merely to silence inference. An override needs a query-level invariant and a relevant test.
- Preserve runtime wire semantics: decimal strings, timestamp offsets, optional versus null fields, enum encoding, and integer precision. Check generation drift with the repository's existing tooling.
- Represent known internal error codes with an enum and map HTTP status through an exhaustive `match`; generate or verify the client's exhaustive presentation map. Adding a known code must expose missing mappings during checks. At an independently versioned wire boundary, decode unknown codes into a safe fallback instead of crashing or revealing raw provider diagnostics.

An uncommitted SQLx transaction initiates rollback when dropped. This protects normal abandonment; it does not prove a disconnected client means a commit failed. Resolve ambiguous mutation outcomes through idempotency. [SQLx transactions](https://docs.rs/sqlx/latest/sqlx/struct.Transaction.html)

## Async, cancellation, and shutdown

- Avoid blocking or sustained CPU work on the async executor. Bound expensive work before scheduling it; a large blocking thread pool is not a concurrency budget.
- Acquire an owned semaphore permit before `spawn_blocking`, move it into the closure, and retain it until the computation finishes. Dropping the request or its join handle must not release capacity while the computation continues.
- Started `spawn_blocking` tasks cannot be aborted. A timeout stops waiting, not computation. Use cooperative cancellation or a supervised process when hard termination is required. [Tokio blocking tasks](https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html)
- Never hold a synchronous mutex guard across `.await`. Choose synchronization according to contention and I/O needs, not as a default wrapper around all state.
- Bound fan-out and channels. Track spawned work, propagate cancellation safely, and handle join failures; do not detach required work with unobserved `tokio::spawn`.
- On shutdown, stop accepting work, stop claiming jobs, allow bounded draining, and leave unfinished durable work recoverable. A shutdown deadline cannot terminate already running blocking tasks.
- Trace request/job identity, error category, durations, and relevant resource waits. Redact request bodies and secrets; keep metrics labels bounded.

## Verification

Use repository commands and production-equivalent database privileges. Candidate checks, only where configured:

```bash
cargo fmt --all -- --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
cargo sqlx prepare --workspace --check -- --all-targets
```

Check the real features and targets used in CI; do not force incompatible `--all-features`. Exercise rejection mapping, invalid input, commit failure, cancellation, and authorization wiring where changed. SQLx test databases must be disposable and separate from application data. Coordinate concurrent tests with barriers or observable lock state rather than assuming scheduling overlap.
