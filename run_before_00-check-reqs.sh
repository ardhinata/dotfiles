#!/bin/bash
# This script will check dependency for restoring complete configuration

# Color constant
TBOLD=$(tput bold)
TRED=$(tput setaf 1)
TYELLOW=$(tput setaf 3)
TRESET=$(tput sgr0)

# Newline padding flag
NEED_NEWLINE=0

if [[ -z $(which age 2>/dev/null) ]]; then
    echo "${TBOLD}${TYELLOW}No age executable found in \$PATH. Chezmoi will use internal age implementation${TRESET}" >&2
    NEED_NEWLINE=1
fi

if [[ -z $(which age-keygen 2>/dev/null) ]]; then
    echo "${TBOLD}${TRED}age-keygen isn't found in \$PATH. Recipient auto-population will be disabled.${TRESET}" >&2
    NEED_NEWLINE=1
fi;

if [[ -z "${FETCH_ATTACHMENT}" ]]; then
    echo "${TYELLOW}Bitwarden attachment download is disabled by default. Pass 'FETCH_ATTACHMENT=1' environment variable to enable bitwarden attachment download.${TRESET}" >&2
else
    if [[ -z "${BW_SESSION}" ]]; then
        echo "${TBOLD}${TRED}Environment variable BW_SESSION is not set, attachment will not be restored. Check .chezmoiignore for list of attachments.${TRESET}" >&2
        NEED_NEWLINE=1
    fi
fi

if [[ $NEED_NEWLINE -gt 0 ]]; then
    echo ""
fi
