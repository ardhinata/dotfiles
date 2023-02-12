# Generate random password
randpw() { 
  < /dev/urandom tr -dc "A-Za-z0-9" | tr -d "oOlI01" | head -c"${1:-16}";echo;echo -n "${1:-16}" | awk '{ printf "Estimated entropy: %.1f bit\n", 5.80735 * $1 }' >&2 
}
