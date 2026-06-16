#!/usr/bin/env bash
set -euo pipefail

KEY_DIR="${1:?}"
SEARCH_DIR="${2:?}"

strip_attrs() {
	sed 's/^encrypted_//; s/^private_//; s/^readonly_//; s/^empty_//; s/^executable_//; s/^dot_//; s/\.tmpl$//; s/\.age$//; s/\.asc$//'
}

source_to_target() {
	local encrypted_file="$1"
	local base_dir="$2"
	local rel_path="${encrypted_file#$base_dir/}"
	local dir filename
	dir=$(dirname "$rel_path")
	filename=$(basename "$rel_path")
	local target_dir
	target_dir=$(echo "$dir" | sed 's#^dot_#.#; s#/dot_#/.#g')
	local target_name
	target_name=$(echo "$filename" | strip_attrs)
	if [ "$target_dir" = "." ]; then
		echo "$target_name"
	else
		echo "$target_dir/$target_name"
	fi
}

if ! command -v age &>/dev/null; then
	echo "check_decrypt: age not found" >&2
	exit 1
fi

shopt -s nullglob
secret_keys=("$KEY_DIR"/*.secret.key)
if [ ${#secret_keys[@]} -eq 0 ]; then
	find "$SEARCH_DIR" -name 'encrypted_*' -type f -print0 2>/dev/null | while IFS= read -r -d '' encrypted_file; do
		source_to_target "$encrypted_file" "$SEARCH_DIR"
	done
	exit 0
fi
shopt -u nullglob

identity_args=()
for key in "${secret_keys[@]}"; do
	identity_args+=(-i "$key")
done

find "$SEARCH_DIR" -name 'encrypted_*' -type f -print0 2>/dev/null | while IFS= read -r -d '' encrypted_file; do
	if ! age --decrypt "${identity_args[@]}" "$encrypted_file" >/dev/null 2>&1; then
		source_to_target "$encrypted_file" "$SEARCH_DIR"
	fi
done
