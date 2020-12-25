#!/usr/bin/env bash
set -e
BASEDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../secret/" && pwd)"
COUNT=0
FILES=""
DIRS=""

while (( "$#" )); do
  case "$1" in
    -s|--shallow)
      SHALLOW="-maxdepth 1"
      shift
      ;;
    -*|--*=) # unsupported flags
      echo "Error: Unsupported flag $1" >&2
      exit 1
      ;;
    *) # preserve positional arguments
      DIRS[$COUNT]=$1
      COUNT=$((COUNT + 1))
      shift
      ;;
  esac
done

COUNT=0

for i in $(seq 0 $((${#DIRS[@]} - 1))); do
    target=${DIRS[i]}
    echo -n "Scanning symlink in $target" >&2
    if [[ -n $SHALLOW ]]; then
        echo " with shallow mode." >&2
    else
        echo ""
    fi
    for j in $(find $target $SHALLOW -type l -print); do 
        FILES[$COUNT]=$j
        COUNT=$((COUNT + 1))
    done;
done

COUNT=0

for i in $(seq 0 $((${#FILES[@]} - 1))); do
    FOUND=$([[ -n ${FILES[i]} ]] && readlink ${FILES[i]} | grep $BASEDIR) || true
    if [[ -n $FOUND ]]; then
        rm -v ${FILES[i]} >&2
        COUNT=$((COUNT + 1))
    fi
done

echo "Deleted $COUNT from ${#FILES[@]} found symlink(s)."