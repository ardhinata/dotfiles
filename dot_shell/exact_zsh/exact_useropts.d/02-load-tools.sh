# Make local tools git
if [[ -z "$LOCAL_TOOLS_GIT" ]]; then
    LOCAL_TOOLS_GIT="${HOME}/.shell"
fi

internal_pyenv_export() {
    PYENV_ROOT="$LOCAL_TOOLS_GIT/pyenv"
    export PYENV_ROOT
    export PATH="$PYENV_ROOT/bin:$PATH"
}

internal_pyenv_run() {
    eval "$(pyenv init --path)"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
}

internal_phpenv_export() {
    PHPENV_ROOT="$LOCAL_TOOLS_GIT/phpenv"
    export PHPENV_ROOT
    export PATH="$PHPENV_ROOT/bin:$PATH"
}

internal_phpenv_run() {
    eval "$(phpenv init -)"
}

internal_nvm_export() {
    NVM_ROOT="$LOCAL_TOOLS_GIT/nvm"
    export NVM_ROOT
}

internal_nvm_run() {
   source "$NVM_ROOT/nvm.sh"
   [ -s "$NVM_ROOT/bash_completion" ] && source "$NVM_ROOT/bash_completion"
   autoload -U add-zsh-hook
   add-zsh-hook chpwd internal_load_nvmrc
   internal_load_nvmrc
}


internal_load_nvmrc() {
  local -r node_version="$(nvm version)"
  local -r nvmrc_path="$(nvm_find_nvmrc)"

  if [ -n "$nvmrc_path" ]; then
    local -r nvmrc_node_version=$(nvm version "$(cat "${nvmrc_path}")")

    if [ "$nvmrc_node_version" = "N/A" ]; then
      nvm install
    elif [ "$nvmrc_node_version" != "$node_version" ]; then
      nvm use
    fi
  elif [ "$node_version" != "$(nvm version default)" ]; then
    echo "Reverting to nvm default version"
    nvm use default
  fi
}

if [[ -d "$HOME/.shell/flag" ]]; then
    if [[ -d "$LOCAL_TOOLS_GIT/pyenv/bin" && -f "$LOCAL_TOOLS_GIT/flag/pyenv" ]]; then 
        internal_pyenv_export
        internal_pyenv_run
    fi
    if [[ -d "$LOCAL_TOOLS_GIT/phpenv/bin" && -f "$LOCAL_TOOLS_GIT/flag/phpenv" ]]; then 
        internal_phpenv_export
        internal_phpenv_run
    fi
    if [[ -s "$LOCAL_TOOLS_GIT/nvm/nvm.sh" && -f "$LOCAL_TOOLS_GIT/flag/nvm" ]]; then
        internal_nvm_export
        internal_nvm_run
    fi
fi

# Manual load
u_enable_pyenv() {
    internal_pyenv_export
    internal_pyenv_run
}

u_enable_phpenv() {
    internal_phpenv_export
    internal_phpenv_run
}

u_enable_nvm() {
    internal_nvm_export
    internal_nvm_run
}
