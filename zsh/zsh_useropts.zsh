# export additional PATH
export PATH="$PATH:$HOME/.dotfiles:$HOME/.local/bin:$HOME/go/bin"
export NMON="-GDkmcn"

# Fix fishy color
# export user_color="green"

# Auto set language
export LANG="en_US.UTF-8"

# Set ZSH history limit
setopt INC_APPEND_HISTORY
setopt EXTENDED_HISTORY
unsetopt HIST_SAVE_BY_COPY
setopt HIST_FIND_NO_DUPS
export HISTFILESIZE=1000000000
export HISTSIZE=1000000000
export HISTTIMEFORMAT="[%F %T] "

alias idea-full="_JAVA_AWT_WM_NONREPARENTING=1 nohup idea &>/dev/null &"
alias idea-clean="rm -rfv ~/.IdeaIC20*/system/{index,caches}"
alias idea-kill='jps -lvm | grep "com.intellij.idea.Main" | cut -d " " -f 1 | xargs kill -SIGKILL'
alias idea-pid='jps -lvm | grep "com.intellij.idea.Main" | cut -d " " -f 1'
alias mirror-fastest='sudo reflector --verbose --save /etc/pacman.d/mirrorlist --sort rate --age 6 -p http -p https -c id -c sg -c tw -c jp'

_systemctl_unit_state() {
  typeset -gA _sys_unit_state
  _sys_unit_state=( $(__systemctl list-unit-files "$PREFIX*" | awk '{print $1, $2}') ) }
