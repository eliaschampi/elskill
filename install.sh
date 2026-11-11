#!/usr/bin/env bash
# Link el-* skills into Claude Code, Codex, and opencode. Links point to
# this checkout, so edits here update every installation.
#
#   ./install.sh             ~/.claude/skills (Claude Code and opencode) and ~/.codex/skills
#   ./install.sh --opencode  also ~/.config/opencode/skills
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
			echo "skipped: $link exists and is not a symlink" >&2
			continue
		fi
		ln -sfn "$skill" "$link"
		echo "linked: $link → $skill"
	done
done
