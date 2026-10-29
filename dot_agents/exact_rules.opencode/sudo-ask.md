# Sudo Needs Approval — OpenCode

OpenCode tools for the shared rule
`~/.agents/rules.personal.d/sudo-ask.md`.

- Ask for approval with the `question` tool. It adds a "Type your own answer"
  option by itself, so do not add a separate free-form option.
- Give sudo a terminal with the shell tool's pty mode —
  `shell({ pty: true })`. A tool shell without a pty has no tty, so
  interactive sudo fails fast with "a terminal is required to read the
  password".
