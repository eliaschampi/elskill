# elskill

Build, refactor, and debug modern web software with `$el`, an engineering skill for coding agents. It helps turn a product goal into a working feature, preserve behavior through a refactor, and verify that architecture, backend logic, and interface design work together.

EL starts with the risk of the change. A small edit gets the nearest relevant check. A change to payments, authorization, or stored data calls for a failing test first and evidence that the fix holds under the conditions that can break it. For a new product, EL starts with one working path that a user can exercise, then expands from there.

## Install

From the repository root, run the command for your setup.

```bash
./install.sh
./install.sh --opencode --gemini
./install.sh --target /path/to/project/.agents/skills
```

| Command | Destination |
| --- | --- |
| `./install.sh` | Claude Code in `~/.claude/skills` and Codex in `$CODEX_HOME/skills`, defaulting to `~/.codex/skills` |
| `./install.sh --opencode --gemini` | The default destinations plus OpenCode in `${XDG_CONFIG_HOME:-~/.config}/opencode/skills` and Gemini CLI in `~/.gemini/skills`. Either flag can be used on its own. |
| `./install.sh --target DIR` | Only the supplied skills directory. Use the path your agent reads. |

The Bash installer creates an `el` symlink to this checkout, reuses an existing correct link, and preserves conflicting entries. Keep the checkout in place while the link is in use. You can also copy the `el` directory into your agent's skills directory. The skill works without Python or a separate skill pack.

## Use

Select EL in your agent or invoke it by name. Give it the behavior you want and any constraints the implementation must preserve.

```text
Use $el to build the first working reservation flow. A customer should be able
to pick an available time, book it, and receive confirmation.
```

```text
Use $el to consolidate two report implementations. Compare their rows and totals
on the same fixtures, including empty periods, and preserve the export format.
```

[The skill entry point](el/SKILL.md) classifies the change and routes the agent to the relevant guidance. It uses the project's existing stack and design system. When project context is missing, the read-only probe can identify manifests, instruction files, and likely check commands.

```bash
sh el/scripts/probe.sh /path/to/project
```

| What you are working on | Guidance |
| --- | --- |
| New projects, module boundaries, dependencies, or documentation | [Project structure](el/references/structure.md) |
| Cross-layer changes, refactors, reviews, or performance claims | [Architecture](el/references/architecture.md) |
| APIs, domain logic, data, authorization, or workers | [Backend](el/references/backend.md) and relevant stack references |
| Interfaces, forms, accessibility, or visual direction | [Design](el/references/design.md), [visual direction](el/references/design-direction.md), and [web platform](el/references/web-platform.md) |
| Reports, dashboards, exports, or audit views | [Read models](el/references/read-models.md) |

For review findings, cite the relevant rule and repository revision. The rule groups are architecture (`A1`–`A25`), backend (`B1`–`B47`), and design (`D1`–`D49`).

## Verify the package

Use Python 3.10 or later and install the development dependency in a virtual environment.

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/check.py
python3 -m unittest discover -s tests -v
sh el/scripts/lint.sh
bash -n install.sh
```

These commands check metadata, relative links, reference routing, rule IDs, context budgets, and installer behavior. To measure how the skill affects an agent's work, compare runs on the same task and fixtures using the [behavioral evaluation scenarios](evals/scenarios.md).

## License

EL is released under the [MIT License](LICENSE). The [source notes](SOURCES.md) credit the material that informed the guidance and link to its licenses.
