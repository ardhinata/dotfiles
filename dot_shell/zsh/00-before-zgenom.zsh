# ~/.shell/zsh/00-before-zgenom.zsh
# Runs before zgenom/Prezto initialization in ~/.zshrc.
# SHELL_TOOL_DIR is set in ~/.zshrc before this file is sourced.

# Register custom completions directory so Prezto's completion module
# discovers completions (e.g. _runpriv via #compdef) during compinit.
fpath=("${SHELL_TOOL_DIR}/zsh/completions" $fpath)
