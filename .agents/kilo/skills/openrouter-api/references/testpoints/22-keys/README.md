# Testpoint: /keys (management)

Management-key probe: 'GET /keys' returns the account's API key fleet under 'data[]'. CLI key returns 401 ("Invalid API key"). Required by auth scope 'auth=mgmt'.

Expected status: '200'.
Expected body shape: 'object{keys=1,data}'.
Required keys: 'data'.
Last verified: 2026-08-25.
