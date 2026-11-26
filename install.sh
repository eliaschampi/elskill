#!/usr/bin/env bash
# Link the skill from this checkout; preserve existing installations.
set -euo pipefail

usage() {
	printf '%s\n' 'Usage: ./install.sh [--opencode] [--gemini] | --target DIRECTORY | --help' \
		'With no arguments, install into Claude Code and Codex skill directories.' \
		'--opencode also installs into ${XDG_CONFIG_HOME:-~/.config}/opencode/skills.' \
		'--gemini also installs into ~/.gemini/skills.' \
		'--target installs only into the supplied directory.'
}

targets=("$HOME/.claude/skills" "${CODEX_HOME:-$HOME/.codex}/skills")
case "${1:-}" in
	--help)
		if [[ $# -ne 1 ]]; then usage >&2; exit 2; fi
		usage; exit 0 ;;
	--target)
		if [[ $# -ne 2 || -z "$2" || "$2" == -* ]]; then usage >&2; exit 2; fi
		targets=("$2") ;;
	*)
		for argument in "$@"; do
			case "$argument" in
				--opencode) targets+=("${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills") ;;
				--gemini) targets+=("$HOME/.gemini/skills") ;;
				*) usage >&2; exit 2 ;;
			esac
		done ;;
esac

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
status=0
for target in "${targets[@]}"; do
	mkdir -p -- "$target"
	for skill in "$here"/el*/; do
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
