# Plugin load

# Prezto
zplug "modules/environment", from:prezto
zplug "modules/helper", from:prezto
zplug "modules/utility", from:prezto
zplug "modules/history", from:prezto
zplug "modules/rsync", from:prezto
zplug "modules/gpg", from:prezto
zplug "modules/completion", from:prezto

# External plugin
zplug "CupricReki/zsh-bw-completion"
zplug "pkulev/zsh-rustup-completion"
zplug "plugins/colored-man-pages", from:oh-my-zsh
zplug "lib/key-bindings", from:oh-my-zsh

# Load syntax highlighting on last plugin load
zplug "zsh-users/zsh-syntax-highlighting", defer:2

# Theme
zplug "spaceship-prompt/spaceship-prompt", use:spaceship.zsh, from:github, as:theme