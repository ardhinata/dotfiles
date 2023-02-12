# Export default editor
export EDITOR=vim

# Add local user executable to $PATH
export PATH="${PATH}:${HOME}/.local/bin"

# Export GPG SSH agent override
if [[ -n $(gpgconf --list-dirs agent-ssh-socket) && -S $(gpgconf --list-dirs agent-ssh-socket) ]]; then
    SSH_AUTH_SOCK=$(gpgconf --list-dirs agent-ssh-socket)
    export SSH_AUTH_SOCK
fi
