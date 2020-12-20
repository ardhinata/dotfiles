##!/bin/sh
BASEDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

FLAG="$(grep "##DECRYPTED##" $BASEDIR/../secret/.status 2>/dev/null)"

if [[ -z $FLAG ]]; then
    exit 1
else
    exit 0
fi

