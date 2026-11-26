# Laravel and PHP

For an existing Laravel application or PHP integration service. Resolve versions, model ownership, policies, middleware, database conventions, and checks from the project; preserve its accepted framework boundaries.

## Laravel application

| Responsibility | Typical owner (verify locally) |
| --- | --- |
| Authentication, session | Existing guard, account model, middleware |
| Authorization, scope | Policy or established permission resolver |
| Input shape, normalization | FormRequest or established parser |
| Atomic use case | Focused Action or application service |
| Simple persistence | Existing Eloquent model and query path |
| HTTP or Inertia response | Controller with explicit resource projection |

Extend the real owners. A trivial write needs no new Action, repository, DTO package, or generic service; keep existing modules that own real transactional or domain behavior. Never hide required business effects in model observers or unobserved events.

- Authorize server actions independently of UI visibility. Centralize permission implications, tenant scope, branch context, and delegation; no role checks repeated in controllers.
- Use the existing transaction owner for related writes, audit, and outbox records. Pass the intended connection throughout; no external calls while holding database locks.
- Database constraints hold persistent invariants; validation rules alone do not prevent concurrent duplicates. Translate structural database errors through the project's error contract.
- Explicit writable fields and response projections. Guard mass assignment and accidental exposure of password hashes, tokens, or administrative attributes.
- Bound list queries and eager loading: eager-load required relations to prevent N+1, never whole histories for a summary.
- Dispatch-after-commit prevents premature execution but is not an atomic durable handoff. Use an outbox when losing the job between commit and dispatch would break the business contract.
- Keep posted financial and audit facts traceable; follow domain lifecycle rules rather than blanket soft deletion.

## Stateless PHP integration

Durable business memory stays with its established owner. A signing or transport service may take a strict request, produce or transmit an immutable artifact, and return a typed outcome without its own database or session system.

Use strict types and narrowly scoped dependencies. Parse input once; keep exact amounts and external codes lossless. Sensitive-parameter attributes and redacted logs reduce leakage but do not encrypt storage or guarantee memory erasure. Inspect the dependency's real signature and transport behavior before changing integration code.

A retry sends the persisted artifact and the provider idempotency identity. Timeout, unknown outcome, accepted, and rejected are distinct states; the business owner reconciles uncertainty. Never infer success from transport completion alone.

## Verification

Use Composer and package scripts, the project's static analysis, formatting, tests, and frontend build. Confirm the real database target before destructive setup such as `migrate:fresh`; an environment label is not proof of isolation. Tests use disposable databases and fake providers. Review changed contract fixtures and signed-artifact goldens as behavioral evidence; never regenerate them blindly.
