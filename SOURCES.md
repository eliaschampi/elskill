# Research and adoption decisions

Reviewed on 2026-11-11. Repository revisions below pin the inspected source; they are evidence for design choices, not dependencies to load during ordinary skill use. License links record upstream terms. This repository uses independently written guidance and does not vendor upstream scripts or assets.

## Addy Osmani: explicit constraints and relevant evidence

Source: [agent-skills at 301b02b](https://github.com/addyosmani/agent-skills/tree/301b02b12bff98e4688e6984af6556802322bbde), [MIT license](https://github.com/addyosmani/agent-skills/blob/301b02b12bff98e4688e6984af6556802322bbde/LICENSE).

Inspected [constraint-driven development](https://github.com/addyosmani/agent-skills/blob/301b02b12bff98e4688e6984af6556802322bbde/skills/constraint-driven-development/SKILL.md), [source-driven development](https://github.com/addyosmani/agent-skills/blob/301b02b12bff98e4688e6984af6556802322bbde/skills/source-driven-development/SKILL.md), [context engineering](https://github.com/addyosmani/agent-skills/blob/301b02b12bff98e4688e6984af6556802322bbde/skills/context-engineering/SKILL.md), and [debugging](https://github.com/addyosmani/agent-skills/blob/301b02b12bff98e4688e6984af6556802322bbde/skills/debugging-and-error-recovery/SKILL.md).

**Adopt:** connect quality claims to commands; test gates with violations and controls; preserve the quality bar; verify unfamiliar version-sensitive APIs; retain restartable evidence; diagnose before retrying.

**Adapt:** keep constraints in the project's existing owner and scope checks to risk. Do not require a new constraints document, tool installation, interview, or citation on every ordinary line of code. Measured budgets replace copied thresholds.

**Owner:** [architecture](el-architecture/SKILL.md), especially A7, A14, A17, A24 and completion evidence.

## Dietrich Gebert: minimal complete changes

Source: [Ponytail skill at 96608e0](https://github.com/DietrichGebert/ponytail/blob/96608e078b2d5ea607c5c3b8b5a54d1c1fba6846/skills/ponytail/SKILL.md), [MIT license](https://github.com/DietrichGebert/ponytail/blob/96608e078b2d5ea607c5c3b8b5a54d1c1fba6846/LICENSE).

**Adopt:** inspect all affected consumers; reuse existing owners and platform capabilities before adding code; preserve validation, error recovery, security, and accessibility; finish the whole requested behavior.

**Adapt:** minimize unnecessary structure, not diff size. A safe compatibility migration, an explicit domain type, or a real resource boundary may require additional code. Do not introduce session modes or a permanent override of the user's chosen workflow.

**Owner:** [architecture](el-architecture/SKILL.md), A8–A13 and A18–A21.

## Matt Pocock: deep interfaces and behavioral feedback

Source: [skills at 4ae2317](https://github.com/mattpocock/skills/tree/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d), [MIT license](https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/LICENSE).

Inspected [codebase design](https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/codebase-design/SKILL.md) and [TDD](https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/tdd/SKILL.md).

**Adopt:** hide meaningful complexity behind small interfaces; examine what returns to callers if an abstraction disappears; test externally observable behavior with independent expected outcomes; learn through one working slice at a time.

**Adapt:** a second implementation is supporting evidence, not the only justification for an interface. Tests may inspect durable invariants when persistence is the contract. Do not require a user interview for every test boundary or tests for trivial wording edits.

**Owner:** [architecture](el-architecture/SKILL.md), A9–A10 and A21; [backend verification](el-backend/SKILL.md).

## Paul Bakaus: purpose-led design and rendered proof

Source: [Impeccable at c1e0e54](https://github.com/pbakaus/impeccable/tree/c1e0e5492fbb524f5df84d635ecfae7dc438ec45), [Apache-2.0 license](https://github.com/pbakaus/impeccable/blob/c1e0e5492fbb524f5df84d635ecfae7dc438ec45/LICENSE).

Inspected its [entry skill](https://github.com/pbakaus/impeccable/blob/c1e0e5492fbb524f5df84d635ecfae7dc438ec45/plugin/skills/impeccable/SKILL.md), [craft floor](https://github.com/pbakaus/impeccable/blob/c1e0e5492fbb524f5df84d635ecfae7dc438ec45/plugin/skills/impeccable/reference/craft-floor.md), and [hardening guidance](https://github.com/pbakaus/impeccable/blob/c1e0e5492fbb524f5df84d635ecfae7dc438ec45/plugin/skills/impeccable/reference/harden.md).

**Adopt:** choose composition by the user's purpose; distinguish refinement from redesign; honor the brief; inspect actual rendered work; test imperfect content, narrow layouts, interaction states, and recovery.

**Adapt:** preserve the installed design system and make visual ambition fit the surface. Do not copy aesthetic bans, fixed palettes, mandatory document sets, launcher downloads, or the upstream command framework.

**Owner:** [design](el-design/SKILL.md) and its conditional framework references.

## Chrome team: retrieve platform knowledge on demand

Source: [Modern Web Guidance at 4dd9683](https://github.com/GoogleChrome/modern-web-guidance/tree/4dd968349e54ca45a05dd5c818fb035c9054b022), [Apache-2.0 license](https://github.com/GoogleChrome/modern-web-guidance/blob/4dd968349e54ca45a05dd5c818fb035c9054b022/LICENSE). Inspected its README.

**Adopt:** search for a native platform capability before writing JavaScript or adding a dependency; keep specialized knowledge retrievable instead of always loaded; prune guidance that evaluations show a model no longer needs.

**Adapt:** elskill decides what must be solved and how it is proven; platform guides answer how the browser does it. The guide library is neither bundled nor required: the design skill points to it when installed and to MDN and Baseline otherwise.

**Owner:** [design](el-design/SKILL.md), entry routing.

## elskill synthesis

- **Execution contract:** outcome, owner, constraints, proof, and unresolved decisions make the next action explicit without a separate planning bureaucracy.
- **Conditional rigor:** replace blanket rules about transactions, traits, modals, rendering, versions, and locales with criteria tied to the actual invariant or task.
- **Cross-layer recovery:** backend idempotency and UI retry identity describe the same operation; stale responses, commit failures, and unknown external outcomes remain visible states.
- **Evidence over model reputation:** structural validation and behavioral scenarios distinguish package correctness from unmeasured model effectiveness.

These are local design decisions inspired by the sources above, not claims that this skill outperforms them. Rust, PostgreSQL, and UI references link official technical documentation where behavior requires verification.

## Conservation audit: original rules and public reuse

The follow-up audit compared the original `eae24e2` with `3435f92`, including conditional references rather than only numbered rules. The original supplied valuable working mechanisms, not merely material to shorten. Its one-owner principle, database-enforced invariants, complete flows, exact arithmetic, and machine-checked contracts remain the foundation.

| Finding in the first rewrite | Resolution and current owner |
| --- | --- |
| Private Rust fields were treated as enough to preserve validity | Restore parser-based deserialization and storage conversions in [Rust guidance](el-backend/references/rust-axum-sqlx.md) |
| Stable error strings replaced mechanically complete mappings | Restore a closed internal catalog and exhaustive known-code mappings, with a safe fallback for newer wire codes, in backend contracts and design D29 |
| New authentication and stored-secret protection became vague | Restore conditional password, session, cookie, expiry, CSRF, and vault/encryption defaults in [web security](el-backend/references/web-security.md) |
| Form dismissal lost its single decision point | Restore consistent handling across applicable close paths while keeping bounded recovery in [Svelte dialogs](el-design/references/svelte-patterns.md) |
| General UI guidance assumed every product had a server or an incumbent design system | Preserve local domain computation for offline tools and give new interfaces a concrete visual brief and representative-screen loop in [design](el-design/SKILL.md) |
| Visual checks named contrast and zoom without a measurable target | Add a sourced WCAG baseline and focused rendered checks; do not claim full conformance from a partial scan |
| The gate accepted malformed metadata and machine-local links | Parse YAML structurally and test positive and negative package fixtures |
| Installer arguments and conflicting symlinks could change unintended paths | Validate before mutation, preserve conflicts, and test a caller-selected installation directory |

Retained corrections include transactions per atomic operation, version-compatible migrations, true idempotency replay, real RLS privileges, and bounded blocking-task lifetimes. Restoring the old blanket rules would reintroduce defects. Project-specific paths, versions, locale, budgets, and mandatory Lumi/SPA choices remain conditional or removed.

The upstream ideas now have concrete checks: Addy's quality gates must reject invalid inputs and checker errors; Ponytail's minimal change preserves every affected consumer; Pocock's module interfaces include construction and serialization paths; Impeccable's visual intent is paired with rendered accessibility evidence. The installed instructions remain independent of those repositories and of any model identity or price.

The repository's MIT license covers its own material. Public packaging tests establish installation and metadata behavior; the model evaluation scenarios remain unexecuted specifications, not evidence of universal model quality.

## Proportion revision

A review of `8245a6f` judged the rules sound and found three gaps: the entry points applied the same weight to every task, the design guidance said more about what to avoid than what to build, and no behavior was measured. The response adds selection, not knowledge.

| Decision | Owner |
| --- | --- |
| Classify risk first: trivial work skips the contract; critical work adds a failing test and evidence under failure; every change ends with a proportion check | [Architecture](el-architecture/SKILL.md), "Scale the response to the risk" |
| Each domain skill names the rule groups a change touches, and a local change no longer loads architecture | [Backend](el-backend/SKILL.md) and [design](el-design/SKILL.md) entry points |
| Positive, judgeable visual starting points live in a conditional reference | [Visual craft](el-design/references/visual-craft.md) |
| Rules stay in the entry points: a one-line rule costs less than a retrieval round trip, and a reference nobody opens protects nothing | All three skills |
| No benchmark is claimed; the first three comparisons and their measurements are named | [Scenarios](evals/scenarios.md) |

Not adopted: mandatory brainstorming, plan documents, or subagents for ordinary work; session modes; a bundled guide library; aesthetic bans. Each adds ceremony or weight to the routine case this revision makes cheaper.
