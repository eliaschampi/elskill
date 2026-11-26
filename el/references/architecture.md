# Architecture rules

Rules A4-A5, A8-A16, A20, A22-A25. The core rules (A1-A3, A6-A7, A17-A19, A21) live in SKILL.md.

## Contents
- Ownership map
- Structure rules
- Slice and handoff
- Decide, bound, measure
- Review protocol
- Gates

## Ownership map

| Responsibility | Owner | Boundary |
| --- | --- | --- |
| Referential integrity, uniqueness, row predicates | Database constraints | Friendly prechecks cannot replace concurrent enforcement |
| Pure calculations, domain transitions | Domain functions, validated types | No HTTP, UI, or storage dependency; client-only tools may own local computation |
| Authorization | Server policy over authoritative facts | UI capabilities describe access; every mutation rechecks |
| Input syntax and bounds | Trust-boundary parser | Storage-dependent facts stay transactional |
| Use-case orchestration | Existing handler, action, or application service | Owns atomicity and effects; no pass-through layers |
| Wire representation | Existing schema or contract | Generate or verify consumers; expose only intended fields |
| Derived data | Query, view, or reactive derivation | Persist projections only with a need and a consistency strategy |
| Tenancy, secrets, transactions, limits | Shared infrastructure boundary | Prevent bypass with types, privileges, or checks |
| Presentation and interaction | Existing design system and UI | Authorization and server-backed invariants stay on the server |

## Structure rules

- **A4. Match the repository.** File names and folder layouts are conventions, not prerequisites. New app or reorganized docs/folders: read structure.md.
- **A8. Organize by cohesive responsibility.** Extend the existing owner first. Split when independent responsibilities or change patterns justify it, not to satisfy a file-length number.
- **A9. Justify each abstraction.** What knowledge does it hide? If removed, where does the complexity return? Do its consumers share a reason to change? A second adapter supports an interface, and so can a present security, resource, or test boundary. A test double isolates real nondeterminism or I/O; it is not a reason to add a wrapper.
- **A10. Prefer deep modules.** A small interface hiding meaningful behavior, ordering, failure modes, and resource handling. Test through the interface callers use; keep implementation private. If the `codebase-design` skill is installed, use its vocabulary (module, interface, seam, depth).
- **A11. Least machinery that meets the contract.** Existing owner, then project primitive, then platform, then installed dependency, then focused new code. Reject speculative layers, mirrored DTOs, option bags, empty features, duplicate auth/state/UI/HTTP systems.
- **A12. Complete the cutover.** Update callers and remove replaced behavior together. Independently deployed clients or stored data may need a staged migration with an owner, an exit condition, and a removal check; an unsafe atomic rewrite is not simplicity. A fix replaces the wrong path; no flag or legacy mode keeps it selectable. A staged migration keeps its remaining exceptions in a list that a check allows only to shrink. For material refactors or migrations, compare observable results on the same inputs before and after; account for intended differences.
- **A13. One authoritative write path.** Required local effects share its transaction. Independent external effects need explicit delivery semantics and durable handoff; an in-process event is not durable delivery.
- **A14. Turn guarantees into checks.** Narrowest useful type, constraint, privilege, lint, contract check, or behavioral test. Cover every construction and bypass path (a private constructor does not protect a type whose deserializer skips it). Cover affected finite contract cases exhaustively when cheap. State what the check proves and what it cannot.
- **A15. Dependencies earn their cost.** Existing capability, compatibility, maintenance, security, runtime weight, license. Enable only needed features. Follow project approval rules; do not re-ask for authorized routine choices.
- **A16. Preserve the reason.** Document non-obvious invariants, tradeoffs, and constraints beside their owner. Code that implements an external specification or regulation links the clause it implements and uses its terms. A deliberate fast path, deviation, or known gap carries a searchable tag and its reason where it lives (`FIXME:`, `OPTIMIZATION:`). No comments that narrate code, no mandatory boilerplate headers.

## Slice and handoff

- **A5. One observable slice at a time.** At a handoff keep scope, decisions, changed paths, verification outcomes, and the next unresolved step. Re-check actual repository state on resume.
- **A20. Resolve necessary dependencies.** Implement adjacent behavior the flow requires and say why. Optional ideas go to the existing backlog, not the diff.

## Decide, bound, measure

- **A22. Record consequential decisions** in the existing decision owner: context, choice, rejected alternative, reason, revisit condition. Do not label every choice irreversible.
- **A23. Bound accepted risk.** Affected behavior, evidence, mitigation, owner or follow-up condition. A limitation must not silently invalidate acceptance.
- **A24. Measure the bottleneck.** Record workload, environment, metric, baseline, and command before claiming improvement. Derive budgets from needs or measured baselines (security and accessibility requirements apply without one). Label estimate, lab result, or production evidence.

## Review protocol

- **A25. Review behavior and structure.** No edits unless asked. Each actionable finding gives trigger, consequence, location, and rule ID. Inspect the full diff for missed consumers, duplicate owners, obsolete paths, weakened checks, and scope growth. Separate confirmed defects from questions. Cite the skill version with a rule ID; wording evolves.

## Gates

For a changed gate (lint, type, contract check, CI rule) demonstrate a rejected violation, an accepted control, and failure on checker errors; generating a report does not enforce a rule. Fast checks near edits, expensive checks at the task or CI boundary.
