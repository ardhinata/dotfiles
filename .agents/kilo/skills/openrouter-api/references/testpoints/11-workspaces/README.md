# Testpoint: /workspaces (negative)

Negative testpoint: CLI key returns 401 with 'error.{message,code}'. Workspace-scoped write/admin endpoints need a different key scope.

Expected status: '401'.
Expected body shape: 'object{keys=1,error}'.
Required keys: 'error'.
Last verified: 2026-08-25.
