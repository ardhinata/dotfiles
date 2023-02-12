export SHELLVARS="/run/user/$UID/shellvars"

# Make temporary directory to save sesson-related variable
if [[ ! -d $SHELLVARS ]]; then
    mkdir -p $SHELLVARS
fi

# WIP export
