# Laravel and PHP

Read for an existing Laravel application or PHP integration service. Resolve versions, model ownership, policies, middleware, database conventions, and checks from the project. Preserve its accepted framework boundaries.

## Laravel application

| Responsibility | Typical owner; verify locally |
| --- | --- |
| Authentication and session | Existing guard, account model, and middleware |
| Authorization and scope | Policy or established permission resolver |
| Input shape and normalization | FormRequest or established parser |
| Atomic use case | Focused Action or application service |
| Simple persistence | Existing Eloquent model/query path |
| HTTP or Inertia response | Controller and explicit resource projection |

Extend the actual owners. A trivial write does not require a new Action, repository, DTO package, or generic service. Conversely, retain existing modules that own real transactional or domain behavior. Do not hide required business effects in model observers or unobserved events.

- Authorize server actions independently of UI visibility. Centralize permission implications, tenant scope, branch context, and delegation rules; do not repeat role checks in controllers.
- Use the existing transaction owner for related writes, audit, and outbox records. Pass the intended connection throughout and do not call external services while holding database locks.
- Apply database constraints to persistent invariants; validation rules alone do not prevent concurrent duplicates. Translate structural database errors through the project's error contract.
- Use explicit writable fields and response projections. Guard against mass assignment and accidental exposure of password hashes, tokens, or administrative attributes.
- Bound list queries and eager loading. Eager-load required relationships to prevent N+1 work, but do not load entire histories for a summary.
- Queue dispatch after commit prevents premature execution but is not an atomic durable handoff by itself. Use an outbox when losing the required job between commit and dispatch would violate the business contract.
- Keep posted financial and audit facts traceable; follow domain-specific lifecycle rules rather than applying generic soft deletion everywhere.

## Stateless PHP integration

Keep durable business memory in its established owner. A signing or transport service may accept a strict request, produce or transmit an immutable artifact, and return a typed outcome without acquiring its own database or session system.

Use supported strict types and narrowly scoped dependencies. Parse input once; keep exact amounts and external codes lossless. Sensitive parameters and redacted logs reduce leakage but do not encrypt storage or guarantee memory erasure. Inspect the dependency's actual signature and transport behavior before changing integration code.

A retry sends the persisted artifact and provider idempotency identity. Timeout, unknown outcome, accepted, and rejected are distinct states; the business owner reconciles uncertainty. Do not infer success from transport completion alone.

## Verification

Use Composer/package scripts and the project's static analysis, formatting, tests, and frontend build. Confirm the actual database target before running destructive setup such as `migrate:fresh`; an environment label alone is not proof of isolation. Tests use disposable databases and fake external providers. Review changed contract fixtures and signed-artifact goldens as behavioral evidence rather than regenerating them blindly.
