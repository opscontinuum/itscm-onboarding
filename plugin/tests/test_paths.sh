#!/usr/bin/env bash
# test_paths.sh — proves no skill points at a path that only exists before install.
#
# Four independent checks. Any one failing fails the suite:
#   1. Every SKILL.md carries a name and a description (static).
#   2. No SKILL.md names a path inside this plugin (static tripwire).
#   3. Every skill a SKILL.md refers to by name exists.
#   4. No two skills claim the same name.
#
# Check 2 is the one that matters over time, and it exists because of a bug that
# reached main. A tool's working directory is the user's project, never the
# directory this plugin was installed into, so a skill that said
# `skills/_method/coverage-map.md` sent the model looking inside the customer's
# own repository, where no such file exists. Eleven references were broken that
# way. Naming the absolute path instead is worse, not better: a deployment with
# confine_to_project set refuses an absolute path into a plugin directory
# outright, and that flag is the user's to set, not ours.
#
# The convention every shipped picoagent plugin follows is the fix: a skill
# refers to registered TOOL names and sibling SKILL names, never to a bundled
# file. This test fails CI if a bundled path comes back.

set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
PLUGIN_DIR="$PWD"
FAILS=0
pass() { printf '  ok    %s\n' "$1"; }
fail() { printf '  FAIL  %s\n' "$1"; FAILS=$((FAILS + 1)); }

mapfile -t SKILL_FILES < <(find skills -name SKILL.md | sort)
if [ "${#SKILL_FILES[@]}" -eq 0 ]; then
    printf 'FAIL - no SKILL.md found under %s/skills\n' "$PLUGIN_DIR"; exit 1
fi

# Directories that hold this plugin's own files. A path reference whose first
# segment is one of these, and which names something below it, is a bundled
# path: it resolves inside the plugin and nowhere else.
#
# `scripts` is deliberately on this list even though the *generated plan* also
# has a scripts/ directory for recovery automation. A bare `scripts/` is that
# one and is left alone; `scripts/discover/oci-discover.sh` is ours. The rule
# below is the discriminator: one segment is the plan's, two or more is ours.
BUNDLED_ROOTS='skills|scripts|templates|tests|plugin'

printf '\n1. every skill declares a name and a description\n'
BAD=0
for file in "${SKILL_FILES[@]}"; do
    head -n 1 "$file" | grep -q '^---$' || { printf '          %s: no frontmatter\n' "$file"; BAD=$((BAD + 1)); continue; }
    for field in name description; do
        if ! sed -n '2,/^---$/p' "$file" | grep -q "^$field:[[:space:]]*[^[:space:]]"; then
            printf '          %s: frontmatter has no %s\n' "$file" "$field"
            BAD=$((BAD + 1))
        fi
    done
done
if [ "$BAD" -eq 0 ]; then
    pass "${#SKILL_FILES[@]} skill(s) declare a name and a description"
else
    fail "$BAD frontmatter problem(s)"
fi

# The bundled scripts, by bare name. Naming one is the same mistake as naming
# its path: the model cannot run it, and the tool it should call is not
# mentioned. Derived from what is on disk, so a new script is covered for free.
BUNDLED_SCRIPTS="$(find scripts -type f -name '*.sh' -printf '%f\n' 2>/dev/null | paste -sd'|' -)"

printf '\n2. static tripwire: no skill names a path inside this plugin\n'
BROKEN=0
for file in "${SKILL_FILES[@]}"; do
    while IFS= read -r token; do
        [ -n "$token" ] || continue
        printf '          %s: %s\n' "$file" "$token"
        BROKEN=$((BROKEN + 1))
    done < <({ grep -oE "(^|[^A-Za-z0-9_./-])($BUNDLED_ROOTS)/[A-Za-z0-9_][A-Za-z0-9_./-]*" "$file"
               [ -n "$BUNDLED_SCRIPTS" ] && grep -oE "(^|[^A-Za-z0-9_./-])($BUNDLED_SCRIPTS)" "$file"
             } | sed -E "s#^[^A-Za-z0-9_]*##; s#[.,;:)]+\$##" \
               | sort -u)
done
if [ "$BROKEN" -eq 0 ]; then
    pass 'no bundled path references; skills name tools and sibling skills'
else
    fail "$BROKEN bundled path reference(s) that will not resolve after install"
    printf '          a tool runs in the user'"'"'s project, so these resolve there and fail.\n'
    printf '          refer to the registered tool or the sibling skill by name instead.\n'
fi

printf '\n3. every skill referred to by name exists\n'
KNOWN="$(sed -n 's/^name:[[:space:]]*//p' "${SKILL_FILES[@]}" | sort -u)"
MISSING=0
for file in "${SKILL_FILES[@]}"; do
    while IFS= read -r name; do
        [ -n "$name" ] || continue
        if ! printf '%s\n' "$KNOWN" | grep -qx "$name"; then
            printf '          %s: refers to unknown skill `%s`\n' "$file" "$name"
            MISSING=$((MISSING + 1))
        fi
    done < <(grep -oE '`itscp-[a-z0-9-]+`' "$file" | tr -d '`' | sort -u)
done
if [ "$MISSING" -eq 0 ]; then
    pass 'every `itscp-*` skill reference resolves'
else
    fail "$MISSING reference(s) to a skill that does not exist"
fi

printf '\n4. no two skills claim the same name\n'
# The registry is a dict keyed by name: a duplicate silently replaces the first,
# and the loaded skill count still looks right.
DUPES="$(sed -n 's/^name:[[:space:]]*//p' "${SKILL_FILES[@]}" | sort | uniq -d)"
if [ -z "$DUPES" ]; then
    pass "${#SKILL_FILES[@]} distinct skill name(s)"
else
    fail 'duplicate skill name(s):'
    printf '%s\n' "$DUPES" | sed 's/^/          /'
fi

printf '\n'
if [ "$FAILS" -eq 0 ]; then
    printf 'PASS - every skill reference survives installation\n'; exit 0
else
    printf 'FAIL - %s check(s) failed\n' "$FAILS"; exit 1
fi
