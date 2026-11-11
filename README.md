# elskill

Three coordinated skills for building web software with explicit ownership, reliable Rust backends, and usable interfaces. Instructions, examples, and metadata are in English. Product copy follows the application's own language requirements.

| Skill | Use it for | What it owns |
| --- | --- | --- |
| [el-architecture](el-architecture/SKILL.md) | Cross-layer implementation, architecture, refactoring, review | Execution contract, ownership, scope, evidence, completion |
| [el-backend](el-backend/SKILL.md) | Rust HTTP, SQL, authorization, migrations, workers | Integrity, atomicity, concurrency, contracts, bounded resources |
| [el-design](el-design/SKILL.md) | Screens, forms, interactions, responsive UI | Task clarity, state transitions, accessibility, visual verification |

Load architecture once for shared decisions, then the relevant domain skill. Each skill routes to focused references only when needed. Existing frameworks and design systems remain authoritative; Rust/axum/sqlx/PostgreSQL and Svelte/Lumi have dedicated guidance, not universal mandates.

## Install

```bash
./install.sh
./install.sh --opencode
```

The installer links the three skill folders into `~/.claude/skills` and `${CODEX_HOME:-~/.codex}/skills`. The optional flag also links `~/.config/opencode/skills`. Existing non-symlink entries are skipped. Links point here, so repository edits update the installed content. Keep this checkout available.

For project-local installation, place the three sibling skill folders in the project's supported skills directory. Keep them together: domain skills link to the architecture workflow. No external skill repository, paid model, or downloaded executable is required.

## Use

Select the relevant skill in your agent, or name it explicitly, for example:

```text
Use $el-architecture and $el-backend to fix duplicate payment submissions.
Trace the write path, preserve the existing contract, and demonstrate safe retries.
```

```text
Use $el-design to improve this order form within the existing design system.
Verify keyboard use, failed submission recovery, and the rendered mobile layout.
```

The workflow is **observe → define outcome and proof → change the owner → verify → review the diff**. Routine edits stay routine. Architecture rule IDs (`A1`–`A25`), backend IDs (`B1`–`B47`), and design IDs (`D1`–`D49`) remain stable for reviews; several formerly absolute rules now state their actual applicability.

## Maintain and evaluate

```bash
python3 scripts/check.py
bash -n install.sh
```

Structural checks validate the package, not a model's engineering judgment. Use the [behavioral scenarios](evals/scenarios.md) to evaluate decisions and observable outcomes. Compare baseline and skill-assisted runs on the same task and artifacts before claiming a quality gain; no model benchmark is claimed here.

Keep one owner per instruction. Add a rule only for a demonstrated decision or failure mode; place conditional detail in its reference. Preserve existing rule IDs and remove superseded guidance. Do not copy another product's versions, budgets, paths, locale, or approval workflow into general rules.

Research and adoption decisions are recorded in [SOURCES.md](SOURCES.md), including pinned revisions of all four requested repositories. The resulting guidance is an original synthesis, not a bundled copy of those skill packs.

## Model context

The requester identified “Claude Fable 5.2 Fable” and a $25 cost; no billing basis or capability benchmark was supplied. Model selection belongs to the host environment. These skills do not depend on that identifier, price, or a superiority claim: completion requires the same observable evidence from any model.
