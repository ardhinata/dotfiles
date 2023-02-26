# Export default editor
export EDITOR=vim

# Add local user executable to $PATH
export PATH="${PATH}:${HOME}/.local/bin"

# Export GPG SSH agent override
if [[ -n $(gpgconf --list-dirs agent-ssh-socket) && -S $(gpgconf --list-dirs agent-ssh-socket) ]]; then
    SSH_AUTH_SOCK=$(gpgconf --list-dirs agent-ssh-socket)
    export SSH_AUTH_SOCK
fi

# # Use user podman socket for docker compose if the flag `podman-user` is set
# if [[ -f $HOME/.shell/flag/podman-user ]]; then
#     export DOCKER_HOST=unix:///run/user/$UID/podman/podman.sock
# fi
