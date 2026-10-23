# Testpoint: /generation/content without id

Validation probe: 'GET /generation/content' without '?id=' returns **400** with the same Zod envelope as '/generation'. Always pass '?id=<gen-...>'.

Expected status: '400'.
Expected body shape: 'object{keys=2,success,error}'.
Required keys: 'success,error'.
Last verified: 2026-08-25.
