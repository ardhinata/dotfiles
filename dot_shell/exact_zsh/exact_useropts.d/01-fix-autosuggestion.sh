# Enable completion for gnu-style programs (program that accept `--help` argument)
compdef _gnu_generic zstd

# Case-insensitive autosuggest
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Za-z}'
