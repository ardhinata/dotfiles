#!/usr/bin/env bash
# Checks that check_decrypt.sh maps every encrypted source file to the target
# path chezmoi would use. A mismatch means the .chezmoiignore pattern misses
# the real target and `chezmoi apply` dies on the undecryptable file.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HELPER="$REPO_ROOT/.shell_helper/check_decrypt.sh"
SOURCE_DIR="${1:-$REPO_ROOT}"

command -v chezmoi >/dev/null 2>&1 || { echo "SKIP: chezmoi not found" >&2; exit 0; }
[ -d "$SOURCE_DIR" ] || { echo "SKIP: no source dir" >&2; exit 0; }

mapfile -t source_files < <(
	find "$SOURCE_DIR" -mindepth 1 -type d -name '.*' ! -name '.chezmoi*' -prune \
		-o -name 'encrypted_*' -type f -print
)

if [ ${#source_files[@]} -eq 0 ]; then
	echo "SKIP: no encrypted files under $SOURCE_DIR" >&2
	exit 0
fi

# The helper prints one target path per source file, in find order. Run it
# against the same tree and pair the two lists by position.
helper_targets=()
while IFS= read -r line; do
	helper_targets+=("$line")
done < <(bash "$HELPER" "$REPO_ROOT/.encryption_keys" "$SOURCE_DIR" 2>/dev/null)

if [ ${#helper_targets[@]} -ne ${#source_files[@]} ]; then
	printf 'FAIL: helper emitted %s targets for %s source files\n' \
		"${#helper_targets[@]}" "${#source_files[@]}" >&2
	exit 1
fi

failures=0
for i in "${!source_files[@]}"; do
	src="${source_files[$i]}"
	want=$(chezmoi target-path "$src" 2>/dev/null | sed "s#^$HOME/##")
	got="${helper_targets[$i]}"
	if [ "$want" != "$got" ]; then
		printf 'FAIL: %s\n  chezmoi: %s\n  helper:  %s\n' \
			"${src#$SOURCE_DIR/}" "$want" "$got" >&2
		failures=$((failures + 1))
	fi
done

if [ "$failures" -ne 0 ]; then
	printf 'FAIL: %s of %s mappings differ from chezmoi\n' "$failures" "${#source_files[@]}" >&2
	exit 1
fi

printf 'OK: %s encrypted files map to the chezmoi target path\n' "${#source_files[@]}"
