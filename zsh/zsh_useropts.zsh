# export additional PATH
export PATH="$PATH:$HOME/.dotfiles:$HOME/.local/bin:$HOME/.scripts:$HOME/go/bin"
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
export HISTFILESIZE=10000000000
export HISTSIZE=1000000000
export HISTTIMEFORMAT="[%F %T] "

# Use GUI pinentry for lastpass
export LPASS_PINENTRY=/usr/bin/pinentry-qt

alias idea-full="_JAVA_AWT_WM_NONREPARENTING=1 nohup idea &>/dev/null &"
alias idea-clean="rm -rfv ~/.IdeaIC20*/system/{index,caches}"
alias idea-kill='jps -lvm | grep "com.intellij.idea.Main" | cut -d " " -f 1 | xargs kill -SIGKILL'
alias idea-pid='jps -lvm | grep "com.intellij.idea.Main" | cut -d " " -f 1'
alias mirror-fastest='sudo reflector --verbose --save /etc/pacman.d/mirrorlist --sort rate --age 6 -p http -p https -c id -c sg -c tw -c jp'
alias work-firefox="nohup firefox -P work &>/dev/null &"
alias work-socks="ssh -TND 4711 -v 192.168.26.66"
alias work-route="sudo ip route add 192.168.72.0/24 dev tun7 metric 80; sudo ip route add default via 192.168.72.2 dev tun7 metric 81"
alias work-deroute="sudo ip route delete 192.168.72.0/24 dev tun7; sudo ip route delete default via 192.168.72.2 dev tun7"

# Functions
randpw(){ < /dev/urandom tr -dc "A-Za-z0-9" | tr -d "oOlI01" | head -c${1:-16};echo;LC_ALL=C printf "Password strength: %.3f\n" "$((5.80735*${1:-16}))" >&2}
coba() {
  [[ ! -d /tmp/coba ]] && mkdir /tmp/coba; cd /tmp/coba && code -n .;
}

_systemctl_unit_state() {
  typeset -gA _sys_unit_state
  _sys_unit_state=( $(__systemctl list-unit-files "$PREFIX*" | awk '{print $1, $2}') ) }
