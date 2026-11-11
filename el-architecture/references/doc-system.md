# Document ownership

Read when creating or reorganizing project documentation. Reuse equivalent files and create only what the task needs. The goal is discoverable decisions, not a mandatory document set.

| Information | Common owner | Keep out |
| --- | --- | --- |
| Agent workflow, commands, boundaries | `AGENTS.md` or equivalent | Duplicated product rules |
| Product intent, invariants, architecture | Existing specification or ADRs | Progress claims |
| Wire behavior and compatibility | API schema or contract documentation | A separately maintained type system |
| Verified status | Existing status record | Predictions presented as facts |
| Active outcome and remaining work | Existing task tracker or plan | Permanent rules copied from the specification |

If multiple agent tools need entry files, point them to the same owner through mechanisms those tools actually support. Do not maintain divergent copies.

## Useful record shapes

**Decision:** context → choice → reason → rejected alternative → revisit condition. Add owner and date when accountability matters.

**Constraint:** invariant or metric → enforcement command → workload/scope → execution stage → reason. A measured baseline is not an enforced gate until the command rejects violations. Exceptions need scope, rationale, responsible owner, and an expiry or removal condition.

**Task:** observable outcome → required slices → current status → unresolved decisions. A task is selected from the user's request; a backlog is not automatic permission to start unrelated work.

**Evidence:** date/revision → command or inspected artifact → observed result → limitations. Mark unavailable checks explicitly. Do not turn estimates into facts or preserve stale success after relevant code changes.

**Handoff:** accepted scope → changed paths and working-tree state → decisions → checks and outcomes → next unresolved step. Keep only the information needed to resume accurately.

## Maintain without duplication

- Link to the authoritative rule instead of restating it in every file.
- Update a contract, its consumers, and its documentation together when behavior changes.
- Remove superseded instructions while preserving valid constraints and their reasons.
- Keep entry documents short and route to conditional detail; avoid templates full of unused sections.
- A documentation cleanup must check callers and links just as a code refactor does.
