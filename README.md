# Dotfile repository
This is my personal dotfile repository, managed by [dotbot](https://github.com/anishathalye/dotbot) and sensitive files encrypted by [transcrypt](https://github.com/elasticdog/transcrypt).

## How to applying the dotfile
Simply run the install script located in this repo:
```
$ ./dotfile-bot
```
It will install dependency configured in `install.conf.yaml` (in the `shell` section). Files that located in `./secret` will transparently encrypted by transcrypt, and it will not be symlinked if this directory isn't decrypted.

