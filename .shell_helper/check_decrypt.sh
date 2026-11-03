#!/usr/bin/env bash
set -euo pipefail

KEY_DIR="${1:?}"
SEARCH_DIR="${2:?}"

# The source-state attributes that apply to a directory, in the order chezmoi
# parses them. See https://chezmoi.io/reference/source-state-attributes/
DIR_ATTRS="remove_ external_ exact_ private_ readonly_ dot_"

# The source-state attributes that apply to a regular file, in the order
# chezmoi parses them. The script only ever sees files whose name starts with
# "encrypted_", so the create/modify/script/symlink orders cannot apply.
FILE_ATTRS="encrypted_ private_ readonly_ empty_ executable_ dot_"

# Strip the attributes from one path component and report the result in
# STRIPPED_NAME. Sets STRIPPED_DOT to 1 when the component gains a leading
# dot, which is what the "dot_" attribute means.
#
# "literal_" stops attribute parsing. It is checked at every step because it
# may appear anywhere in the name.
strip_attrs() {
	local name="$1" attrs="$2" attr
	STRIPPED_NAME=""
	STRIPPED_DOT=0
	for attr in $attrs; do
		case "$name" in
			literal_*)
				STRIPPED_NAME="${name#literal_}"
				return
				;;
			"$attr"*)
				name="${name#"$attr"}"
				[ "$attr" = dot_ ] && STRIPPED_DOT=1
				;;
		esac
	done
	STRIPPED_NAME="$name"
}

# Map a source-relative path to the target path chezmoi would use.
source_to_target() {
	local encrypted_file="$1"
	local base_dir="$2"
	local rel_path="${encrypted_file#$base_dir/}"
	local dir filename target_dir target_name
	dir=$(dirname "$rel_path")
	filename=$(basename "$rel_path")

	# Every directory but the last becomes one target path component.
	local rest="$dir" comp
	target_dir=""
	while [ "$rest" != "." ] && [ -n "$rest" ]; do
		comp="${rest%%/*}"
		if [ "$comp" = "$rest" ]; then
			rest=""
		else
			rest="${rest#*/}"
		fi
		strip_attrs "$comp" "$DIR_ATTRS"
		[ "$STRIPPED_DOT" = 1 ] && comp=".$STRIPPED_NAME" || comp="$STRIPPED_NAME"
		target_dir="${target_dir:+$target_dir/}$comp"
	done

	strip_attrs "$filename" "$FILE_ATTRS"
	target_name="$STRIPPED_NAME"
	[ "$STRIPPED_DOT" = 1 ] && target_name=".$target_name"

	# Suffixes, outermost first: the encryption suffix, then the template
	# suffix, then the literal suffix. The repository encrypts with age, so
	# ".age" is the encryption suffix to strip.
	case "$target_name" in
		*.age) target_name="${target_name%.age}" ;;
	esac
	case "$target_name" in
		*.tmpl) target_name="${target_name%.tmpl}" ;;
	esac
	case "$target_name" in
		*.literal) target_name="${target_name%.literal}" ;;
	esac

	if [ -z "$target_dir" ]; then
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

# Prune dot-directories. chezmoi itself ignores every dot-dir at the source
# root except .chezmoi*, so a file inside one can never become a target and
# never needs an ignore pattern. Without the prune the walk descends into
# .tmp (146k files) and .git on every chezmoi command.
# -mindepth 1 keeps the start point itself from being pruned.
find_encrypted() {
	find "$SEARCH_DIR" -mindepth 1 -type d -name '.*' ! -name '.chezmoi*' -prune \
		-o -name 'encrypted_*' -type f -print0 2>/dev/null
}

if [ ${#secret_keys[@]} -eq 0 ]; then
	find_encrypted | while IFS= read -r -d '' encrypted_file; do
		source_to_target "$encrypted_file" "$SEARCH_DIR"
	done
	exit 0
fi
shopt -u nullglob

identity_args=()
for key in "${secret_keys[@]}"; do
	identity_args+=(-i "$key")
done

find_encrypted | while IFS= read -r -d '' encrypted_file; do
	if ! age --decrypt "${identity_args[@]}" "$encrypted_file" >/dev/null 2>&1; then
		source_to_target "$encrypted_file" "$SEARCH_DIR"
	fi
done
