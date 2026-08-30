# Testpoint: /activity (management)

Management-key probe: 'GET /activity' returns the daily inference log (one row per 'date, model, endpoint'). CLI key returns 403 ("Only management keys can fetch activity for an account"). Required by auth scope 'auth=mgmt'.

Expected status: '200'.
Expected body shape: 'object{keys=1,data}'.
Required keys: 'data'.
Last verified: 2026-08-25.
