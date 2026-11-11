# elskill

Three coordinated skills for building web software with explicit ownership, reliable Rust backends, and usable interfaces. Instructions, examples, and metadata are in English. Product copy follows the application's own language requirements.

The governing principle is **one owner per rule, the smallest complete behavior, and evidence at the boundary that matters**. Concrete defaults help new projects start; explicit applicability keeps those defaults from overriding an existing product. Modern techniques earn their place through the problem they solve.

| Skill | Use it for | What it owns |
| --- | --- | --- |
| [el-architecture](el-architecture/SKILL.md) | Cross-layer implementation, architecture, refactoring, review | Risk classes, execution contract, ownership, scope, evidence, completion |
| [el-backend](el-backend/SKILL.md) | Rust HTTP, SQL, authorization, migrations, workers | Integrity, atomicity, concurrency, contracts, bounded resources |
| [el-design](el-design/SKILL.md) | Screens, forms, interactions, responsive UI | Task clarity, state transitions, visual craft, accessibility, rendered verification |

A local change needs only its domain skill; load architecture for cross-layer, structural, or critical work. Each skill names the rule groups a change touches and routes to focused references only when needed. Existing frameworks and design systems remain authoritative; Rust/axum/sqlx/PostgreSQL and Svelte/Lumi have dedicated guidance, not universal mandates.

## Install

```bash
./install.sh
./install.sh --opencode
./install.sh --target /path/to/project/.agents/skills
```

These are alternative installation commands. The default links the three skill folders into `~/.claude/skills` and `$CODEX_HOME/skills` (default: `~/.codex/skills`). `--opencode` also uses `$XDG_CONFIG_HOME/opencode/skills` (default: `~/.config/opencode/skills`). `--target DIR` installs only into the directory you choose. Conflicting files, directories, and links are preserved and reported as conflicts; identical links are left alone. Use `--help` for usage.

The installer requires Bash and standard Unix tools; links point to this checkout, which must remain available. On other platforms, copy the three skill folders together into the agent's supported skills directory. Domain skills link to the sibling architecture workflow. No external skill pack, paid model, or runtime dependency is required to use the instructions.

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

The workflow is **classify the risk → observe → define outcome and proof → change the owner → verify → check proportion**. A trivial edit skips the ceremony; a critical one earns a failing test first. Architecture rule IDs (`A1`–`A25`), backend IDs (`B1`–`B47`), and design IDs (`D1`–`D49`) remain available for reviews. Cite the repository revision with a rule ID: its wording and applicability can evolve.

## Maintain and evaluate

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/check.py
python3 -m unittest discover -s tests
bash -n install.sh
```

Use Python 3.10 or newer and a virtual environment for development dependencies. PyYAML parses metadata; it is not needed by agents consuming the skills. Regression tests exercise rejected metadata, portable links, and safe installation in temporary directories. CI runs the same checks.

These checks validate the package, not a model's engineering judgment. The [behavioral scenarios](evals/scenarios.md) are evaluation specifications, not an automated benchmark. Compare baseline and skill-assisted runs on the same task and artifacts before claiming a quality gain; no model benchmark is claimed here.

Contributions should explain the observed failure or decision, modify its existing owner, and include the relevant verification. Keep one owner per instruction and conditional detail in its reference. Preserve rule IDs, remove superseded guidance, and check the original rule's useful mechanisms before shortening it. Product settings belong to products; security and accessibility criteria come from their applicable standards.

Research and adoption decisions are recorded in [SOURCES.md](SOURCES.md), with the pinned revision of every inspected repository. The resulting guidance is an original synthesis, not a bundled copy of those skill packs.

## License

elskill is available under the [MIT license](LICENSE). Retain the license notice when redistributing it. Upstream references keep their own licenses, documented in [SOURCES.md](SOURCES.md); they are not bundled dependencies.
