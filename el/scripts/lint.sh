#!/bin/sh
# el lint: maintainer guard for this skill. Run after any edit: sh scripts/lint.sh
# Checks frontmatter, token budget, link integrity, reference TOCs, and rule-ID coverage.
dir=$(cd "$(dirname "$0")/.." && pwd)
skill="$dir/SKILL.md"
fail=0
bad() { printf 'FAIL %s\n' "$1"; fail=1; }
ok()  { printf 'ok   %s\n' "$1"; }

[ -f "$skill" ] || { bad "SKILL.md missing"; exit 1; }
[ "$(head -n1 "$skill")" = "---" ] && ok "frontmatter opens on line 1" || bad "frontmatter must open on line 1"

fm=$(awk 'NR==1{next} /^---$/{exit} {print}' "$skill")
name=$(printf '%s\n' "$fm" | sed -n 's/^name:[[:space:]]*//p')
desc=$(printf '%s\n' "$fm" | sed -n 's/^description:[[:space:]]*//p')

[ "$name" = "$(basename "$dir")" ] && ok "name matches directory ($name)" || bad "name '$name' != directory '$(basename "$dir")'"
printf '%s' "$name" | grep -Eq '^[a-z0-9-]{1,64}$' && ok "name charset" || bad "name must be [a-z0-9-], max 64"
printf '%s' "$name" | grep -Eiq 'anthropic|claude' && bad "name contains a reserved word"
dl=${#desc}
[ "$dl" -gt 0 ] && [ "$dl" -le 1024 ] && ok "description $dl/1024 chars (portable cap)" || bad "description length $dl (need 1-1024)"
printf '%s' "$desc" | grep -q '[<>]' && bad "description contains angle brackets (render as &lt; &gt;)"
printf '%s' "$desc" | grep -Eiq '(^| )(I|you) ' && bad "description must be third person"

body_lines=$(wc -l < "$skill" | tr -d ' ')
[ "$body_lines" -lt 500 ] && ok "SKILL.md $body_lines lines (<500)" || bad "SKILL.md $body_lines lines (>=500)"

# links: every reference is routed from SKILL.md, every link resolves
for f in "$dir"/references/*.md; do
  b=$(basename "$f")
  grep -q "references/$b" "$skill" && ok "routed: $b" || bad "orphan reference (not linked from SKILL.md): $b"
  lines=$(wc -l < "$f" | tr -d ' ')
  [ "$lines" -gt 100 ] && ! grep -q '^## Contents' "$f" && bad "$b has $lines lines but no '## Contents'"
done
grep -o 'references/[A-Za-z0-9._-]*\.md' "$skill" | sort -u | while read -r l; do
  [ -f "$dir/$l" ] || { printf 'FAIL dead link: %s\n' "$l"; exit 1; }
done || fail=1
grep -ho '\](\([A-Za-z0-9._-]*\.md\))' "$dir"/references/*.md 2>/dev/null | tr -d '()]' | sort -u | while read -r l; do
  [ -f "$dir/references/$l" ] || { printf 'FAIL dead cross-link: %s\n' "$l"; exit 1; }
done || fail=1

# rule IDs: each defined exactly once across SKILL.md + references
chk() {
  p=$1; max=$2; n=1; missing=''
  while [ "$n" -le "$max" ]; do
    c=$(cat "$skill" "$dir"/references/*.md | grep -oE "\*\*$p$n\. " | wc -l | tr -d ' ')
    [ "$c" -eq 1 ] || missing="$missing $p$n(x$c)"
    n=$((n + 1))
  done
  [ -z "$missing" ] && ok "rules ${p}1-${p}${max} each defined once" || bad "rule IDs wrong:$missing"
}
chk A 25; chk B 47; chk D 49

# SKILL.md loads on every use and each reference on its route, so growth is a stated decision.
# Raise a budget only with a reason recorded in SOURCES.md (A17), never to make a new line fit.
# Count the complete file, rounding up at four bytes per estimated token.
printf '\ncontext budgets (estimated tokens)\n'
for f in "$skill" "$dir"/references/*.md; do
  name=$(basename "$f")
  limit=4000
  [ "$f" = "$skill" ] && limit=2000
  if bytes=$(wc -c < "$f"); then
    estimate=$(( (bytes + 3) / 4 ))
    if [ "$estimate" -le "$limit" ]; then
      ok "$name ~$estimate/$limit"
    else
      bad "$name exceeds its budget (~$estimate/$limit)"
    fi
  else
    bad "could not measure $name"
  fi
done
[ "$fail" -eq 0 ] && printf '\nPASS\n' || printf '\nFAILED\n'
exit "$fail"
