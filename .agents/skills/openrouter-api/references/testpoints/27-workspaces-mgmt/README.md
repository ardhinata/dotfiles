# Testpoint: /workspaces (management, positive)

Management-key probe: 'GET /workspaces' returns the account's workspace list under 'data[]' plus 'total_count'. Companion to '11-workspaces' (CLI-key negative). Required by auth scope 'auth=mgmt'.

Expected status: '200'.
Expected body shape: 'object{keys=2}'.
Required keys: 'data,total_count'.
Last verified: 2026-08-25.
