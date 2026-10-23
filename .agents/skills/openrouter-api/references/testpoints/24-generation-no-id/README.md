# Testpoint: /generation without id

Validation probe: 'GET /generation' without '?id=' returns **400** with a Zod validation envelope ('{success:false, error:{name:"ZodError", ...}}'), not 404. Always pass '?id=<gen-...>'.

Expected status: '400'.
Expected body shape: 'object{keys=2,success,error}'.
Required keys: 'success,error'.
Last verified: 2026-08-25.
