#!/usr/bin/env bash
# Link the sibling skills from this checkout; preserve existing installations.
set -euo pipefail

usage() {
	printf '%s\n' 'Usage: ./install.sh [--opencode | --target DIRECTORY | --help]' \
		'With no arguments, install into Claude Code and Codex skill directories.' \
		'--opencode also installs into ${XDG_CONFIG_HOME:-~/.config}/opencode/skills.' \
		'--target installs only into the supplied directory.'
}

case "$#:${1:-}" in
	0:) targets=("$HOME/.claude/skills" "${CODEX_HOME:-$HOME/.codex}/skills") ;;
	1:--opencode)
		targets=("$HOME/.claude/skills" "${CODEX_HOME:-$HOME/.codex}/skills" \
			"${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills") ;;
	2:--target)
		if [[ -z "$2" || "$2" == -* ]]; then usage >&2; exit 2; fi
		targets=("$2") ;;
	1:--help) usage; exit 0 ;;
	*) usage >&2; exit 2 ;;
esac

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
status=0
for target in "${targets[@]}"; do
	mkdir -p -- "$target"
	for skill in "$here"/el-*/; do
		skill="${skill%/}"
		[[ -f "$skill/SKILL.md" ]] || continue
		link="$target/$(basename "$skill")"
		if [[ -L "$link" && "$link" -ef "$skill" ]]; then
			printf 'unchanged: %s\n' "$link"
		elif [[ -e "$link" || -L "$link" ]]; then
			printf 'conflict: preserved existing entry %s\n' "$link" >&2
			status=1
		elif ln -s -- "$skill" "$link"; then
			printf 'linked: %s -> %s\n' "$link" "$skill"
		else
			status=1
		fi
	done
done
exit "$status"
