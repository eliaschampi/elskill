#!/usr/bin/env bash
# Enlaza las skills el-* en Claude Code, Codex y opencode. Los enlaces apuntan a
# esta carpeta: editar aquí actualiza todas las herramientas.
#
#   ./install.sh             ~/.claude/skills (Claude Code y opencode) y ~/.codex/skills
#   ./install.sh --opencode  además ~/.config/opencode/skills
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
targets=("$HOME/.claude/skills" "${CODEX_HOME:-$HOME/.codex}/skills")

if [[ "${1:-}" == "--opencode" ]]; then
	targets+=("$HOME/.config/opencode/skills")
fi

for target in "${targets[@]}"; do
	mkdir -p "$target"
	for skill in "$here"/el-*/; do
		skill="${skill%/}"
		link="$target/$(basename "$skill")"
		if [[ -e "$link" && ! -L "$link" ]]; then
			echo "omitido: $link existe y no es un enlace" >&2
			continue
		fi
		ln -sfn "$skill" "$link"
		echo "enlazado: $link → $skill"
	done
done
