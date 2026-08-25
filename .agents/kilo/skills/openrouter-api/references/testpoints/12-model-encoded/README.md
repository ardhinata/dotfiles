# Testpoint: /model/{a}/{s} with %2F

Path-encoding probe: '%2F' between author and slug returns 404. The slash must stay **unencoded**.

Expected status: '404'.
Expected body shape: 'object{keys=1,error}'.
Required keys: 'error'.
Last verified: 2026-08-25.
