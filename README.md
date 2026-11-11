# elskill — las skills de Elias

Tres skills que le dicen a cualquier agente (Claude Code, Codex, opencode) cómo se decide y se construye software en estos proyectos. Salen de las reglas que ya gobiernan `core-rs`, `lumi-ui`, `faztore`, `coedula`, `aeduca`, `fact` y `see-php`.

| Skill | Cuándo se carga | Qué fija |
| --- | --- | --- |
| [`el-architecture`](el-architecture/SKILL.md) | Antes de cualquier tarea de código; es la entrada | El dueño único de cada regla, las capas prohibidas, el protocolo de sesión, cuándo detenerse y qué es terminado |
| [`el-backend`](el-backend/SKILL.md) | Servidor, SQL, migraciones, workers, permisos | PostgreSQL dueño de los invariantes, una transacción por request, contrato y errores tipados, seguridad, rendimiento y pruebas |
| [`el-design`](el-design/SKILL.md) | Pantallas, formularios, diálogos, estilos, copy | Svelte 5 con Lumi, anatomía de página, estados obligatorios, ciclo de vida de diálogos, accesibilidad y peso |

Cada `SKILL.md` trae sus reglas numeradas (`A…`, `B…`, `D…`) y basta por sí solo para trabajar bien. Las `references/` añaden el detalle por stack y los fragmentos reales de core-rs; el agente lee sólo la que su tarea necesita.

## Instalar

```bash
./install.sh
```

Crea enlaces en `~/.claude/skills` (lo leen Claude Code y opencode) y en `~/.codex/skills`. Son enlaces a esta carpeta: editar aquí actualiza todas las herramientas. Con `./install.sh --opencode` enlaza además en `~/.config/opencode/skills`, por si desactivaste la compatibilidad de opencode con las skills de Claude.

Para un solo proyecto, enlaza o copia las carpetas `el-*` en su `.claude/skills/` o `.agents/skills/`.

Si quieres que Codex las use siempre, cambia la línea de `~/.codex/AGENTS.md` por:

```text
For code work in my projects, use the `el-architecture` skill first, then `el-backend` or `el-design` as the task requires. Where a project's AGENTS.md conflicts with them, the project's rules win.
```

`senior-code-quality` sigue sirviendo para código ajeno; en estos proyectos, las `el-*` la reemplazan.

## Usar

- Se cargan solas por su descripción. Para forzarlas: `$el-backend` en Codex, `/el-backend` en Claude Code, o nombrarlas en el pedido.
- En una revisión, pide los hallazgos citando la regla violada (`A11`, `B12`, `D6`).
- El `AGENTS.md` y el `docs/SPEC.md` de cada proyecto ganan siempre a estas skills.

## Mantener

- El bloque **Núcleo** es idéntico en los tres `SKILL.md`: si lo cambias, cámbialo en los tres.
- Una regla nueva entra cuando un proyecto la ganó de verdad, con su porqué, y en una sola skill.
- No renumeres las reglas existentes: los informes y las revisiones las citan. Las nuevas van al final de su sección.
- Mantén cada `SKILL.md` corto. El detalle de un stack va en `references/`.
