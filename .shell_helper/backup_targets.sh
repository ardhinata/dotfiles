#!/usr/bin/env bash
# Backup the live targets that a chezmoi apply would change or delete.
#
# The backup is a copy of the CURRENT destination state, not the target
# state. It exists so an apply can be undone.
#
# Usage:
#   backup_targets.sh <backup-dir> [--extra <path> ...]
#   backup_targets.sh --restore <backup-dir>
#
# The backup dir receives:
#   manifest.tsv   status code, target path, live path
#   files/         a copy of each live target that is a file or a symlink
#   metadata.tsv   mode, owner, target path per copied path
#
# Directories are recorded as a mode change only. chezmoi lists a changed
# directory and its changed files as separate entries, so the files are
# copied individually. Copying the directory would pull in the whole tree,
# which is wrong for a target such as ~/Library.
#
# --extra adds a path that chezmoi does not manage but that the apply would
# disturb, such as a hand-written file inside a directory the apply changes
# the mode of. The path is relative to $HOME.
#
# Restore copies files/ back over the live paths and restores the modes.
# It does not delete files that the apply created. Remove those with
# `chezmoi destroy <target>`.
set -euo pipefail

BACKUP_DIR=""
MODE="backup"
EXTRA_PATHS=()

while [[ $# -gt 0 ]]; do
	case "$1" in
		--restore)
			MODE="restore"
			shift
			;;
		--extra)
			[[ $# -ge 2 ]] || { printf -- '--extra needs a path\n' >&2; exit 2; }
			EXTRA_PATHS+=("$2")
			shift 2
			;;
		-*)
			printf 'unknown option: %s\n' "$1" >&2
			exit 2
			;;
		*)
			[[ -z "${BACKUP_DIR}" ]] || { printf 'too many arguments\n' >&2; exit 2; }
			BACKUP_DIR="$1"
			shift
			;;
	esac
done

if [[ -z "${BACKUP_DIR}" ]]; then
	printf 'usage: %s <backup-dir> | %s --restore <backup-dir>\n' \
		"$0" "$0" >&2
	exit 2
fi

HOME_DIR="${HOME}"
# Set CHEZMOI_CONFIG to point at a config file when the default config
# cannot render the target state.
CHEZMOI_CONFIG="${CHEZMOI_CONFIG:-}"

# The permission bits of a path. BSD stat takes -f, GNU stat takes -c.
# Both print the same octal string, so the value feeds chmod unchanged.
if stat -f '%Lp' /dev/null >/dev/null 2>&1; then
	stat_mode() { stat -f '%Lp' "$1"; }
else
	stat_mode() { stat -c '%a' "$1"; }
fi

chezmoi_cmd() {
	if [[ -n "${CHEZMOI_CONFIG}" ]]; then
		chezmoi --config "${CHEZMOI_CONFIG}" "$@"
	else
		chezmoi "$@"
	fi
}

if [[ "${MODE}" == "backup" ]]; then
	if [[ -e "${BACKUP_DIR}" ]]; then
		printf 'backup dir exists: %s\n' "${BACKUP_DIR}" >&2
		exit 1
	fi
	mkdir -p "${BACKUP_DIR}/files"

	: >"${BACKUP_DIR}/manifest.tsv"
	: >"${BACKUP_DIR}/metadata.tsv"

	# Copy one live path into the backup and record it.
	record_path() {
		local target="$1" live kind dest
		live="${HOME_DIR}/${target}"

		if [[ -L "${live}" ]]; then
			kind="symlink"
		elif [[ -f "${live}" ]]; then
			kind="file"
		else
			# A directory. Record the mode; its files are listed
			# separately by chezmoi status.
			printf 'dir\t%s\t%s\n' \
				"$(stat_mode "${live}")" "${target}" \
				>>"${BACKUP_DIR}/metadata.tsv"
			return
		fi

		dest="${BACKUP_DIR}/files/${target}"
		mkdir -p "$(dirname "${dest}")"
		if [[ "${kind}" == "symlink" ]]; then
			ln -s "$(readlink "${live}")" "${dest}"
		else
			cp -p "${live}" "${dest}"
		fi

		printf '%s\t%s\t%s\n' "${kind}" \
			"$(stat_mode "${live}")" "${target}" \
			>>"${BACKUP_DIR}/metadata.tsv"
	}

	# chezmoi status prints one line per changed target: a status code
	# letter, then the target path relative to $HOME.
	while read -r code target; do
		[[ -z "${target}" ]] && continue
		live="${HOME_DIR}/${target}"
		printf '%s\t%s\t%s\n' "${code}" "${target}" "${live}" \
			>>"${BACKUP_DIR}/manifest.tsv"

		[[ -e "${live}" || -L "${live}" ]] || continue
		record_path "${target}"
	done < <(chezmoi_cmd status 2>/dev/null)

	# Extra paths that chezmoi does not manage but the apply would disturb.
	for target in "${EXTRA_PATHS[@]}"; do
		[[ -e "${HOME_DIR}/${target}" || -L "${HOME_DIR}/${target}" ]] || continue
		printf 'X\t%s\t%s\n' "${target}" "${HOME_DIR}/${target}" \
			>>"${BACKUP_DIR}/manifest.tsv"
		record_path "${target}"
	done

	printf 'backup written to %s\n' "${BACKUP_DIR}"
	printf 'targets in manifest: %s\n' \
		"$(wc -l <"${BACKUP_DIR}/manifest.tsv" | tr -d ' ')"
	printf 'paths recorded: %s\n' \
		"$(wc -l <"${BACKUP_DIR}/metadata.tsv" | tr -d ' ')"
	exit 0
fi

# Restore.
if [[ ! -d "${BACKUP_DIR}/files" ]]; then
	printf 'not a backup dir: %s\n' "${BACKUP_DIR}" >&2
	exit 1
fi

while IFS=$'\t' read -r kind mode target; do
	live="${HOME_DIR}/${target}"
	if [[ "${kind}" == "dir" ]]; then
		[[ -d "${live}" ]] && chmod "${mode}" "${live}"
		continue
	fi

	src="${BACKUP_DIR}/files/${target}"
	[[ -e "${src}" || -L "${src}" ]] || continue
	mkdir -p "$(dirname "${live}")"
	if [[ "${kind}" == "symlink" ]]; then
		rm -f "${live}"
		ln -s "$(readlink "${src}")" "${live}"
	else
		[[ -e "${live}" ]] && chmod u+w "${live}" 2>/dev/null || true
		cp -p "${src}" "${live}"
		chmod "${mode}" "${live}"
	fi
done <"${BACKUP_DIR}/metadata.tsv"

printf 'restored from %s\n' "${BACKUP_DIR}"
printf 'note: files the apply CREATED are still present.\n'
printf 'remove them with: chezmoi destroy <target>\n'
