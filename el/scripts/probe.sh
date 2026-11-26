#!/bin/sh
# el probe: read-only stack fingerprint (one call replaces several discovery calls).
# Never executes project code, never writes, always exits 0. Usage: probe.sh [dir]
LC_ALL=C; export LC_ALL
cd "${1:-.}" 2>/dev/null || { printf 'probe: cannot enter %s\n' "${1:-.}"; exit 0; }
# Never crawl a home or root directory (slow, and can trip macOS privacy prompts).
case "$(pwd -P)" in
  /|"$(cd "$HOME" 2>/dev/null && pwd -P)") printf 'probe: skipped, cwd is home or root; pass a project dir: probe.sh PATH\n'; exit 0 ;;
esac

PRUNE='-name node_modules -o -name target -o -name .git -o -name dist -o -name build -o -name .svelte-kit -o -name vendor -o -name .next -o -name .venv'
list=$(find . -maxdepth 3 \( $PRUNE \) -prune -o -type f \
  \( -name Cargo.toml -o -name package.json -o -name composer.json \) -print 2>/dev/null | sort | head -12)

# Concatenated manifests (size-capped) for dependency matching.
manifests=$(printf '%s\n' "$list" | while IFS= read -r f; do [ -n "$f" ] && head -c 100000 "$f" 2>/dev/null; done)
has() { printf '%s' "$manifests" | grep -Eq "$1"; }

printf '# el probe: %s\n' "$(basename "$(pwd)")"

# git state
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  br=$(git symbolic-ref --short -q HEAD 2>/dev/null || git rev-parse --short HEAD 2>/dev/null)
  n=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
  printf 'git: %s, %s changed path(s)\n' "$br" "$n"
fi

# project instructions and decision records
ins=''
for f in CLAUDE.md AGENTS.md CONTRIBUTING.md docs/adr; do [ -e "$f" ] && ins="$ins$f "; done
# Any-case spec name (docs/SPEC.md), listed once even on case-insensitive filesystems.
spec=$(find docs -maxdepth 1 -type f -iname spec.md 2>/dev/null | head -1)
[ -n "$spec" ] && ins="$ins$spec "
printf 'instructions: %s\n' "${ins:-none (A2: infer from precedent)}"

# manifests and stack tags
printf 'manifests: %s\n' "$(printf '%s' "$list" | tr '\n' ' ')"
[ -n "$(printf '%s\n' "$list" | grep Cargo.toml)" ] && printf 'rust: %s\n' "$(for p in axum sqlx tokio serde utoipa ts-rs specta diesel sea-orm tower; do has "^[[:space:]]*$p[[:space:]]*=|\"$p\"" && printf '%s ' "$p"; done)"
if [ -n "$(printf '%s\n' "$list" | grep package.json)" ]; then
  printf 'node: %s\n' "$(for p in @sveltejs/kit svelte react next vue nuxt astro solid-js kysely drizzle-orm prisma tailwindcss @renui/svelte @lumi-ui/svelte typescript vitest playwright eslint biome; do has "\"$p\"" && printf '%s ' "$p"; done)"
fi
[ -n "$(printf '%s\n' "$list" | grep composer.json)" ] && printf 'php: %s\n' "$(for p in laravel/framework inertiajs; do has "$p" && printf '%s ' "$p"; done)"
[ -f rust-toolchain.toml ] && printf 'toolchain: rust-toolchain.toml\n'

# data and contract owners
mig=$(find . -maxdepth 3 \( $PRUNE \) -prune -o -type d \( -name migrations -o -name migrate \) -print 2>/dev/null | head -3)
for d in $mig; do printf 'migrations: %s (%s files)\n' "$d" "$(find "$d" -maxdepth 2 -type f 2>/dev/null | wc -l | tr -d ' ')"; done
[ -d .sqlx ] && printf 'sqlx: .sqlx offline metadata present (regenerate, never hand-edit)\n'
ct=$(find . -maxdepth 3 \( $PRUNE \) -prune -o -type f \( -name 'openapi*.y*ml' -o -name 'openapi*.json' -o -name '*.proto' -o -name 'schema.graphql' \) -print 2>/dev/null | head -3 | tr '\n' ' ')
[ -n "$ct" ] && printf 'contract: %s\n' "$ct"

# check commands (names only; read, never run)
for f in $(printf '%s\n' "$list" | grep package.json | head -3); do
  s=$(awk '/"scripts"[[:space:]]*:[[:space:]]*\{/{f=1;next} f&&/\}/{exit} f&&match($0,/"[^"]+"[[:space:]]*:/){k=substr($0,RSTART+1,RLENGTH-1);sub(/".*/,"",k);printf "%s ",k}' "$f" 2>/dev/null | cut -c1-160)
  [ -n "$s" ] && printf 'scripts %s: %s\n' "$f" "$s"
done
[ -f Cargo.toml ] && printf 'cargo: fmt --check, clippy -D warnings, test%s\n' "$([ -d .sqlx ] && printf ', sqlx prepare --check')"
jf=''; for f in justfile Justfile; do [ -z "$jf" ] && [ -f "$f" ] && jf=$f; done  # macOS is case-insensitive
for f in $jf Makefile; do
  [ -f "$f" ] && printf '%s targets: %s\n' "$f" "$(grep -Eo '^[a-z][a-z0-9_-]*:' "$f" | tr -d ':' | head -12 | tr '\n' ' ')"
done
[ -d xtask ] && printf 'xtask: present (repo checks as code)\n'
[ -d .github/workflows ] && printf 'ci: %s\n' "$(ls .github/workflows 2>/dev/null | head -6 | tr '\n' ' ')"

# routing hint: references worth reading for this stack
r=''
add() { case " $r " in *" $1 "*) ;; *) r="$r $1" ;; esac; }
has 'axum|sqlx|tokio' && { add backend.md; add rust.md; }
has 'sqlx|kysely|drizzle|prisma' && add postgres.md
[ -n "$mig" ] && add postgres.md
has '"kysely"' && { add backend.md; add sveltekit-kysely.md; }
has 'laravel/framework' && { add backend.md; add laravel.md; }
has '"svelte"' && { add design.md; add svelte.md; }
has '"@renui/svelte"|"@lumi-ui/svelte"' && add renui.md
has '"@lumi-ui/svelte"' && printf 'renui: legacy @lumi-ui/svelte pinned; 2.0 migration in renui.md\n'
has '"react"|"next"|"vue"|"nuxt"|"astro"|"solid-js"|"tailwindcss"' && add design.md
printf 'read-if-touched:%s\n' "${r:- (stack not recognized; route by the table in SKILL.md)}"
exit 0
